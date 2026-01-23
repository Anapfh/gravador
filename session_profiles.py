from pathlib import Path

ALIASES = {
    "curso": "aprendizado",
    "treinamento": "aprendizado",
    "capacitacao": "aprendizado",
    "ti": "gestao_contratos_ti",
    "contratos": "gestao_contratos_ti",
}

SESSION_MAP = {
    "reuniao_interna": "preamble_reuniao_interna.txt",
    "reuniao_externa": "preamble_reuniao_externa.txt",
    "aprendizado": "preamble_aprendizado.txt",
    "gestao_contratos_ti": "preamble_gestao_contratos_ti.txt",
    "outro": "preamble_generico.txt",
}


def resolve_session_config(session_type: str, base_dir: Path) -> dict:
    stype = (session_type or "outro").lower()
    stype = ALIASES.get(stype, stype)

    preamble = SESSION_MAP.get(stype, SESSION_MAP["outro"])
    path = base_dir / preamble

    if not path.exists():
        path = base_dir / SESSION_MAP["outro"]

    return {
        "session_type": stype,
        "preamble_path": path,
    }
