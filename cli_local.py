"""
CLI principal do projeto de gravação e transcrição.

Responsabilidades:
- Orquestrar gravação (core.recorder)
- Orquestrar transcrição (core.whisper_core)
- Exibir status claro ao usuário
- Não conter lógica de áudio nem ASR

Fontes:
- docs/PROJECT_RULES.md
- docs/DECISIONS.md
- docs/LESSONS_LEARNED_PIPELINE_TRANSCRICAO.md
"""

import argparse
import logging
from pathlib import Path

from core.recorder import record_until_stop
from core.whisper_core import whisper_transcribe

# ---------------------------------------------------------
# Logging
# ---------------------------------------------------------
LOG_DIR = Path("logs")
LOG_DIR.mkdir(exist_ok=True)

logging.basicConfig(
    filename=LOG_DIR / "cli.log",
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s",
)

logger = logging.getLogger(__name__)

# ---------------------------------------------------------
# Constantes
# ---------------------------------------------------------
AUDIO_DIR = Path("output/audio")
TRANSCRIPT_DIR = Path("output/transcripts")


# ---------------------------------------------------------
# Comando: GRAVAR
# ---------------------------------------------------------
def cmd_gravar(_args):
    """
    Comando CLI para gravação de áudio.
    """

    base_name = input("📝 Nome do arquivo de áudio: ").strip()

    try:
        audio_path = record_until_stop(
            output_dir=AUDIO_DIR,
            base_name=base_name,
        )
    except Exception as e:
        print(f"\n❌ Falha na gravação: {e}")
        logger.exception("Falha na gravação")
        return

    print("\n✔ Gravação concluída com sucesso")
    print(f"📄 Arquivo gerado: {audio_path}")
    logger.info("Gravação concluída: %s", audio_path)


# ---------------------------------------------------------
# Comando: TRANSCRIBER
# ---------------------------------------------------------
def cmd_transcrever(args):
    """
    Comando CLI para transcrição de áudio usando Whisper.
    """

    audio_path = Path(args.audio)

    if not audio_path.exists():
        print(f"❌ Arquivo não encontrado: {audio_path}")
        return

    TRANSCRIPT_DIR.mkdir(parents=True, exist_ok=True)

    print("▶ Iniciando transcrição...")
    logger.info("Transcrição iniciada: %s", audio_path)

    try:
        result = whisper_transcribe(audio_path)
    except Exception:
        import traceback
        print("\n❌ Falha na transcrição:")
        traceback.print_exc()
        logger.exception("Falha na transcrição")
        return

    # 🔒 Correção canônica: tratar dict ou str
    if isinstance(result, dict):
        text = result.get("text", "")
        logger.info(
            "Resultado Whisper (dict) | keys=%s | chars=%d",
            list(result.keys()),
            len(text),
        )
    else:
        text = str(result)
        logger.info("Resultado Whisper (str) | chars=%d", len(text))

    output_path = TRANSCRIPT_DIR / audio_path.with_suffix(".txt").name
    output_path.write_text(text, encoding="utf-8")

    print("✔ Transcrição concluída")
    print(f"📄 Arquivo gerado: {output_path}")
    logger.info("Transcrição concluída: %s", output_path)


# ---------------------------------------------------------
# Main
# ---------------------------------------------------------
def main():
    parser = argparse.ArgumentParser(
        description="Gravador e Transcritor de Áudio (CLI)"
    )
    sub = parser.add_subparsers(dest="cmd")

    g = sub.add_parser("gravar", help="Gravar áudio")
    g.set_defaults(func=cmd_gravar)

    t = sub.add_parser("transcrever", help="Transcrever áudio WAV")
    t.add_argument(
        "-a", "--audio",
        required=True,
        help="Caminho do arquivo WAV",
    )
    t.set_defaults(func=cmd_transcrever)

    args = parser.parse_args()

    if not args.cmd:
        parser.print_help()
        return

    args.func(args)


if __name__ == "__main__":
    main()


# ---------------------------------------------------------
# CHANGELOG
# ---------------------------------------------------------
# 2026-01-23
# - Correção: suporte a retorno dict do Whisper
# - Logs explícitos de tamanho/keys do resultado
# - Mantida separação CLI vs core
