"""
download_and_transcribe_youtube.py

Utilitário para:
- baixar áudio do YouTube
- normalizar para WAV 16kHz mono
- disparar o pipeline oficial de transcrição via CLI

Este script NÃO implementa lógica de transcrição.
Ele apenas orquestra chamadas externas conforme a arquitetura oficial.
"""

# =========================
# Changelog
# =========================
#
# 2026-01-20
# - Correção de path para cli_local.py (execução fora do diretório tests)
# - Resolução robusta da raiz do projeto via Path(__file__)
# - Nenhuma alteração de interface ou comportamento funcional
#
# =========================

import subprocess
import sys
from pathlib import Path


# =========================
# Configuração
# =========================

YOUTUBE_URL = "https://www.youtube.com/watch?v=EIp1YZpJ2Mw"
AUDIO_BASENAME = "youtube_teste"
SESSION_TYPE = "reuniao"


# =========================
# Resolução de paths
# =========================

# Diretório atual: .../tests/
CURRENT_DIR = Path(__file__).resolve().parent

# Raiz do projeto: .../gravador_transcritor/
PROJECT_ROOT = CURRENT_DIR.parent

OUTPUT_AUDIO_DIR = PROJECT_ROOT / "output" / "audio"
CLI_PATH = PROJECT_ROOT / "cli_local.py"


# =========================
# Utilitários
# =========================

def run(cmd: list[str]) -> None:
    """
    Executa um comando externo e falha explicitamente
    caso o retorno não seja zero.

    Args:
        cmd (list[str]): comando a ser executado
    """
    result = subprocess.run(cmd)
    if result.returncode != 0:
        raise RuntimeError("Erro ao executar comando externo")


# =========================
# Fluxo principal
# =========================

def main() -> None:
    """
    Fluxo principal:
    1. Baixa o áudio do YouTube
    2. Converte para WAV 16kHz mono
    3. Dispara a transcrição via CLI oficial
    """

    OUTPUT_AUDIO_DIR.mkdir(parents=True, exist_ok=True)

    audio_path = OUTPUT_AUDIO_DIR / f"{AUDIO_BASENAME}.wav"

    yt_cmd = [
        "yt-dlp",
        "-x",
        "--audio-format", "wav",
        "--audio-quality", "0",
        "--postprocessor-args", "ffmpeg:-ar 16000 -ac 1",
        "--js-runtimes", "node",
        "-o", str(OUTPUT_AUDIO_DIR / f"{AUDIO_BASENAME}.%(ext)s"),
        YOUTUBE_URL,
    ]

    print("▶ Baixando áudio do YouTube...")
    run(yt_cmd)

    if not CLI_PATH.exists():
        raise FileNotFoundError(f"CLI não encontrado em: {CLI_PATH}")

    cli_cmd = [
        sys.executable,
        str(CLI_PATH),
        "transcrever",
        "-a", str(audio_path),
        "-t", SESSION_TYPE,
    ]

    print("▶ Iniciando transcrição...")
    run(cli_cmd)


if __name__ == "__main__":
    main()
