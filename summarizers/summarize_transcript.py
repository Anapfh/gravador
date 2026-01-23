"""
summarize_transcript.py

Resumo / ATA via LLM com governança.
"""

# =========================
# Changelog
# =========================
#
# 2026-01-22
# - Integração obrigatória do Root Prompt
#
# =========================

from core.prompt_loader import build_prompt
from gemma import run_gemma


def summarize_transcript(transcript_text: str, session_type: str) -> str:
    prompt = build_prompt(
        task_prompt_file="ata_prompt.md",
        content=transcript_text,
    )
    return run_gemma(prompt)
