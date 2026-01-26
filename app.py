"""
app.py

Interface Streamlit para gravação de áudio com pause/resume e finalização segura.

Princípios de arquitetura:
- Streamlit NÃO acessa session_state dentro de threads
- Threads não chamam st.* (UI)
- Comunicação thread → UI via estruturas simples (dict + flags)
- Core de gravação permanece intacto (core.recorder)

UX:
- Tempo atualizado por evento (pause / retomar / finalizar)
- Indicador visual contínuo de gravação (spinner)
- Botões habilitados/desabilitados conforme estado (Opção A)

Referências:
- docs/DECISIONS.md
- docs/STATUS_ATUAL.md
"""

from pathlib import Path
import threading
import time
import logging

import streamlit as st

from core.recorder import record_until_stop

# ---------------------------------------------------------------------
# Configuração
# ---------------------------------------------------------------------
AUDIO_DIR = Path("output/audio")
AUDIO_DIR.mkdir(parents=True, exist_ok=True)

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------
# Estado inicial
# ---------------------------------------------------------------------
def _init_state():
    defaults = {
        "recording": False,
        "paused": False,
        "finalizing": False,
        "start_time": None,
        "pause_started_at": None,
        "paused_time_total": 0.0,
        "audio_path": None,
        "stop_event": threading.Event(),
        "pause_event": threading.Event(),
        "result_holder": {},
    }

    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v

    # gravação começa despausada
    st.session_state.pause_event.set()


# ---------------------------------------------------------------------
# Cálculo de tempo
# ---------------------------------------------------------------------
def _tempo_total():
    if not st.session_state.start_time:
        return 0.0
    return time.time() - st.session_state.start_time


def _tempo_gravado():
    return max(0.0, _tempo_total() - st.session_state.paused_time_total)


# ---------------------------------------------------------------------
# Thread de gravação (SEM Streamlit aqui)
# ---------------------------------------------------------------------
def _record_worker(
    output_dir: Path,
    base_name: str,
    stop_event: threading.Event,
    pause_event: threading.Event,
    result_holder: dict,
):
    try:
        audio_path = record_until_stop(
            output_dir=output_dir,
            base_name=base_name,
            stop_event=stop_event,
            pause_event=pause_event,
            show_timer=False,
        )
        result_holder["audio_path"] = audio_path
    except Exception as exc:
        result_holder["error"] = str(exc)
        logger.exception("Erro na gravação (thread)")


# ---------------------------------------------------------------------
# UI principal
# ---------------------------------------------------------------------
def main():
    st.title("🎙️ Gravação de Áudio")

    _init_state()

    base_name = st.text_input(
        "Nome do arquivo de áudio",
        disabled=st.session_state.recording
    )

    col1, col2, col3 = st.columns(3)

    # -------------------------------------------------------------
    # Iniciar
    # -------------------------------------------------------------
    with col1:
        if st.button(
            "▶️ Iniciar",
            disabled=st.session_state.recording or not base_name
        ):
            logger.info("Início de gravação via Streamlit")

            # reset estado
            st.session_state.recording = True
            st.session_state.paused = False
            st.session_state.finalizing = False
            st.session_state.start_time = time.time()
            st.session_state.paused_time_total = 0.0
            st.session_state.pause_started_at = None
            st.session_state.audio_path = None

            # limpar eventos/resultados
            st.session_state.stop_event.clear()
            st.session_state.pause_event.set()
            st.session_state.result_holder.clear()

            threading.Thread(
                target=_record_worker,
                args=(
                    AUDIO_DIR,
                    base_name,
                    st.session_state.stop_event,
                    st.session_state.pause_event,
                    st.session_state.result_holder,
                ),
                daemon=True,
            ).start()

    # -------------------------------------------------------------
    # Pausar / Retomar
    # -------------------------------------------------------------
    with col2:
        if st.button(
            "⏸️ Pausar",
            disabled=not st.session_state.recording or st.session_state.paused
        ):
            logger.info("Gravação pausada via Streamlit")
            st.session_state.paused = True
            st.session_state.pause_started_at = time.time()
            st.session_state.pause_event.clear()

        if st.button(
            "▶️ Retomar",
            disabled=not st.session_state.paused
        ):
            logger.info("Gravação retomada via Streamlit")

            if st.session_state.pause_started_at is not None:
                paused_delta = time.time() - st.session_state.pause_started_at
                st.session_state.paused_time_total += paused_delta
            else:
                logger.warning(
                    "Retomada solicitada sem pausa registrada (estado inconsistente)"
                )

            st.session_state.pause_started_at = None
            st.session_state.paused = False
            st.session_state.pause_event.set()

    # -------------------------------------------------------------
    # Finalizar
    # -------------------------------------------------------------
    with col3:
        if st.button(
            "⏹️ Finalizar",
            disabled=not st.session_state.recording
        ):
            logger.info("Finalização solicitada via Streamlit")
            st.session_state.finalizing = True
            st.session_state.stop_event.set()

    # -------------------------------------------------------------
    # Status visual
    # -------------------------------------------------------------
    st.divider()

    if st.session_state.recording:
        estado = "⏸️ Pausado" if st.session_state.paused else "🔴 Gravando"
        st.markdown(f"**Estado:** {estado}")

        if not st.session_state.paused and not st.session_state.finalizing:
            with st.spinner("Gravação em andamento..."):
                pass

        st.markdown(
            f"⏱️ **Tempo total:** `{_tempo_total():.1f}s`  \n"
            f"🎙️ **Tempo gravado:** `{_tempo_gravado():.1f}s`"
        )

    if st.session_state.finalizing:
        st.info("Finalizando gravação, aguarde…")

    # -------------------------------------------------------------
    # Coleta de resultado do thread (UI controla)
    # -------------------------------------------------------------
    if st.session_state.finalizing:
        holder = st.session_state.result_holder

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

    if st.session_state.audio_path:
        st.write(st.session_state.audio_path)


if __name__ == "__main__":
    main()


# ---------------------------------------------------------------------
# CHANGELOG
# 2026-01-26
# - Implementação segura de gravação via Streamlit
# - Pause / Resume com tempo por evento
# - Finalização confiável sem travamento
# - Comunicação thread → UI sem acesso ilegal ao session_state
# - Logs adicionados para rastreabilidade
