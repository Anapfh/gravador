"""
core/prompt_loader.py

Carregador e compositor de prompts do projeto.

Garante:
- Aplicação obrigatória do Root Prompt
- Governança centralizada de IA
"""

# =========================
# Changelog
# =========================
#
# 2026-01-22
# - Introdução do Root Prompt como guard rail técnico
#
# =========================

from pathlib import Path

PROMPTS_DIR = Path(__file__).parents[1] / "prompts"


def load_prompt(filename: str) -> str:
    path = PROMPTS_DIR / filename
    if not path.exists():
        raise FileNotFoundError(f"Prompt não encontrado: {path}")
    return path.read_text(encoding="utf-8")


def build_prompt(task_prompt_file: str, content: str) -> str:
    root = load_prompt("ROOT_PROMPT.md")
    task = load_prompt(task_prompt_file)

    return f"""
{root}

---

{task}

---

TEXTO DE ENTRADA:
{content}
""".strip()
