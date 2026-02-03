"""
structural.py
Refino estrutural de transcrições de áudio.

Objetivo:
- Melhorar legibilidade do texto transcrito
- Organizar em parágrafos coerentes
- Reduzir ruídos conversacionais
- Ajustar pontuação básica
- Preparar o texto para sumarização posterior

Este módulo NÃO utiliza IA.
Ele opera apenas com regras determinísticas e heurísticas simples.
"""

from __future__ import annotations
import re
import logging
from typing import List

logger = logging.getLogger(__name__)


# -----------------------------------------------------
# Configurações básicas
# -----------------------------------------------------

# Expressões comuns de ruído conversacional
FILLER_WORDS = [
    r"\bné\b",
    r"\btá\b",
    r"\bentão\b",
    r"\bassim\b",
    r"\baham\b",
    r"\buhum\b",
    r"\béé+\b",
]

# Tamanho mínimo para considerar uma frase válida
MIN_SENTENCE_LENGTH = 20


# -----------------------------------------------------
# Funções utilitárias
# -----------------------------------------------------

def _remove_fillers(text: str) -> str:
    """Remove palavras de preenchimento comuns."""
    for filler in FILLER_WORDS:
        text = re.sub(filler, "", text, flags=re.IGNORECASE)
    return text


def _normalize_spacing(text: str) -> str:
    """Normaliza espaços e quebras de linha."""
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


def _split_sentences(text: str) -> List[str]:
    """
    Divide o texto em frases usando pontuação básica.
    Não é linguística perfeita — é intencionalmente simples.
    """
    parts = re.split(r"(?<=[.!?])\s+", text)
    return [p.strip() for p in parts if p.strip()]


def _merge_short_sentences(sentences: List[str]) -> List[str]:
    """
    Junta frases muito curtas à frase anterior,
    evitando parágrafos fragmentados.
    """
    merged: List[str] = []

    for sentence in sentences:
        if not merged:
            merged.append(sentence)
            continue

        if len(sentence) < MIN_SENTENCE_LENGTH:
            merged[-1] = f"{merged[-1]} {sentence}"
        else:
            merged.append(sentence)

    return merged


def _build_paragraphs(sentences: List[str]) -> str:
    """
    Agrupa frases em parágrafos simples.
    Cada parágrafo representa uma ideia contínua.
    """
    paragraphs: List[str] = []
    current: List[str] = []

    for sentence in sentences:
        current.append(sentence)

        # Heurística simples: novo parágrafo a cada 3 frases
        if len(current) >= 3:
            paragraphs.append(" ".join(current))
            current = []

    if current:
        paragraphs.append(" ".join(current))

    return "\n\n".join(paragraphs)


# -----------------------------------------------------
# Função principal
# -----------------------------------------------------

def refine_structural(text: str) -> str:
    """
    Aplica refino estrutural ao texto transcrito.

    Pipeline:
    1. Remoção de ruídos conversacionais
    2. Normalização de espaços
    3. Quebra em frases
    4. União de frases curtas
    5. Agrupamento em parágrafos

    Retorna texto estruturado e legível.
    """

    if not text or not text.strip():
        logger.warning("Texto vazio recebido para refino estrutural")
        return ""

    logger.info("Iniciando refino estrutural do texto")

    original_length = len(text)

    text = _remove_fillers(text)
    text = _normalize_spacing(text)

    sentences = _split_sentences(text)
    sentences = _merge_short_sentences(sentences)

    refined = _build_paragraphs(sentences)
    refined = _normalize_spacing(refined)

    logger.info(
        "Refino estrutural concluído | chars antes=%s | chars depois=%s",
        original_length,
        len(refined),
    )

    return refined
