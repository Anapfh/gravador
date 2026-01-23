"""
hallucination.py

Refinador de corte de cauda alucinada.

Aplica regras defensivas para remover padrões
repetitivos sem diversidade lexical.

Contrato:
- ADR-001
- Nunca remove conteúdo válido no meio do texto
"""

def cut_hallucinated_tail(text: str, cfg: dict) -> str:
    """
    Corta cauda potencialmente alucinada.

    Se configuração estiver vazia, retorna texto original.
    """

    if not text or not cfg:
        return text

    words = text.split()

    min_words = cfg.get("min_words_for_checks", 0)
    window = cfg.get("max_tail_window_words", 0)
    min_repeats = cfg.get("min_repeats_for_tail_cut", 0)

    if len(words) < min_words:
        return text

    tail = words[-window:]
    unique_ratio = len(set(tail)) / max(len(tail), 1)

    if unique_ratio < cfg.get("diversity_threshold", 0):
        return " ".join(words[:-window])

    return text


# --------------------
# CHANGELOG
# --------------------
# 2026-01-22
# - Blindagem contra cfg vazio
# - Nenhuma mudança de regra
