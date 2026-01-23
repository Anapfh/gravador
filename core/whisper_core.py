"""
whisper_core.py

Backend canônico de transcrição usando faster-whisper.

Responsabilidades:
- Executar transcrição local (offline)
- Retornar resultado estruturado (dict)
- NÃO formatar saída (responsabilidade do CLI/UI)

Decisões:
- Backend: faster-whisper (performance + qualidade)
- Retorno: dict {"text", "language", "segments", "duration_s"}

Referências:
- docs/DECISIONS.md
- docs/POSTMORTEM_TRANSCRICAO.md
- docs/LESSONS_LEARNED_PIPELINE_TRANSCRICAO.md
"""

from __future__ import annotations

import logging
import time
from pathlib import Path
from typing import Dict, Any, List

from faster_whisper import WhisperModel

logger = logging.getLogger(__name__)

# ---------------------------------------------------------
# Configuração do modelo
# ---------------------------------------------------------
# Ajustes conservadores e estáveis
MODEL_NAME = "small"          # bom equilíbrio qualidade/velocidade
DEVICE = "cpu"                # local, sem GPU
COMPUTE_TYPE = "int8"         # rápido e leve em CPU

# Instância única (lazy)
_model: WhisperModel | None = None


def _get_model() -> WhisperModel:
    global _model
    if _model is None:
        logger.info(
            "Carregando faster-whisper | model=%s | device=%s | compute=%s",
            MODEL_NAME, DEVICE, COMPUTE_TYPE
        )
        _model = WhisperModel(
            MODEL_NAME,
            device=DEVICE,
            compute_type=COMPUTE_TYPE,
        )
    return _model


# ---------------------------------------------------------
# API pública
# ---------------------------------------------------------
def whisper_transcribe(audio_path: Path) -> Dict[str, Any]:
    """
    Executa transcrição do áudio usando faster-whisper.

    Args:
        audio_path: caminho para arquivo WAV (mono, 16kHz recomendado)

    Returns:
        dict com:
          - text: texto completo
          - language: idioma detectado
          - segments: lista de segmentos (start, end, text)
          - duration_s: tempo total de execução
    """

    if not audio_path.exists():
        raise FileNotFoundError(f"Áudio não encontrado: {audio_path}")

    model = _get_model()

    logger.info("Iniciando transcrição | audio=%s", audio_path)
    t0 = time.time()

    segments_iter, info = model.transcribe(
        str(audio_path),
        beam_size=5,
        vad_filter=True,     # ajuda em ruído/silêncios
    )

    segments: List[Dict[str, Any]] = []
    texts: List[str] = []

    for seg in segments_iter:
        seg_dict = {
            "start": float(seg.start),
            "end": float(seg.end),
            "text": seg.text.strip(),
        }
        segments.append(seg_dict)
        texts.append(seg_dict["text"])

    duration_s = time.time() - t0
    full_text = " ".join(texts).strip()

    result = {
        "text": full_text,
        "language": info.language,
        "segments": segments,
        "duration_s": duration_s,
    }

    logger.info(
        "Transcrição concluída | idioma=%s | segmentos=%d | chars=%d | tempo=%.2fs",
        info.language,
        len(segments),
        len(full_text),
        duration_s,
    )

    return result


# ---------------------------------------------------------
# CHANGELOG
# ---------------------------------------------------------
# 2026-01-23
# - Ativada transcrição real com faster-whisper
# - Modelo default: small (CPU, int8)
# - Retorno estruturado (dict) mantido
# - Logs de idioma, tempo e tamanho
