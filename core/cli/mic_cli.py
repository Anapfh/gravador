from __future__ import annotations

import argparse
import logging
import sys
import tempfile
import wave
from pathlib import Path
from typing import Optional, TYPE_CHECKING

PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

if TYPE_CHECKING:
    from core.audio.mic_recorder import MicRecorder


def _write_temp_wav(audio_bytes: bytes, sample_rate: int) -> Path:
    temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".wav")
    temp_path = Path(temp_file.name)
    temp_file.close()

    with wave.open(str(temp_path), "wb") as wav_file:
        wav_file.setnchannels(1)
        wav_file.setsampwidth(2)
        wav_file.setframerate(sample_rate)
        wav_file.writeframes(audio_bytes)

    return temp_path


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Grava audio do microfone, salva temporariamente e transcreve com faster-whisper."
        )
    )

    parser.add_argument(
        "--duration",
        type=float,
        default=None,
        help="Duracao da gravacao em segundos. Se omitido, grava ate silencio.",
    )
    parser.add_argument(
        "--model",
        default="base",
        help="Modelo Whisper (ex: tiny, base, small, medium, large-v3).",
    )
    parser.add_argument(
        "--device",
        default="auto",
        help="Dispositivo para inferencia (cpu, cuda ou auto).",
    )
    parser.add_argument(
        "--compute-type",
        default="int8",
        help="Compute type do faster-whisper (ex: int8, float16).",
    )
    parser.add_argument(
        "--sample-rate",
        type=int,
        default=16000,
        help="Taxa de amostragem do microfone.",
    )
    parser.add_argument(
        "--energy",
        type=int,
        default=300,
        help="Energy threshold do reconhecimento de fala.",
    )
    parser.add_argument(
        "--pause",
        type=float,
        default=0.8,
        help="Tempo de pausa para finalizar a fala.",
    )
    parser.add_argument(
        "--dynamic-energy",
        action="store_true",
        help="Ativa ajuste dinamico de energia.",
    )
    parser.add_argument(
        "--mic-index",
        type=int,
        default=None,
        help="Indice do microfone (opcional).",
    )
    parser.add_argument(
        "--language",
        default=None,
        help="Idioma (ex: pt, en). Se omitido, autodetect.",
    )
    parser.add_argument(
        "--output",
        default="output/transcricao.txt",
        help="Caminho do arquivo de saida do texto.",
    )

    return parser.parse_args()


def _record_audio(mic: "MicRecorder", duration: Optional[float]) -> bytes:
    with mic.source as microphone:
        if duration is None:
            audio = mic.recognizer.listen(microphone)
        else:
            audio = mic.recognizer.record(microphone, duration=duration)
    return audio.get_raw_data()


def main() -> int:
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(name)s: %(message)s",
    )
    logger = logging.getLogger("mic_cli")

    args = _parse_args()

    from core.audio.mic_recorder import MicRecorder

    mic = MicRecorder(
        model=args.model,
        device=args.device,
        compute_type=args.compute_type,
        sample_rate=args.sample_rate,
        energy=args.energy,
        pause=args.pause,
        dynamic_energy=args.dynamic_energy,
        mic_index=args.mic_index,
        language=args.language,
    )

    logger.info("Gravando audio do microfone...")
    audio_bytes = _record_audio(mic, args.duration)

    temp_wav = _write_temp_wav(audio_bytes, args.sample_rate)
    logger.info("Audio salvo temporariamente em %s", temp_wav)

    try:
        text = mic.transcribe_audio(audio_bytes)
    finally:
        try:
            temp_wav.unlink(missing_ok=True)
        except OSError:
            logger.warning("Nao foi possivel remover o arquivo temporario: %s", temp_wav)

    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(text, encoding="utf-8-sig")

    logger.info("Transcricao salva em %s", output_path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
