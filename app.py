"""
app.py

Responsabilidade:
- Interface Streamlit para transcrição e geração de atas/resumos
- SUPORTA:
    - Upload de WAV
    - Gravação local via microfone (NOVO)
- NÃO altera core nem lógica de ASR

Decisões técnicas:
- ADR-001 — Transcrição imutável
- ADR-002 — Estrutura de Resumo / Ata Corporativa
- Issue 1 — Streamlit UI (MVP)

Fontes:
- docs/ISSUES.md
- docs/DECISIONS.md
"""

from pathlib import Path
from datetime import datetime
import json
import threading
import streamlit as st

# =========================================================
# ANTES — imports existentes
# =========================================================
from transcriber import transcribe_audio, save_transcription_bundle
from session_profiles import resolve_session_config
from summarizers.corporate_minutes import generate_corporate_minutes
from summarizers.ollama_summarizer import summarize_with_ollama

# =========================================================
# NOVO — gravação local via core
# =========================================================
from core.recorder import record_until_stop


# =========================================================
# Diretórios base
# =========================================================
BASE_OUTPUT = Path("output")
TRANSCRIPTS_DIR = BASE_OUTPUT / "transcripts"
RECORDINGS_DIR = BASE_OUTPUT / "recordings"
SUMMARIES_DIR = BASE_OUTPUT / "summaries"

TRANSCRIPTS_DIR.mkdir(parents=True, exist_ok=True)
RECORDINGS_DIR.mkdir(parents=True, exist_ok=True)
SUMMARIES_DIR.mkdir(parents=True, exist_ok=True)


# =========================================================
# Utilidades
# =========================================================
def load_transcript_with_context(txt_path: Path) -> tuple[str, str]:
    text = txt_path.read_text(encoding="utf-8")
    meta_path = txt_path.with_suffix(".meta.json")

    if meta_path.exists():
        meta = json.loads(meta_path.read_text(encoding="utf-8"))
        return text, meta.get("session_type", "outro")

    return text, "outro"


def load_preamble(session_type: str) -> str:
    resolved = resolve_session_config(session_type, Path("."))
    return resolved["preamble_path"].read_text(encoding="utf-8")


# =========================================================
# Session State (NOVO)
# =========================================================
if "recording" not in st.session_state:
    st.session_state.recording = False

if "recorded_audio" not in st.session_state:
    st.session_state.recorded_audio = None


# =========================================================
# UI — Streamlit
# =========================================================
st.set_page_config(page_title="Gravador e Transcritor", page_icon="🎙️")
st.title("🎙️ Gravador e Transcritor")

# =========================================================
# ANTES — aviso fixo de CLI
# =========================================================
# NOVO — aviso atualizado, sem negar o CLI
st.info(
    "ℹ️ **Formas de entrada de áudio**\n\n"
    "- Gravação local via microfone (aba abaixo)\n"
    "- Upload de arquivo WAV\n"
    "- CLI (`python cli_local.py gravar`)\n\n"
    "Todos os métodos utilizam o mesmo pipeline de transcrição."
)

tipo = st.sidebar.selectbox(
    "Tipo de sessão",
    ["reuniao_interna", "reuniao_externa", "treinamento", "curso", "outro"],
)

tab_transc, tab_resumo = st.tabs(["🎛️ Transcrição", "📝 Ata / Resumo"])


# =========================================================
# Aba 1 — Transcrição
# =========================================================
with tab_transc:

    # -----------------------------------------------------
    # NOVO — gravação local via microfone
    # -----------------------------------------------------
    st.subheader("🎙️ Gravação local")

    nome_audio = st.text_input(
        "Nome base do arquivo de áudio",
        value="gravacao",
    )

    if not st.session_state.recording:
        if st.button("▶️ Gravar via microfone"):
            st.session_state.recording = True

            def _record():
                try:
                    audio_path = record_until_stop(
                        output_dir=RECORDINGS_DIR,
                        base_name=nome_audio,
                    )
                    st.session_state.recorded_audio = audio_path
                except Exception as e:
                    st.error(f"Falha na gravação: {e}")
                finally:
                    st.session_state.recording = False

            threading.Thread(target=_record, daemon=True).start()

    if st.session_state.recording:
        st.warning("🎙️ Gravando... pressione ENTER no terminal para finalizar")

    if st.session_state.recorded_audio:
        st.success(f"📄 Áudio gravado: {st.session_state.recorded_audio.name}")
        st.audio(str(st.session_state.recorded_audio))


    # -----------------------------------------------------
    # ANTES — upload de WAV (mantido)
    # -----------------------------------------------------
    st.divider()
    st.subheader("📤 Upload de arquivo WAV")

    uploaded = st.file_uploader(
        "Selecione um arquivo WAV para transcrição",
        type=["wav"],
    )

    wav_path: Path | None = None

    if uploaded:
        wav_path = RECORDINGS_DIR / uploaded.name
        wav_path.write_bytes(uploaded.read())
        st.audio(str(wav_path))

    # -----------------------------------------------------
    # Transcrição (comum aos dois fluxos)
    # -----------------------------------------------------
    audio_to_transcribe = (
        st.session_state.recorded_audio or wav_path
    )

    if audio_to_transcribe:
        if st.button("🧠 Transcrever áudio"):
            with st.spinner("Transcrevendo áudio..."):
                result = transcribe_audio(
                    audio_path=audio_to_transcribe,
                    session_type=tipo,
                )

            if not result["text"].strip():
                st.warning("Transcrição vazia após processamento.")
            else:
                out = (
                    TRANSCRIPTS_DIR
                    / f"{datetime.now():%Y-%m-%d_%H-%M-%S}_{tipo}.txt"
                )
                save_transcription_bundle(result, out)

                st.success("Transcrição concluída com sucesso.")
                st.text_area(
                    "Texto transcrito",
                    result["text"],
                    height=300,
                )


# =========================================================
# Aba 2 — Ata / Resumo (INALTERADA)
# =========================================================
with tab_resumo:
    files = sorted(TRANSCRIPTS_DIR.glob("*.txt"), reverse=True)

    if not files:
        st.info("Nenhuma transcrição disponível.")
    else:
        selected = st.selectbox(
            "Selecione a transcrição",
            files,
            format_func=lambda p: p.name,
        )

        text, ctx = load_transcript_with_context(selected)
        st.caption(f"Contexto detectado: **{ctx}**")

        st.text_area(
            "Transcrição (somente leitura)",
            text,
            height=300,
        )

        if st.button("Gerar ata / resumo"):
            try:
                if not text.strip():
                    raise ValueError(
                        "Transcrição vazia. Não é possível gerar ata."
                    )

                preamble = load_preamble(ctx)

                markdown = generate_corporate_minutes(
                    transcription_text=text,
                    preamble_text=preamble,
                    context_label=ctx,
                    llm_callable=summarize_with_ollama,
                )

                out_md = SUMMARIES_DIR / f"{selected.stem}_ata.md"
                out_md.write_text(markdown, encoding="utf-8")

                st.success("Ata gerada com sucesso.")
                st.markdown(markdown)
                st.caption(f"Arquivo salvo em: `{out_md}`")

            except ValueError as ve:
                st.warning(str(ve))

            except Exception as e:
                st.error(
                    "Erro ao gerar ata.\n\n"
                    f"Detalhe técnico: {e}"
                )
