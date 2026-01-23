from summarizers.corporate_minutes import generate_corporate_minutes


def fake_llm(prompt: str) -> str:
    return "# Ata\n\nConteúdo gerado."


if __name__ == "__main__":
    try:
        generate_corporate_minutes(
            transcription_text="",
            preamble_text="Você é um assistente corporativo.",
            context_label="reuniao_interna",
            llm_callable=fake_llm,
        )
    except Exception as e:
        print(type(e).__name__, ":", e)

