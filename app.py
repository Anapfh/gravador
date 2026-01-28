"""
app.py — Interface Streamlit para gravação e transcrição local.

Correções importantes:
- Duração calculada apenas para WAV (evita wave.Error)
- Transcrição de arquivos externos desacoplada da gravação
- Estado persistido corretamente no Streamlit
"""

from pathlib import Path
import json
import logging
import tomllib
import wave
import streamlit as st
import subprocess
import sys

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
# CONFIG
# =====================================================
CONFIG_PATH = Path("config.toml")
config = {}

if CONFIG_PATH.exists():
    with open(CONFIG_PATH, "rb") as f:
        config = tomllib.load(f)
    logger.info("config.toml carregado")

# =====================================================
# PATHS
# =====================================================
BASE_OUTPUT = Path(config.get("paths", {}).get("base_output", "output"))
AUDIO_DIR = BASE_OUTPUT / "audio"
TRANSCRIPT_DIR = BASE_OUTPUT / "transcripts"

AUDIO_DIR.mkdir(parents=True, exist_ok=True)
TRANSCRIPT_DIR.mkdir(parents=True, exist_ok=True)

# =====================================================
# SESSION STATE
# =====================================================
st.session_state.setdefault("recorder", None)
st.session_state.setdefault("audio_path", None)
st.session_state.setdefault("transcript_text", None)
st.session_state.setdefault("stats", None)
st.session_state.setdefault("external_transcript", None)
st.session_state.setdefault("external_stats", None)

# =====================================================
# UTILS
# =====================================================
def get_audio_duration_seconds(path: Path) -> float | None:
    """
    Retorna duração em segundos apenas para arquivos WAV.
    Para outros formatos, retorna None.
    """
    try:
        if path.suffix.lower() != ".wav":
            logger.info("Duração ignorada (não WAV): %s", path.name)
            return None

        with wave.open(str(path), "rb") as wf:
            return wf.getnframes() / float(wf.getframerate())

    except Exception as e:
        logger.warning("Falha ao calcular duração | %s | %s", path.name, e)
        return None


def open_folder(path: Path):
    if sys.platform.startswith("win"):
        subprocess.Popen(f'explorer "{path}"')
    elif sys.platform.startswith("darwin"):
        subprocess.Popen(["open", path])
    else:
        subprocess.Popen(["xdg-open", path])

# =====================================================
# UI — TÍTULO
# =====================================================
st.title("🎙️ Gravador & Transcritor Local")

# =====================================================
# BLOCO 1 — GRAVAÇÃO
# =====================================================
filename = st.text_input("Nome base do arquivo", value="sessao")
col1, col2 = st.columns(2)

with col1:
    if st.button("▶️ Iniciar gravação"):
        recorder = StreamlitRecorder(
            output_dir=AUDIO_DIR,
            base_name=filename,
        )
        recorder.start()
        st.session_state.recorder = recorder
        st.session_state.audio_path = None
        st.session_state.transcript_text = None
        st.session_state.stats = None
        st.success("Gravação iniciada")

with col2:
    if st.button("⏹️ Finalizar gravação"):
        recorder = st.session_state.get("recorder")
        if recorder and recorder.is_running():
            recorder.stop()
            st.session_state.audio_path = recorder.final_audio_path
            st.success("Gravação finalizada")

st.divider()

# =====================================================
# BLOCO 2 — TRANSCRIÇÃO DA GRAVAÇÃO ATUAL
# =====================================================
if st.session_state.audio_path and st.session_state.transcript_text is None:
    if st.button("📝 Transcrever gravação atual"):
        with st.spinner("Transcrevendo áudio gravado..."):
            audio_path = st.session_state.audio_path
            result = whisper_transcribe(audio_path)
            text = result.get("text", "").strip()

            txt = TRANSCRIPT_DIR / f"{audio_path.stem}.txt"
            jsn = TRANSCRIPT_DIR / f"{audio_path.stem}.json"

            txt.write_text(text, encoding="utf-8")
            jsn.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")

            duration = get_audio_duration_seconds(audio_path)
            words = len(text.split())

            st.session_state.transcript_text = text
            st.session_state.stats = {
                "duration": duration,
                "words": words,
            }

st.divider()

# =====================================================
# BLOCO 3 — TRANSCRIÇÃO DE ÁUDIO EXISTENTE (INDEPENDENTE)
# =====================================================
st.subheader("📁 Transcrever áudio existente")

uploaded_file = st.file_uploader(
    "Selecione um arquivo de áudio",
    type=["wav", "mp3", "m4a", "flac", "ogg"],
)

if uploaded_file:
    if st.button("📝 Transcrever arquivo selecionado"):
        with st.spinner("⏳ Transcrevendo arquivo, isso pode levar alguns minutos..."):
            temp_audio = AUDIO_DIR / uploaded_file.name
            temp_audio.write_bytes(uploaded_file.read())

            logger.info("Transcrição manual iniciada | %s", temp_audio)

            result = whisper_transcribe(temp_audio)
            text = result.get("text", "").strip()

            txt = TRANSCRIPT_DIR / f"{temp_audio.stem}.txt"
            jsn = TRANSCRIPT_DIR / f"{temp_audio.stem}.json"

            txt.write_text(text, encoding="utf-8")
            jsn.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")

            duration = get_audio_duration_seconds(temp_audio)
            words = len(text.split())

            st.session_state.external_transcript = text
            st.session_state.external_stats = {
                "duration": duration,
                "words": words,
            }

            st.success("Transcrição concluída")

# =====================================================
# BLOCO 4 — EXIBIÇÃO DO RESULTADO
# =====================================================
if st.session_state.external_transcript:
    st.subheader("📝 Transcrição do arquivo")

    col1, col2 = st.columns(2)

    if st.session_state.external_stats["duration"] is not None:
        col1.metric("⏱️ Duração (s)", round(st.session_state.external_stats["duration"], 2))
    else:
        col1.caption("⏱️ Duração indisponível para este formato")

    col2.metric("🔤 Palavras", st.session_state.external_stats["words"])

    st.text_area(
        "Texto transcrito",
        value=st.session_state.external_transcript,
        height=300,
    )

    st.button(
        "📂 Abrir pasta de transcrições",
        on_click=open_folder,
        args=(TRANSCRIPT_DIR,),
    )
