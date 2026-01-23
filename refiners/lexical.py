"""
lexical.py

Refinador lexical conservador.

Responsabilidades:
- Corrigir erros léxicos evidentes
- Nunca inventar conteúdo
- Nunca retornar None
"""

# =========================
# Changelog
# =========================
#
# 2026-01-21
# - Contrato absoluto: sempre retorna string
#
# =========================

import re


_CORRECTIONS = {
    r"\biscos\b": "riscos",
    r"\bconis\b": "cones",
    r"\bcônis\b": "cones",
    r"\bvariedade da cnh\b": "validade da cnh",
}


def refine_lexical(text: str) -> str:
    if not isinstance(text, str) or not text.strip():
        return ""

    out = text
    for pattern, replacement in _CORRECTIONS.items():
        out = re.sub(pattern, replacement, out, flags=re.IGNORECASE)

    return out
