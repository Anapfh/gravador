"""
app.py

Interface Streamlit para gravação e transcrição local de áudio.

Funcionalidades:
- Gravação de áudio
- Pause / Resume apenas como estado visual (UX)
- Finalização segura com geração de WAV
- Transcrição automática pós-gravação (Issue 4)
- Transcrição manual via botão
- Exibição do texto transcrito na UI
- Tratamento explícito de erros

Referências:
- docs/STATUS_ATUAL.md
- docs/DECISIONS.md
"""

from pathlib import Path
import threading
import time
import logging

import streamlit as st

from core.recorder import record_until_stop
from core.whisper_core import whisper_transcribe

# ---------------------------------------------------------------------
# Configuração
# ---------------------------------------------------------------------
AUDIO_DIR = Path("output/audio")
TRANSCRIPT_DIR = Path("output/transcripts")

AUDIO_DIR.mkdir(parents=True, exist_ok=True)
TRANSCRIPT_DIR.mkdir(parents=True, exist_ok=True)

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------
# Estado inicial
# ---------------------------------------------------------------------
def _init_state():
    defaults = {
        # gravação
        "recording": False,
        "paused": False,
        "finalizing": False,
        "start_time": None,
        "pause_started_at": None,
        "paused_time_total": 0.0,
        "audio_path": None,
        "stop_event": threading.Event(),
        "record_result": {},

        # transcrição
        "transcribing": False,
        "transcript_text": None,
        "transcription_error": None,
        "transcription_result": {},
    }

    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v


# ---------------------------------------------------------------------
# Utilitários de tempo (UX)
# ---------------------------------------------------------------------
def _tempo_total():
    if not st.session_state.start_time:
        return 0.0
    return time.time() - st.session_state.start_time


def _tempo_gravado():
    return max(0.0, _tempo_total() - st.session_state.paused_time_total)


# ---------------------------------------------------------------------
# Workers (threads) — SEM Streamlit aqui
# ---------------------------------------------------------------------
def _record_worker(output_dir, base_name, stop_event, result_holder):
    try:
        audio_path = record_until_stop(
            output_dir=output_dir,
            base_name=base_name,
            stop_event=stop_event,
            show_timer=False,
        )
        result_holder["audio_path"] = audio_path
    except Exception as exc:
        result_holder["error"] = str(exc)
        logger.exception("Erro na gravação")


def _transcribe_worker(audio_path: str, result_holder: dict):
    try:
        logger.info("Iniciando transcrição: %s", audio_path)
        result = whisper_transcribe(Path(audio_path))
        result_holder["text"] = result.get("text", "").strip()
    except Exception as exc:
        result_holder["error"] = str(exc)
        logger.exception("Erro na transcrição")


