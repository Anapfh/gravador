"""
summarizers/ollama_summarizer.py

Summarizer corporativo usando LLM local via Ollama.

Responsabilidade:
- Gerar resumos / atas a partir de texto já validado
- Não inventar informações
- Não manter estado
- Não acessar áudio diretamente

Inspirado conceitualmente em projetos públicos (GitHub),
sem reutilização direta de código.
"""

import ollama


def summarize_with_ollama(
    prompt: str,
    model: str = "gemma3:4b",
) -> str:
    """
    Executa sumarização usando modelo local via Ollama.

    Parâmetros:
    - prompt (str): prompt completo e fechado
    - model (str): modelo Ollama

    Retorno:
    - texto gerado pelo modelo
    """
    response = ollama.generate(
        model=model,
        prompt=prompt,
        options={
            "temperature": 0.2,
        },
    )

    return response.get("response", "").strip()
