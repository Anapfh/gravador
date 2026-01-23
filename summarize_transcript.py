from pathlib import Path
from session_profiles import resolve_session_config
from gemma import run_gemma

def load_preamble_for_session(session_type: str) -> str:
    base_dir = Path(".")
    resolved = resolve_session_config(session_type, base_dir)
    return resolved["preamble_path"].read_text(encoding="utf-8")

def summarize_transcript(
    transcript_text: str,
    session_type: str,
) -> str:
    preamble = load_preamble_for_session(session_type)

    prompt = f"""{preamble}

TRANSCRIÇÃO:
{transcript_text}
"""

    try:
        return run_gemma(prompt)
    except Exception as e:
        return (
            "⚠️ Resumo automático indisponível no momento.\n\n"
            "Verifique se o Ollama está em execução.\n\n"
            f"Erro técnico: {e}"
        )
