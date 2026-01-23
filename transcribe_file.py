"""
transcribe_file.py

Orquestrador do pipeline de transcrição.

Responsabilidades:
- Executar ASR
- Aplicar refinadores de forma segura
- Garantir que texto válido nunca seja apagado
- Persistir resultado final
"""

# =========================
# Changelog
# =========================
#
# 2026-01-22
# - Correção definitiva do consumo de refinadores
# - Suporte explícito a retornos (str) e (str, dict)
# - Garantia absoluta de que texto válido nunca é zerado
#
# =========================

import argparse
import json
import time
from pathlib import Path
from typing import Any, Tuple

from core.whisper_core import whisper_transcribe
from refiners.orality import normalize_orality
from refiners.repetition import remove_repetition
from refiners.hallucination import cut_hallucinated_tail
from refiners.lexical import refine_lexical


def _extract_text(result: Any) -> str:
    """
    Extrai texto de um refinador.

    Aceita:
    - str
    - (str, dict)

    Qualquer outro tipo é ignorado.
    """
    if isinstance(result, str):
        return result

    if isinstance(result, tuple) and result:
        text = result[0]
        if isinstance(text, str):
            return text

    return ""


def _apply_refiner(current: str, result: Any) -> str:
    """
    Aplica o resultado de um refinador somente se:
    - for string
    - não estiver vazia

    Nunca permite apagar texto válido.
    """
    candidate = _extract_text(result)
    if candidate.strip():
        return candidate
    return current


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("-a", "--audio", required=True)
    parser.add_argument("-t", "--type", default="reuniao")
    parser.add_argument("-s", "--slug", default=None)
    args = parser.parse_args()

    audio_path = Path(args.audio)
    if not audio_path.exists():
        raise FileNotFoundError(audio_path)

    print("[PIPELINE] Iniciando transcrição")
    start = time.time()

    # ==================================================
    # ASR
    # ==================================================
    print("[PIPELINE] Etapa 1/3 — ASR")
    core_result = whisper_transcribe(
        audio_path=audio_path,
        language="pt",
        session_type=args.type,
    )

    text = core_result.get("text") or ""
    text = text.strip()

    # ==================================================
    # Refinadores
    # ==================================================
    print("[PIPELINE] Etapa 2/3 — Refinadores")

    if text:
        text = _apply_refiner(text, normalize_orality(text, terms=[]))
        text = _apply_refiner(text, remove_repetition(text))
        text = _apply_refiner(text, cut_hallucinated_tail(text, cfg={}))
        text = _apply_refiner(text, refine_lexical(text))

    # Blindagem final
    if not isinstance(text, str):
        text = ""

    # ==================================================
    # Persistência
    # ==================================================
    print("[PIPELINE] Etapa 3/3 — Salvando arquivos")

    output_root = audio_path.parents[1]
    transcripts_dir = output_root / "transcripts"
    transcripts_dir.mkdir(parents=True, exist_ok=True)

    name = args.slug or audio_path.stem

    transcript_path = transcripts_dir / f"{name}_transcricao.txt"
    transcript_path.write_text(text, encoding="utf-8")

    metrics_path = transcripts_dir / f"{name}_metrics.json"
    metrics_path.write_text(
        json.dumps(
            {
                "audio": audio_path.name,
                "session_type": args.type,
                "model": core_result.get("model"),
                "pipeline_seconds": round(time.time() - start, 2),
                "text_length": len(text),
            },
            indent=2,
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )

    print("[PIPELINE] Finalizado com sucesso")


if __name__ == "__main__":
    main()
