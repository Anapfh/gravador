# ADR-003 — Chunking Semântico para LLM

Status: Aprovado
Data: 2026-01-19

---

## Contexto

Transcrições de reuniões podem atingir dezenas de milhares de caracteres, excedendo limites de contexto de LLMs e aumentando risco de alucinação, perda de coerência ou resumos incompletos.

O envio do texto completo em um único prompt mostrou-se frágil e imprevisível.

---

## Decisão

Fica definido que textos longos **devem ser processados por chunking semântico**, respeitando limites de tokens e fronteiras lógicas do discurso.

O chunking não altera a transcrição original e ocorre **apenas no pipeline de resumo/síntese**.

---

## Estratégia de Chunking

1. Dividir a transcrição por **blocos semânticos**, priorizando:

   * pausas naturais
   * mudanças de tópico
   * marcadores discursivos

2. Cada chunk deve:

   * respeitar limite seguro de tokens
   * conter contexto suficiente para entendimento local

3. O LLM gera um **resumo parcial por chunk**.

4. Os resumos parciais são agregados em um **resumo final consolidado**.

---

## Consequências

### Benefícios

* Redução drástica de alucinação
* Maior previsibilidade de saída
* Escalabilidade para reuniões longas
* Melhor qualidade semântica

### Riscos

* Perda de contexto global se chunks forem mal definidos

Mitigação:

* Sobreposição leve entre chunks
* Consolidação final orientada por preâmbulo

---

## Status

Esta decisão está **aprovada** e deve ser aplicada em qualquer integração com LLM.
