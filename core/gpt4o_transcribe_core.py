"""
core/gpt4o_transcribe_core.py

Core de transcrição via GPT-4o-mini-transcribe (OpenAI).

IMPORTANTE:
- O cliente OpenAI só é inicializado no momento da chamada
- Este módulo pode existir sem OPENAI_API_KEY configurada
- Seguro para fallback com Whisper local
"""

from pathlib import Path
from typing import Dict

from openai import OpenAI


def gpt4o_transcribe(
    audio_path: Path,
    language: str = "pt",
) -> Dict:
    """
    Executa transcrição usando GPT-4o-mini-transcribe.

    Este método só deve ser chamado quando:
    - transcription.engine == "gpt4o"
    - OPENAI_API_KEY estiver configurada

    Retorno:
    - dict com:
        - text (str)
        - duration (float | None)
    """
    if not audio_path.exists():
        raise FileNotFoundError(f"Áudio não encontrado: {audio_path}")

    # 🔒 Cliente criado SOMENTE aqui
    client = OpenAI()

    with audio_path.open("rb") as audio_file:
        response = client.audio.transcriptions.create(
            file=audio_file,
            model="gpt-4o-mini-transcribe",
            language=language,
        )

    return {
        "text": response.text or "",
        "duration": None,
    }
