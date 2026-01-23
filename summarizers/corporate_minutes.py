"""
corporate_minutes.py

Responsabilidade:
- Gerar ata / resumo corporativo a partir de uma transcrição confiável
- Aplicar preâmbulo apenas em memória
- Nunca alterar a transcrição original
- Nunca persistir prompt ou preâmbulo em disco

Decisão técnica:
- ADR-002 — Estrutura de Resumo e Ata Corporativa

Status:
- Pipeline mínimo consolidado
- Seguro, previsível e auditável
"""

# =========================================================
# Changelog
# =========================================================
#
# v1.1.0 (2026-01-20)
# - Consolidação do gate de segurança para transcrição vazia
# - Docstrings completas com contrato explícito
# - Mensagens de erro padronizadas e auditáveis
# - Garantia de não persistência de prompt/preâmbulo
#
# v1.0.0 (2026-01-19)
# - Implementação inicial do pipeline mínimo (ADR-002)
#

# =========================================================
# API pública
# =========================================================

def generate_corporate_minutes(
    transcription_text: str,
    preamble_text: str,
    context_label: str,
    llm_callable,
) -> str:
    """
    Gera uma ata corporativa em Markdown a partir de uma transcrição confiável.

    Este método implementa o pipeline mínimo definido no ADR-002.
    Ele NÃO altera a transcrição original e NÃO persiste prompts em disco.

    Parâmetros:
    - transcription_text (str):
        Texto da transcrição, considerado fonte primária imutável.
    - preamble_text (str):
        Preâmbulo correspondente ao contexto (reunião interna, externa, etc.).
        Utilizado apenas em memória.
    - context_label (str):
        Rótulo informativo do contexto da sessão (ex.: "reuniao_interna").
    - llm_callable (callable):
        Função responsável por executar a chamada ao modelo de linguagem.
        Deve receber um único argumento (prompt) e retornar texto.

    Retorno:
    - str:
        Ata corporativa em formato Markdown.

    Exceções:
    - ValueError:
        Lançada quando a transcrição é vazia ou insuficiente.
    - RuntimeError:
        Lançada quando o LLM não retorna conteúdo válido.
    """

    # -----------------------------------------------------
    # Gate de segurança — transcrição vazia ou inválida
    # -----------------------------------------------------
    if not transcription_text or not transcription_text.strip():
        raise ValueError(
            "Não há conteúdo suficiente na transcrição para gerar ata."
        )

    # -----------------------------------------------------
    # Prompt construído apenas em memória
    # -----------------------------------------------------
    prompt = (
        f"{preamble_text}\n\n"
        f"Contexto da sessão: {context_label}\n\n"
        "Transcrição da reunião:\n"
        "\"\"\"\n"
        f"{transcription_text}\n"
        "\"\"\"\n\n"
        "Gere a ata conforme as instruções acima."
    )

    # -----------------------------------------------------
    # Chamada ao LLM (injetável para testes)
    # -----------------------------------------------------
    result = llm_callable(prompt)

    if not result or not str(result).strip():
        raise RuntimeError(
            "O modelo de linguagem não retornou conteúdo válido."
        )

    return str(result).strip()
