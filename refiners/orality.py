"""
orality.py

Refinador determinístico de oralidade.

Remove ou suaviza termos de fala informal.
Não altera sentido semântico.

Contrato:
- Nunca retorna None
- Nunca inventa conteúdo
"""

from typing import Iterable


def normalize_orality(text: str, terms: Iterable[str]) -> str:
    """
    Remove termos de oralidade definidos em configuração.

    Se o texto estiver vazio, retorna vazio.
    """

    if not text:
        return text

    for term in terms:
        text = text.replace(f" {term} ", " ")

    return " ".join(text.split())


# --------------------
# CHANGELOG
# --------------------
# 2026-01-22
# - Garantia explícita de retorno string
# - Nenhuma alteração semântica
