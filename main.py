# main.py
"""
Changelog:
- v1.1.0
  - Documentação do fluxo interativo
  - Garantia de uso do texto pós-processado
"""

from pathlib import Path
from datetime import datetime

from recorder import record_until_enter
from transcriber import transcribe_audio, load_config


def get_base_output() -> Path:
    cfg = load_config()
    return Path(cfg.get("paths", {}).get("base_output", "output"))


def main():
    """
    Fluxo interativo de gravação + transcrição via terminal.
    """
    print(">> Iniciando gravação...")

    base = get_base_output()
    audio_dir = base / "audio"
    txt_dir = base / "transcripts"

    audio_dir.mkdir(parents=True, exist_ok=True)
    txt_dir.mkdir(parents=True, exist_ok=True)

    name = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    audio_path = audio_dir / f"{name}.wav"

    files = record_until_enter(audio_path)
    if not files:
        print("Nenhum áudio gravado.")
        return

    result = transcribe_audio(files[0], language="pt")
    text = result["text"]

    out = txt_dir / f"{name}.txt"
    out.write_text(text, encoding="utf-8")

    print(f">> Transcrição salva em {out}")


if __name__ == "__main__":
    main()
