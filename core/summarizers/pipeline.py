from __future__ import annotations

import logging
import sys
from pathlib import Path
from typing import Callable, Dict, Any

import tomllib

PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from refiners.structural import refine_structural
from refiners.orality import normalize_orality
from refiners.repetition import remove_repetition
from refiners.lexical import refine_lexical
from refiners.hallucination import cut_hallucinated_tail

from summarizers.corporate_minutes import generate_corporate_minutes
from summarizers.ollama_summarizer import summarize_with_ollama

logger = logging.getLogger(__name__)

_PREAMBLE_MAP = {
    "daily": "preamble_daily.txt",
    "reuniao_interna": "preamble_reuniao_interna.txt",
    "reuniao_externa": "preamble_reuniao_externa.txt",
    "outro": "preamble_generico.txt",
    "kickoff": "preamble_kickoff.txt",
    "planejamento_sprint": "preamble_planejamento_sprint.txt",
    "retrospectiva": "preamble_retrospectiva.txt",
    "incidente_postmortem": "preamble_incidente_postmortem.txt",
    "one_on_one": "preamble_one_on_one.txt",
    "treinamento": "preamble_treinamento.txt",
}

_OUTPUT_MAP = {
    "daily": "resumo_daily.md",
    "reuniao_interna": "ata_reuniao_interna.md",
    "reuniao_externa": "ata_reuniao_externa.md",
    "outro": "ata_outro.md",
    "kickoff": "ata_kickoff.md",
    "planejamento_sprint": "ata_planejamento_sprint.md",
    "retrospectiva": "ata_retrospectiva.md",
    "incidente_postmortem": "postmortem_incidente.md",
    "one_on_one": "resumo_one_on_one.md",
    "treinamento": "resumo_treinamento.md",
}


def _load_config() -> Dict[str, Any]:
    config_path = PROJECT_ROOT / "config.toml"
    if not config_path.exists():
        return {}
    return tomllib.loads(config_path.read_text(encoding="utf-8"))


def _load_transcription(session_dir: Path) -> str:
    transcription_path = session_dir / "transcricao_completa.txt"
    if not transcription_path.exists():
        raise FileNotFoundError(f"Transcricao nao encontrada: {transcription_path}")
    return transcription_path.read_text(encoding="utf-8-sig")


def _load_preamble(meeting_type: str) -> str:
    preamble_name = _PREAMBLE_MAP.get(meeting_type)
    if not preamble_name:
        raise ValueError(f"Tipo de reuniao invalido: {meeting_type}")
    preamble_path = PROJECT_ROOT / "preambles" / preamble_name
    return preamble_path.read_text(encoding="utf-8")


def _apply_refiners(text: str, cfg: Dict[str, Any]) -> str:
    refined = refine_structural(text)

    orality_cfg = cfg.get("transcription", {}).get("orality", {})
    if orality_cfg.get("enabled", False):
        terms = orality_cfg.get("terms", [])
        refined = normalize_orality(refined, terms)

    repetition_cfg = cfg.get("transcription", {}).get("repetition", {})
    if repetition_cfg.get("enabled", False):
        max_consecutive = repetition_cfg.get("max_consecutive", 1)
        refined = remove_repetition(refined, max_consecutive=max_consecutive)

    refined = refine_lexical(refined)

    cleaning_cfg = cfg.get("transcription", {}).get("cleaning", {})
    refined = cut_hallucinated_tail(refined, cleaning_cfg)

    return refined


def _summarize_daily(
    refined_text: str,
    preamble_text: str,
    llm_callable: Callable[[str], str],
) -> str:
    if not refined_text or not refined_text.strip():
        raise ValueError("Transcricao refinada vazia para resumo daily.")

    prompt = (
        f"{preamble_text}\n\n"
        "Transcricao refinada:\n"
        "\"\"\"\n"
        f"{refined_text}\n"
        "\"\"\"\n\n"
        "Gere um resumo simples, objetivo e em Markdown."
    )
    result = llm_callable(prompt)
    if not result or not str(result).strip():
        raise RuntimeError("O LLM nao retornou conteudo valido.")
    return str(result).strip()


def run_summary_pipeline(
    session_dir: Path,
    meeting_type: str,
) -> Path:
    """
    Executa pipeline de resumo/ata com governanca.

    - Carrega transcricao consolidada
    - Aplica refinadores deterministas
    - Seleciona preambulo em memoria
    - Gera resumo ou ata via LLM
    - Persiste apenas o resultado final

    Exemplo (CLI):
        from pathlib import Path
        from core.summarizers.pipeline import run_summary_pipeline

        session_dir = Path("output/session_2026-02-03_13-07")
        output_path = run_summary_pipeline(session_dir, meeting_type="reuniao_interna")
        print(output_path)

    Exemplo (Streamlit):
        from pathlib import Path
        from core.summarizers.pipeline import run_summary_pipeline

        session_dir = Path(st.session_state["session_dir"])
        output_path = run_summary_pipeline(session_dir, meeting_type=st.session_state["meeting_type"])
        st.success(f"Resumo gerado: {output_path}")
    """

    meeting_type = meeting_type.strip().lower()
    if meeting_type not in _PREAMBLE_MAP:
        raise ValueError(f"Tipo de reuniao invalido: {meeting_type}")

    cfg = _load_config()
    transcription_text = _load_transcription(session_dir)
    refined_text = _apply_refiners(transcription_text, cfg)

    preamble_text = _load_preamble(meeting_type)

    if meeting_type == "daily":
        result = _summarize_daily(refined_text, preamble_text, summarize_with_ollama)
    else:
        result = generate_corporate_minutes(
            transcription_text=refined_text,
            preamble_text=preamble_text,
            context_label=meeting_type,
            llm_callable=summarize_with_ollama,
        )

    output_name = _OUTPUT_MAP[meeting_type]
    output_path = session_dir / output_name
    output_path.write_text(result, encoding="utf-8-sig")
    logger.info("Resumo/ata gerado em %s", output_path)
    return output_path
