"""
app.py — Interface Streamlit para gravação e transcrição local.

Estado:
- UI declarativa (Streamlit)
- Recorder Streamlit não bloqueante
- Core decide nome final do WAV (fonte da verdade)
- Transcrição local via whisper_core

IMPORTANTE:
- NÃO usar main()
- NÃO usar if __name__ == "__main__"

CHANGELOG:
2026-01-26
- Corrigido contrato de path: UI passa a usar o Path retornado pelo core
- Removida suposição de nome de arquivo na UI
- Eliminado FileNotFoundError na transcrição
- Logs reforçados para rastreabilidade
"""

from pathlib import Path
import time
import logging
import tomllib
import streamlit as st

from core.recorder_streamlit import StreamlitRecorder
from core.whisper_core import whisper_transcribe

# =====================================================
# LOGGING
# =====================================================
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s",
)
logger = logging.getLogger(__name__)

# =====================================================
# CONFIG (carregamento único)
# =====================================================
CONFIG_PATH = Path("config.toml")
config = {}

if CONFIG_PATH.exists():
    with open(CONFIG_PATH, "rb") as f:
        config = tomllib.load(f)
    logger.info("config.toml carregado com sucesso")
else:
    logger.warning("config.toml não encontrado")

# =====================================================
# PATHS
# =====================================================
BASE_OUTPUT = Path(config.get("paths", {}).get("base_output", "output"))
AUDIO_DIR = BASE_OUTPUT / "audio"
TRANSCRIPT_DIR = BASE_OUTPUT / "transcripts"

AUDIO_DIR.mkdir(parents=True, exist_ok=True)
TRANSCRIPT_DIR.mkdir(parents=True, exist_ok=True)

# =====================================================
# SESSION STATE (inicialização segura)
# =====================================================
st.session_state.setdefault("recorder", None)
st.session_state.setdefault("audio_path", None)
st.session_state.setdefault("transcript_text", None)

# =====================================================
# UI — SEMPRE RENDERIZADA
# =====================================================
st.title("🎙️ Gravador & Transcritor Local")

filename = st.text_input(
    "Nome base do arquivo",
    value="sessao",
)

col1, col2 = st.columns(2)

# -----------------------------------------------------
# INICIAR GRAVAÇÃO
# -----------------------------------------------------
with col1:
    if st.button("▶️ Iniciar gravação"):
        if st.session_state.recorder and st.session_state.recorder.is_running():
            st.warning("Já existe uma gravação em andamento")
        else:
            recorder = StreamlitRecorder(
                output_dir=AUDIO_DIR,
                base_name=filename,
            )
            recorder.start()

            st.session_state.recorder = recorder
            st.session_state.audio_path = None
            st.session_state.transcript_text = None

            logger.info("Gravação iniciada | base_name=%s", filename)
            st.success("Gravação iniciada")

# -----------------------------------------------------
# FINALIZAR GRAVAÇÃO
# -----------------------------------------------------
with col2:
    if st.button("⏹️ Finalizar gravação"):
        recorder = st.session_state.get("recorder")

        if not recorder or not recorder.is_running():
            st.warning("Nenhuma gravação ativa para finalizar")
        else:
            recorder.stop()

            # 🔑 fonte da verdade: path retornado pelo core
            if recorder.final_audio_path:
                st.session_state.audio_path = recorder.final_audio_path
                logger.info(
                    "Gravação finalizada | path=%s",
                    recorder.final_audio_path,
                )
                st.success("Gravação finalizada com sucesso")
            else:
                logger.error("Gravação finalizada sem path retornado")
                st.error("Erro ao finalizar gravação")

st.divider()

# =====================================================
# TRANSCRIÇÃO (manual — Etapa 1)
# =====================================================
if st.session_state.audio_path and st.session_state.transcript_text is None:
    if st.button("📝 Transcrever áudio"):
        with st.spinner("Transcrevendo..."):
            try:
                audio_path = st.session_state.audio_path
                logger.info("Iniciando transcrição | audio=%s", audio_path)

                result = whisper_transcribe(audio_path)
                text = result.get("text", "").strip()

                if not text:
                    raise ValueError("Transcrição vazia")

                txt_path = TRANSCRIPT_DIR / f"{audio_path.stem}.txt"
                txt_path.write_text(text, encoding="utf-8")

                st.session_state.transcript_text = text

                logger.info("Transcrição concluída | %s", txt_path)
                st.success("Transcrição concluída")

            except Exception as e:
                logger.exception("Erro na transcrição")
                st.error(str(e))

# =====================================================
# EXIBIÇÃO
# =====================================================
if st.session_state.transcript_text:
    st.subheader("📝 Transcrição")
    st.text_area(
        "Texto transcrito",
        value=st.session_state.transcript_text,
        height=300,
    )
