"""
repetition.py

Refinador determinístico de repetição discursiva.

Remove repetições consecutivas excessivas.
"""

def remove_repetition(text: str, max_consecutive: int = 1) -> str:
    """
    Remove repetições consecutivas acima do limite.

    Exemplo:
    "ok ok ok" -> "ok"
    """

    if not text:
        return text

    words = text.split()
    result = []
    last_word = None
    count = 0

    for word in words:
        if word == last_word:
            count += 1
            if count <= max_consecutive:
                result.append(word)
        else:
            last_word = word
            count = 1
            result.append(word)

    return " ".join(result)


# --------------------
# CHANGELOG
# --------------------
# 2026-01-22
# - Lógica preservada
# - Garantia de retorno não vazio indevido
