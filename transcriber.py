"""
transcriber.py

Orquestrador de transcrição:
- Executa ASR via CORE selecionável (Whisper ou GPT-4o)
- Aplica refinadores determinísticos
- Mantém a transcrição como fonte primária imutável

Decisão técnica:
- ADR-001 — Qualidade da Transcrição
- Issue 4 — Configuração via TOML
"""

from pathlib import Path
import json
import tomli
import logging

# =========================================================
# Logging
# =========================================================
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

# =========================================================
# Core ASR
# =========================================================
from core.whisper_core import whisper_transcribe
from core.gpt4o_transcribe_core import gpt4o_transcribe

# =========================================================
# Refinadores
# =========================================================
from refiners.orality import normalize_orality
from refiners.repetition import remove_repetition
from refiners.hallucination import cut_hallucinated_tail

# =========================================================
# Cache de config
# =========================================================
_CONFIG_CACHE: dict | None = None


def load_config(config_path: Path | None = None) -> dict:
    """
    Carrega e mantém em cache a configuração TOML.

    - Se o arquivo não existir, retorna dict vazio
    - Defaults seguros são aplicados no código
    """
    global _CONFIG_CACHE

    if _CONFIG_CACHE is not None:
        return _CONFIG_CACHE

    config_path = config_path or Path("config/transcription.toml")
    if not config_path.exists():
        logger.warning("Arquivo TOML não encontrado. Usando defaults.")
        _CONFIG_CACHE = {}
        return _CONFIG_CACHE

    with config_path.open("rb") as f:
        _CONFIG_CACHE = tomli.load(f)

    logger.info("Configuração TOML carregada com sucesso.")
    return _CONFIG_CACHE


def transcribe_audio(
    audio_path: Path,
    session_type: str = "outro",
) -> dict:
    """
    Executa a transcrição de áudio e aplica refinadores.

    Retorno:
    {
        "text": str,
        "language": str,
        "session_type": str,
        "duration": float
    }
    """

    logger.info("Iniciando transcrição: %s", audio_path)

    cfg = load_config()
    tcfg = cfg.get("transcription", {})

    engine = tcfg.get("engine", "whisper")

    # -----------------------------------------------------
    # Validação de engine (Issue 4)
    # -----------------------------------------------------
    if engine not in ("whisper", "gpt4o"):
        logger.warning(
            "Engine inválido no TOML (%s). Usando default: whisper",
            engine
        )
        engine = "whisper"

    logger.info(
        "Configuração ativa | engine=%s | orality=%s | repetition=%s | hallucination=%s",
        engine,
        tcfg.get("orality", {}).get("enabled", False),
        tcfg.get("repetition", {}).get("enabled", False),
        tcfg.get("hallucination", {}).get("enabled", False),
    )

    # =====================================================
    # ASR
    # =====================================================
    if engine == "whisper":
        logger.info("Usando Whisper local (idioma automático).")
        result = whisper_transcribe(audio_path=audio_path)
    else:
        logger.info("Usando GPT-4o para transcrição.")
        result = gpt4o_transcribe(audio_path=audio_path)

    text = (result.get("text") or "").strip()

    # =====================================================
    # Refinadores (blindados)
    # =====================================================
    orality_cfg = tcfg.get("orality") or {}
    if orality_cfg.get("enabled") is True:
        logger.info("Aplicando refinador de oralidade.")
        text = normalize_orality(text, orality_cfg.get("terms", []))

    repetition_cfg = tcfg.get("repetition") or {}
    if repetition_cfg.get("enabled") is True:
        logger.info("Aplicando refinador de repetição.")
        text = remove_repetition(text, repetition_cfg.get("max_consecutive", 1))

    logger.info("Aplicando corte de alucinação (cauda).")
    text = cut_hallucinated_tail(text, tcfg.get("hallucination", {}))

    logger.info("Transcrição concluída (%d caracteres).", len(text))

    return {
        "text": text,
        "language": result.get("language", "auto"),
        "session_type": session_type,
        "duration": float(result.get("duration", 0.0) or 0.0),
    }


def save_transcription_bundle(result: dict, output_path: Path) -> None:
    """
    Salva:
    - texto da transcrição (.txt)
    - metadados (.meta.json)
    """
    output_path.write_text(result["text"], encoding="utf-8")

    meta = {
        "language": result["language"],
        "session_type": result["session_type"],
        "duration": result["duration"],
    }

    output_path.with_suffix(".meta.json").write_text(
        json.dumps(meta, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )

    logger.info("Arquivos de transcrição salvos em %s", output_path.parent)
