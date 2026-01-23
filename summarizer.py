from pathlib import Path
from datetime import datetime


def save_training_markdown(
    transcription: dict,
    title: str,
    output_path: Path
) -> Path:
    text = transcription.get("text", "")

    resumo_curto = (
        text[:1000] + "..."
        if len(text) > 1000
        else text
    )

    md = []
    md.append(f"# {title}\n")
    md.append("## Objetivo do treinamento\n")
    md.append(
        "Descrever em alto nível o objetivo do treinamento "
        "com base na transcrição.\n"
    )
    md.append("## Resumo geral\n")
    md.append(resumo_curto + "\n")
    md.append("## Transcrição completa\n")
    md.append("```text")
    md.append(text)
    md.append("```")

    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text("\n".join(md), encoding="utf-8")
    return output_path


def save_meeting_minutes_markdown(
    transcription: dict,
    title: str,
    output_path: Path,
    date: datetime | None = None,
) -> Path:
    text = transcription.get("text", "")
    date_str = (date or datetime.now()).strftime("%Y-%m-%d")

    md = []
    md.append(f"# Ata – {title}\n")
    md.append(f"**Data:** {date_str}\n")
    md.append("**Participantes:** _preencher manualmente_\n")
    md.append("\n## Pauta\n")
    md.append("- Item 1\n- Item 2\n")
    md.append("\n## Discussões\n")
    md.append(
        "Descrever os principais pontos discutidos, agrupando por tema.\n"
    )
    md.append("\n## Decisões\n")
    md.append("1. Descrição da decisão 1 – Responsável – Prazo.\n")
    md.append("2. Descrição da decisão 2 – Responsável – Prazo.\n")
    md.append("\n## Ações/Pendências\n")
    md.append("- Responsável – Descrição da ação – Prazo.\n")
    md.append("\n## Transcrição completa\n")
    md.append("```text")
    md.append(text)
    md.append("```")

    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text("\n".join(md), encoding="utf-8")
    return output_path