# ---------------------------------------------------------------------
# UI principal
# ---------------------------------------------------------------------
def main():
    st.title("🎙️ Gravação e Transcrição de Áudio")
    _init_state()

    base_name = st.text_input(
        "Nome do arquivo de áudio",
        disabled=st.session_state.recording
    )

    col1, col2, col3 = st.columns(3)

    # Iniciar gravação
    with col1:
        if st.button(
            "▶️ Iniciar",
            disabled=st.session_state.recording or not base_name
        ):
            logger.info("Início da gravação")

            st.session_state.recording = True
            st.session_state.paused = False
            st.session_state.finalizing = False
            st.session_state.start_time = time.time()
            st.session_state.paused_time_total = 0.0
            st.session_state.pause_started_at = None
            st.session_state.audio_path = None

            st.session_state.stop_event.clear()
            st.session_state.record_result.clear()

            threading.Thread(
                target=_record_worker,
                args=(
                    AUDIO_DIR,
                    base_name,
                    st.session_state.stop_event,
                    st.session_state.record_result,
                ),
                daemon=True,
            ).start()

    # Pausar / Retomar (UX)
    with col2:
        if st.button(
            "⏸️ Pausar",
            disabled=not st.session_state.recording or st.session_state.paused
        ):
            logger.info("Gravação pausada (UX)")
            st.session_state.paused = True
            st.session_state.pause_started_at = time.time()

        if st.button(
            "▶️ Retomar",
            disabled=not st.session_state.paused
        ):
            logger.info("Gravação retomada (UX)")
            if st.session_state.pause_started_at:
                st.session_state.paused_time_total += (
                    time.time() - st.session_state.pause_started_at
                )
            st.session_state.pause_started_at = None
            st.session_state.paused = False

    # Finalizar gravação
    with col3:
        if st.button(
            "⏹️ Finalizar",
            disabled=not st.session_state.recording
        ):
            logger.info("Finalização solicitada")
            st.session_state.finalizing = True
            st.session_state.stop_event.set()

    st.divider()

    # Status gravação
    if st.session_state.recording:
        estado = "⏸️ Pausado" if st.session_state.paused else "🔴 Gravando"
        st.markdown(f"**Estado:** {estado}")
        st.markdown(
            f"⏱️ **Tempo total:** `{_tempo_total():.1f}s`  \n"
            f"🎙️ **Tempo gravado:** `{_tempo_gravado():.1f}s`"
        )

    if st.session_state.finalizing:
        st.info("Finalizando gravação, aguarde…")

    # Coleta do resultado da gravação
    if st.session_state.finalizing:
        holder = st.session_state.record_result

        if "error" in holder:
            st.error(f"Erro na gravação: {holder['error']}")
            st.session_state.finalizing = False
            st.session_state.recording = False

        if "audio_path" in holder:
            st.session_state.audio_path = holder["audio_path"]
            st.session_state.finalizing = False
            st.session_state.recording = False
            st.session_state.paused = False

            st.success("Gravação concluída com sucesso!")
            logger.info("Arquivo gerado: %s", st.session_state.audio_path)

    # Transcrição (Issue 4)
    if st.session_state.audio_path:
        if (
            not st.session_state.transcribing
            and st.session_state.transcript_text is None
            and st.session_state.transcription_error is None
        ):
            logger.info("Transcrição automática disparada")
            st.session_state.transcribing = True
            st.session_state.transcription_result.clear()

            threading.Thread(
                target=_transcribe_worker,
                args=(
                    st.session_state.audio_path,
                    st.session_state.transcription_result,
                ),
                daemon=True,
            ).start()

        if st.button(
            "📝 Transcrever",
            disabled=st.session_state.transcribing
        ):
            logger.info("Transcrição manual solicitada")
            st.session_state.transcribing = True
            st.session_state.transcript_text = None
            st.session_state.transcription_error = None
            st.session_state.transcription_result.clear()

            threading.Thread(
                target=_transcribe_worker,
                args=(
                    st.session_state.audio_path,
                    st.session_state.transcription_result,
                ),
                daemon=True,
            ).start()

    # Status transcrição
    if st.session_state.transcribing:
        st.info("Transcrevendo áudio, aguarde…")

        holder = st.session_state.transcription_result

        if "error" in holder:
            st.session_state.transcribing = False
            st.session_state.transcription_error = holder["error"]

        if "text" in holder:
            st.session_state.transcribing = False
            st.session_state.transcript_text = holder["text"]

            txt_path = TRANSCRIPT_DIR / (
                Path(st.session_state.audio_path).stem + ".txt"
            )
            txt_path.write_text(st.session_state.transcript_text, encoding="utf-8")
            logger.info("Transcrição salva em: %s", txt_path)
            st.success("Transcrição concluída com sucesso!")

    # Exibição
    if st.session_state.transcription_error:
        st.error(f"Erro na transcrição: {st.session_state.transcription_error}")

    if st.session_state.transcript_text:
        st.subheader("📄 Transcrição")
        st.text_area(
            "Texto transcrito",
            value=st.session_state.transcript_text,
            height=300,
        )


if __name__ == "__main__":
    main()


# ---------------------------------------------------------------------
# CHANGELOG
# 2026-01-26
# - Issue 4: correção definitiva do contrato com recorder.py
# - Pause/Resume mantido como UX (não controle físico)
# - Transcrição automática e manual estáveis
# - Logs enriquecidos
