# gemma.py

import argparse
from pathlib import Path

import ollama


def run_gemma(prompt: str, model: str = "gemma:7b") -> str:
    """
    Envia um prompt completo para o modelo Gemma via Ollama e
    retorna apenas o conteúdo de texto da resposta.
    """
    response = ollama.chat(
        model=model,
        messages=[
            {
                "role": "user",
                "content": prompt,
            }
        ],
    )
    return response["message"]["content"]


def main():
    """
    Modo CLI simples: lê um arquivo .txt e gera um resumo
    usando um prompt interno genérico.
    """
    parser = argparse.ArgumentParser(
        description="Gerar resumo de transcrição usando Gemma via Ollama."
    )
    parser.add_argument(
        "-a",
        "--arquivo",
        type=str,
        required=True,
        help="Caminho para o arquivo de texto (.txt) com a transcrição.",
    )
    parser.add_argument(
        "-m",
        "--modo",
        type=str,
        choices=["general", "key-takeaways"],
        default="general",
        help="Modo de prompt interno (general ou key-takeaways).",
    )
    parser.add_argument(
        "--model",
        type=str,
        default="gemma:7b",
        help="Nome do modelo Ollama (ex.: gemma:7b).",
    )

    args = parser.parse_args()

    text_file_path = Path(args.arquivo)
    if not text_file_path.exists():
        raise SystemExit(f"Arquivo não encontrado: {text_file_path}")

    content = text_file_path.read_text(encoding="utf-8")

    prompts = {
        "general": (
            "Você receberá a transcrição de uma reunião ou treinamento.\n"
            "Produza um resumo conciso em português, destacando:\n"
            "- principais pontos discutidos\n"
            "- decisões tomadas\n"
            "- ações atribuídas\n\n"
            "TRANSCRIÇÃO:\n"
        ),
        "key-takeaways": (
            "Você receberá a transcrição de uma reunião ou treinamento.\n"
            "Liste os principais insights e takeaways em bullet points, incluindo:\n"
            "- pontos importantes discutidos\n"
            "- decisões\n"
            "- tarefas atribuídas\n\n"
            "TRANSCRIÇÃO:\n"
        ),
    }

    base_prompt = prompts[args.modo]
    full_prompt = f"{base_prompt}{content}"

    output = run_gemma(full_prompt, model=args.model)
    print(output)


if __name__ == "__main__":
    main()
