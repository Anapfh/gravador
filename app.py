"""
app.py — Interface Streamlit para gravacao e transcricao local.

Pipeline:
- Captura de audio (RAW)
- Transcricao Whisper
- Refino estrutural deterministico (TXT)
- Persistencia de RAW (JSON)

Etapa 2.1:
- Refino estrutural aplicado sem uso de IA
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
from refiners.structural import refine_structural
from core.summarizers.pipeline import run_summary_pipeline

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
st.session_state.setdefault("summary_output", None)
st.session_state.setdefault("recorded_files", [])

# =====================================================
# UTILS
# =====================================================
def get_audio_duration_seconds(path: Path) -> float | None:
    """
    Retorna duracao em segundos apenas para WAV.
    Para outros formatos, retorna None.
    """
    try:
        if path.suffix.lower() != ".wav":
            logger.info("Duracao ignorada (nao WAV): %s", path.name)
            return None

        with wave.open(str(path), "rb") as wf:
            return wf.getnframes() / float(wf.getframerate())

    except Exception as e:
        logger.warning("Falha ao calcular duracao | %s | %s", path.name, e)
        return None


def open_folder(path: Path):
    if sys.platform.startswith("win"):
        subprocess.Popen(f'explorer "{path}"')
    elif sys.platform.startswith("darwin"):
        subprocess.Popen(["open", path])
    else:
        subprocess.Popen(["xdg-open", path])


def list_session_dirs(base_dir: Path) -> list[Path]:
    if not base_dir.exists():
        return []
    return sorted(
        [p for p in base_dir.iterdir() if p.is_dir() and p.name.startswith("session_")],
        key=lambda p: p.stat().st_mtime,
        reverse=True,
    )

# =====================================================
# UI — TITULO
# =====================================================
st.title("Gravador & Transcritor Local")

# =====================================================
# BLOCO 1 — GRAVACAO
# =====================================================
filename = st.text_input("Nome base do arquivo", value="sessao")
col1, col2 = st.columns(2)

with col1:
    if st.button("Iniciar gravacao"):
        recorder = StreamlitRecorder(
            output_dir=AUDIO_DIR,
            base_name=filename,
        )
        recorder.start()
        st.session_state.recorder = recorder
        st.session_state.audio_path = None
        st.session_state.transcript_text = None
        st.session_state.stats = None
        st.session_state.recorded_files = []
        st.success("Gravacao iniciada")

with col2:
    if st.button("Pausar gravacao"):
        recorder = st.session_state.get("recorder")
        if recorder and recorder.is_running():
            recorder.stop()
            st.session_state.audio_path = recorder.final_audio_path
            if recorder.final_audio_path:
                st.session_state.recorded_files.append(recorder.final_audio_path)
            st.success("Gravacao pausada (arquivo atual finalizado)")

with col2:
    if st.button("Retomar gravacao"):
        recorder = StreamlitRecorder(
            output_dir=AUDIO_DIR,
            base_name=filename,
        )
        recorder.start()
        st.session_state.recorder = recorder
        st.success("Gravacao retomada")

with col2:
    if st.button("Finalizar gravacao"):
        recorder = st.session_state.get("recorder")
        if recorder and recorder.is_running():
            recorder.stop()
            st.session_state.audio_path = recorder.final_audio_path
            if recorder.final_audio_path:
                st.session_state.recorded_files.append(recorder.final_audio_path)
            st.success("Gravacao finalizada")

st.divider()

# =====================================================
# BLOCO 2 — TRANSCRICAO DA GRAVACAO ATUAL
# =====================================================
if st.session_state.audio_path and st.session_state.transcript_text is None:
    if st.button("Transcrever gravacao atual"):
        with st.spinner("Transcrevendo audio gravado..."):
            audio_path = st.session_state.audio_path

            result = whisper_transcribe(audio_path)
            raw_text = result.get("text", "").strip()

            refined_text = refine_structural(raw_text)

            txt = TRANSCRIPT_DIR / f"{audio_path.stem}.txt"
            jsn = TRANSCRIPT_DIR / f"{audio_path.stem}.json"

            txt.write_text(refined_text, encoding="utf-8")
            jsn.write_text(
                json.dumps(result, ensure_ascii=False, indent=2),
                encoding="utf-8",
            )

            duration = get_audio_duration_seconds(audio_path)
            words = len(refined_text.split())

            st.session_state.transcript_text = refined_text
            st.session_state.stats = {
                "duration": duration,
                "words": words,
            }

st.divider()

# =====================================================
# BLOCO 3 — TRANSCRICAO DE AUDIO EXISTENTE (INDEPENDENTE)
# =====================================================
st.subheader("Transcrever audio existente")

uploaded_file = st.file_uploader(
    "Selecione um arquivo de audio",
    type=["wav", "mp3", "m4a", "flac", "ogg"],
)

if uploaded_file:
    if st.button("Transcrever arquivo selecionado"):
        with st.spinner("Transcrevendo arquivo, isso pode levar alguns minutos..."):
            temp_audio = AUDIO_DIR / uploaded_file.name
            temp_audio.write_bytes(uploaded_file.read())

            logger.info("Transcricao manual iniciada | %s", temp_audio)

            result = whisper_transcribe(temp_audio)
            raw_text = result.get("text", "").strip()

            duration = get_audio_duration_seconds(temp_audio)
            if duration and duration > 30 and len(raw_text) < 80:
                logger.warning("Transcricao curta detectada | retry sem VAD")
                result = whisper_transcribe(temp_audio, vad_filter=False)
                raw_text = result.get("text", "").strip()

            refined_text = refine_structural(raw_text)

            txt = TRANSCRIPT_DIR / f"{temp_audio.stem}.txt"
            jsn = TRANSCRIPT_DIR / f"{temp_audio.stem}.json"

            txt.write_text(refined_text, encoding="utf-8")
            jsn.write_text(
                json.dumps(result, ensure_ascii=False, indent=2),
                encoding="utf-8",
            )

            duration = get_audio_duration_seconds(temp_audio)
            words = len(refined_text.split())

            st.session_state.external_transcript = refined_text
            st.session_state.external_stats = {
                "duration": duration,
                "words": words,
            }

            st.success("Transcricao concluida")

# =====================================================
# BLOCO 4 — EXIBICAO DO RESULTADO
# =====================================================
if st.session_state.external_transcript:
    st.subheader("Transcricao do arquivo")

    col1, col2 = st.columns(2)

    if st.session_state.external_stats["duration"] is not None:
        col1.metric(
            "Duracao (s)",
            round(st.session_state.external_stats["duration"], 2),
        )
    else:
        col1.caption("Duracao indisponivel para este formato")

    col2.metric("Palavras", st.session_state.external_stats["words"])

    st.text_area(
        "Texto transcrito",
        value=st.session_state.external_transcript,
        height=300,
    )

    st.button(
        "Abrir pasta de transcricoes",
        on_click=open_folder,
        args=(TRANSCRIPT_DIR,),
    )

st.divider()

# =====================================================
# BLOCO 5 — RESUMO / ATA A PARTIR DE TRANSCRICAO CONSOLIDADA
# =====================================================
st.subheader("Resumo / Ata (transcricao consolidada)")

session_dirs = list_session_dirs(BASE_OUTPUT)
session_labels = [p.name for p in session_dirs]

selected_session = st.selectbox(
    "Sessao com transcricao consolidada",
    options=session_labels,
    index=0 if session_labels else None,
)

meeting_type = st.selectbox(
    "Tipo de reuniao",
    options=[
        "daily",
        "reuniao_interna",
        "reuniao_externa",
        "outro",
        "kickoff",
        "planejamento_sprint",
        "retrospectiva",
        "incidente_postmortem",
        "one_on_one",
        "treinamento",
    ],
    index=1,
)

if st.button("Gerar resumo/ata"):
    if not selected_session:
        st.error("Nenhuma sessao encontrada em output/")
    else:
        session_dir = BASE_OUTPUT / selected_session
        with st.spinner("Gerando resumo/ata..."):
            try:
                output_path = run_summary_pipeline(session_dir, meeting_type)
                st.session_state.summary_output = output_path
                st.success(f"Resumo gerado: {output_path.name}")
            except Exception as exc:
                st.error(f"Falha ao gerar resumo/ata: {exc}")

if st.session_state.summary_output:
    st.button(
        "Abrir pasta da sessao",
        on_click=open_folder,
        args=(st.session_state.summary_output.parent,),
    )

