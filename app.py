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
import re
import json
import logging
import tomllib
import wave
import streamlit as st
import subprocess
import sys
import time
import os
import csv

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


@st.cache_data(show_spinner=False)
def load_config(path: Path) -> dict:
    if not path.exists():
        return {}
    with open(path, "rb") as f:
        return tomllib.load(f)


config = load_config(CONFIG_PATH)

# =====================================================
# PATHS
# =====================================================
BASE_OUTPUT = Path(config.get("paths", {}).get("base_output", "output"))
AUDIO_DIR = BASE_OUTPUT / "audio"
TRANSCRIPT_DIR = BASE_OUTPUT / "transcripts"
SUMMARY_DIR = BASE_OUTPUT / "summaries"
QUALITY_DIR = BASE_OUTPUT / "quality"
VOCAB_PATH = Path(config.get("paths", {}).get("vocab_path", "vocab.csv"))

AUDIO_DIR.mkdir(parents=True, exist_ok=True)
TRANSCRIPT_DIR.mkdir(parents=True, exist_ok=True)
SUMMARY_DIR.mkdir(parents=True, exist_ok=True)
QUALITY_DIR.mkdir(parents=True, exist_ok=True)

# =====================================================
# TRANSCRIPTION SETTINGS
# =====================================================
WHISPER_CFG = config.get("transcription", {}).get("whisper", {})
VAD_FILTER_DEFAULT = WHISPER_CFG.get("vad_filter", False)
QUALITY_CFG = config.get("quality", {})
MIN_WPM = float(QUALITY_CFG.get("min_wpm", 90))
MAX_WPM = float(QUALITY_CFG.get("max_wpm", 220))
MIN_WORDS = int(QUALITY_CFG.get("min_words", 30))

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
st.session_state.setdefault("rec_status", "idle")
st.session_state.setdefault("rec_start_ts", None)
st.session_state.setdefault("rec_elapsed_total", 0.0)
st.session_state.setdefault("rec_paused", False)
st.session_state.setdefault("rec_last_action_ts", 0.0)
st.session_state.setdefault("last_transcript_path", None)

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


def open_file(path: Path):
    if not path or not path.exists():
        return
    if sys.platform.startswith("win"):
        os.startfile(path)  # type: ignore[attr-defined]
    elif sys.platform.startswith("darwin"):
        subprocess.Popen(["open", path])
    else:
        subprocess.Popen(["xdg-open", path])


def get_latest_file(directory: Path, pattern: str) -> Path | None:
    if not directory.exists():
        return None
    files = list(directory.glob(pattern))
    if not files:
        return None
    return max(files, key=lambda p: p.stat().st_mtime)


def _should_retry_without_vad(duration: float | None, raw_text: str) -> bool:
    if not duration or duration <= 30:
        return False
    chars = len(raw_text)
    words = len(raw_text.split())
    return chars < duration * 5 or words < duration * 0.6


def _compute_wpm(duration: float | None, words: int) -> float | None:
    if not duration or duration <= 0:
        return None
    minutes = duration / 60.0
    if minutes <= 0:
        return None
    return round(words / minutes, 2)


def _slugify(name: str) -> str:
    cleaned = re.sub(r"[^A-Za-z0-9_-]+", "_", name.strip())
    cleaned = re.sub(r"_+", "_", cleaned).strip("_")
    return cleaned or "arquivo"


def _ensure_vocab_file() -> None:
    if VOCAB_PATH.exists():
        return
    with VOCAB_PATH.open("w", encoding="utf-8-sig", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["source", "target"])


def _append_vocab_entry(source: str, target: str) -> None:
    _ensure_vocab_file()
    with VOCAB_PATH.open("a", encoding="utf-8-sig", newline="") as f:
        writer = csv.writer(f)
        writer.writerow([source, target])


def _load_vocab_entries() -> list[tuple[str, str]]:
    if not VOCAB_PATH.exists():
        return []
    entries: list[tuple[str, str]] = []
    with VOCAB_PATH.open("r", encoding="utf-8-sig", newline="") as f:
        reader = csv.reader(f)
        for row in reader:
            if not row or len(row) < 2:
                continue
            source, target = row[0].strip(), row[1].strip()
            if not source or source.lower() == "source":
                continue
            entries.append((source, target))
    return entries


def _save_vocab_entries(entries: list[tuple[str, str]]) -> None:
    _ensure_vocab_file()
    with VOCAB_PATH.open("w", encoding="utf-8-sig", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["source", "target"])
        for source, target in entries:
            writer.writerow([source, target])


def _assess_quality(duration: float | None, words: int, wpm: float | None) -> dict:
    status = "ok"
    reasons = []
    if words < MIN_WORDS:
        status = "warn"
        reasons.append(f"poucas_palavras<{MIN_WORDS}")
    if wpm is None:
        status = "warn"
        reasons.append("wpm_indisponivel")
    else:
        if wpm < MIN_WPM:
            status = "warn"
            reasons.append(f"wpm_baixo<{MIN_WPM}")
        if wpm > MAX_WPM:
            status = "warn"
            reasons.append(f"wpm_alto>{MAX_WPM}")
    return {"status": status, "reasons": reasons}


def _append_quality_report(payload: dict) -> None:
    jsonl_path = QUALITY_DIR / "quality_reports.jsonl"
    csv_path = QUALITY_DIR / "quality_reports.csv"

    # JSONL
    with open(jsonl_path, "a", encoding="utf-8") as jf:
        jf.write(json.dumps(payload, ensure_ascii=False) + "\n")

    # CSV (write header if needed)
    header = [
        "timestamp",
        "audio",
        "transcript",
        "duration_s",
        "words",
        "wpm",
        "status",
        "reasons",
        "mode",
    ]
    write_header = not csv_path.exists()
    with open(csv_path, "a", encoding="utf-8") as cf:
        if write_header:
            cf.write(",".join(header) + "\n")
        row = [
            str(payload.get("timestamp", "")),
            str(payload.get("audio", "")),
            str(payload.get("transcript", "")),
            str(payload.get("duration_s", "")),
            str(payload.get("words", "")),
            str(payload.get("wpm", "")),
            str(payload.get("status", "")),
            "|".join(payload.get("reasons", [])),
            str(payload.get("mode", "")),
        ]
        cf.write(",".join(row) + "\n")

# =====================================================
# UI — TITULO
# =====================================================
st.title("Gravador & Transcritor Local")

# =====================================================
# BLOCO 1 — GRAVACAO
# =====================================================
filename = st.text_input("Nome base do arquivo", value="sessao")
status_box = st.empty()

def _mark_action():
    st.session_state.rec_last_action_ts = time.time()


def _start_recording():
    recorder_local = StreamlitRecorder(
        output_dir=AUDIO_DIR,
        base_name=filename,
    )
    recorder_local.start()
    st.session_state.recorder = recorder_local
    st.session_state.audio_path = None
    st.session_state.transcript_text = None
    st.session_state.stats = None
    st.session_state.recorded_files = []
    st.session_state.rec_status = "recording"
    st.session_state.rec_start_ts = time.time()
    st.session_state.rec_elapsed_total = 0.0
    st.session_state.rec_paused = False
    _mark_action()
    status_box.success("Gravacao iniciada")


def _pause_recording():
    recorder_local = st.session_state.get("recorder")
    if recorder_local and recorder_local.is_running():
        recorder_local.pause()
        if st.session_state.rec_start_ts:
            st.session_state.rec_elapsed_total += max(
                0.0, time.time() - st.session_state.rec_start_ts
            )
        st.session_state.rec_start_ts = None
        st.session_state.rec_status = "paused"
        st.session_state.rec_paused = True
        _mark_action()
        status_box.info("Gravacao pausada (gap zero)")


def _resume_recording():
    recorder_local = st.session_state.get("recorder")
    if recorder_local and recorder_local.is_running():
        recorder_local.resume()
        st.session_state.rec_status = "recording"
        st.session_state.rec_start_ts = time.time()
        st.session_state.rec_paused = False
        _mark_action()
        status_box.success("Gravacao retomada")
    else:
        status_box.warning("Nao foi possivel retomar (gravacao nao ativa)")


def _finalize_recording():
    recorder_local = st.session_state.get("recorder")
    if recorder_local and recorder_local.is_running():
        recorder_local.stop()
        st.session_state.audio_path = recorder_local.final_audio_path
        if recorder_local.final_audio_path:
            st.session_state.recorded_files.append(recorder_local.final_audio_path)
    st.session_state.recorder = None
    if st.session_state.rec_start_ts:
        st.session_state.rec_elapsed_total += max(
            0.0, time.time() - st.session_state.rec_start_ts
        )
    st.session_state.rec_start_ts = None
    st.session_state.rec_status = "idle"
    st.session_state.rec_paused = False
    _mark_action()
    status_box.success("Gravacao finalizada")


recorder = st.session_state.get("recorder")
is_running = recorder is not None and recorder.is_running()
is_paused = recorder is not None and recorder.is_paused()
st.session_state.rec_paused = is_paused
is_idle = not is_running and not is_paused

time_since_action = time.time() - st.session_state.rec_last_action_ts
if is_paused:
    st.session_state.rec_status = "paused"
elif is_running:
    st.session_state.rec_status = "recording"
elif time_since_action < 2.0 and st.session_state.rec_status == "recording":
    # evita flicker logo apos iniciar
    st.session_state.rec_status = "recording"
else:
    st.session_state.rec_status = "idle"

metrics_col1, metrics_col2 = st.columns(2)
elapsed = st.session_state.rec_elapsed_total
if st.session_state.rec_status == "recording" and st.session_state.rec_start_ts:
    elapsed += max(0.0, time.time() - st.session_state.rec_start_ts)
metrics_col1.metric("Status", st.session_state.rec_status.upper())
metrics_col2.metric("Tempo gravado (s)", int(elapsed))

# Atualiza automaticamente o tempo enquanto estiver gravando
if st.session_state.rec_status == "recording":
    try:
        st.autorefresh(interval=1000, key="rec_autorefresh")
    except Exception:
        pass

btn_col1, btn_col2, btn_col3 = st.columns(3)

with btn_col1:
    st.button("Iniciar gravacao", disabled=not is_idle, on_click=_start_recording)

with btn_col2:
    st.button("Pausar gravacao", disabled=not is_running, on_click=_pause_recording)

with btn_col3:
    st.button("Retomar gravacao", disabled=not is_paused, on_click=_resume_recording)

st.button(
    "Finalizar gravacao",
    disabled=not is_running and not is_paused,
    on_click=_finalize_recording,
)

st.divider()

# =====================================================
# BLOCO 2 — TRANSCRICAO DA GRAVACAO ATUAL
# =====================================================
st.subheader("Transcrever gravacao atual")

latest_wav = get_latest_file(AUDIO_DIR, "*.wav")
if latest_wav:
    st.caption(f"Arquivo atual: {latest_wav.name}")
    st.session_state.audio_path = latest_wav
    if st.button("Transcrever gravacao atual"):
        with st.spinner("Transcrevendo audio gravado..."):
            audio_path = st.session_state.audio_path

            result = whisper_transcribe(audio_path, vad_filter=VAD_FILTER_DEFAULT)
            raw_text = result.get("text", "").strip()
            duration = get_audio_duration_seconds(audio_path)
            if VAD_FILTER_DEFAULT and _should_retry_without_vad(duration, raw_text):
                logger.warning("Transcricao curta detectada | retry sem VAD")
                result = whisper_transcribe(audio_path, vad_filter=False)
                raw_text = result.get("text", "").strip()
            result["audio_duration_s"] = duration

            refined_text = refine_structural(raw_text)

            txt = TRANSCRIPT_DIR / f"{audio_path.stem}.txt"
            raw_txt = TRANSCRIPT_DIR / f"{audio_path.stem}.raw.txt"
            jsn = TRANSCRIPT_DIR / f"{audio_path.stem}.json"

            txt.write_text(refined_text, encoding="utf-8-sig")
            raw_txt.write_text(raw_text, encoding="utf-8-sig")
            jsn.write_text(
                json.dumps(result, ensure_ascii=False, indent=2),
                encoding="utf-8-sig",
            )
            st.session_state.last_transcript_path = txt

            words = len(refined_text.split())
            wpm = _compute_wpm(duration, words)
            quality = _assess_quality(duration, words, wpm)

            _append_quality_report(
                {
                    "timestamp": int(time.time()),
                    "audio": audio_path.name,
                    "transcript": txt.name,
                    "duration_s": duration,
                    "words": words,
                    "wpm": wpm,
                    "status": quality["status"],
                    "reasons": quality["reasons"],
                    "mode": "recording",
                }
            )

            st.session_state.transcript_text = refined_text
            st.session_state.stats = {
                "duration": duration,
                "words": words,
                "wpm": wpm,
                "quality": quality,
            }
        st.success("Transcricao finalizada")
        if st.session_state.last_transcript_path:
            st.button(
                "Abrir ultima transcricao",
                on_click=open_file,
                args=(st.session_state.last_transcript_path,),
            )
        st.button(
            "Abrir pasta de transcricoes",
            on_click=open_folder,
            args=(TRANSCRIPT_DIR,),
        )
else:
    st.caption("Nenhuma gravacao finalizada ainda.")

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

            result = whisper_transcribe(temp_audio, vad_filter=VAD_FILTER_DEFAULT)
            raw_text = result.get("text", "").strip()

            duration = get_audio_duration_seconds(temp_audio)
            if VAD_FILTER_DEFAULT and _should_retry_without_vad(duration, raw_text):
                logger.warning("Transcricao curta detectada | retry sem VAD")
                result = whisper_transcribe(temp_audio, vad_filter=False)
                raw_text = result.get("text", "").strip()
            result["audio_duration_s"] = duration

            refined_text = refine_structural(raw_text)

            txt = TRANSCRIPT_DIR / f"{temp_audio.stem}.txt"
            raw_txt = TRANSCRIPT_DIR / f"{temp_audio.stem}.raw.txt"
            jsn = TRANSCRIPT_DIR / f"{temp_audio.stem}.json"

            txt.write_text(refined_text, encoding="utf-8-sig")
            raw_txt.write_text(raw_text, encoding="utf-8-sig")
            jsn.write_text(
                json.dumps(result, ensure_ascii=False, indent=2),
                encoding="utf-8-sig",
            )
            st.session_state.last_transcript_path = txt

            duration = get_audio_duration_seconds(temp_audio)
            words = len(refined_text.split())
            wpm = _compute_wpm(duration, words)
            quality = _assess_quality(duration, words, wpm)

            _append_quality_report(
                {
                    "timestamp": int(time.time()),
                    "audio": temp_audio.name,
                    "transcript": txt.name,
                    "duration_s": duration,
                    "words": words,
                    "wpm": wpm,
                    "status": quality["status"],
                    "reasons": quality["reasons"],
                    "mode": "upload",
                }
            )

            st.session_state.external_transcript = refined_text
            st.session_state.external_stats = {
                "duration": duration,
                "words": words,
                "wpm": wpm,
                "quality": quality,
            }
        st.success("Transcricao concluida")
        if st.session_state.last_transcript_path:
            st.button(
                "Abrir ultima transcricao",
                on_click=open_file,
                args=(st.session_state.last_transcript_path,),
            )

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
    if st.session_state.external_stats.get("wpm") is not None:
        col2.metric("Palavras/min", st.session_state.external_stats["wpm"])
    quality = st.session_state.external_stats.get("quality") or {}
    if quality.get("status") == "warn":
        st.warning(
            "Qualidade em alerta: "
            + ", ".join(quality.get("reasons", []))
            + " | verifique o audio/transcricao."
        )

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

with st.expander("Glossario (pos-processamento)", expanded=False):
    st.caption("Adicione termos para correção automática nos próximos resumos.")
    vocab_col1, vocab_col2 = st.columns(2)
    with vocab_col1:
        vocab_source = st.text_input("Termo errado", value="")
    with vocab_col2:
        vocab_target = st.text_input("Correcao", value="")
    if st.button("Adicionar ao glossario"):
        if not vocab_source.strip() or not vocab_target.strip():
            st.error("Preencha os dois campos.")
        else:
            _append_vocab_entry(vocab_source.strip(), vocab_target.strip())
            st.success("Termo adicionado ao glossario.")

    st.divider()
    entries = _load_vocab_entries()
    st.caption(f"Lista atual do glossario ({len(entries)} termos)")
    if not entries:
        st.info("Glossario vazio.")
    else:
        options = [f"{s} -> {t}" for s, t in entries]
        selected = st.selectbox("Selecionar entrada", options=options, index=None)

        action_col1, action_col2 = st.columns(2)
        with action_col1:
            if st.button("Remover selecionado"):
                if selected:
                    idx = options.index(selected)
                    entries.pop(idx)
                    _save_vocab_entries(entries)
                    st.success("Entrada removida do glossario.")
                else:
                    st.error("Selecione uma entrada para remover.")
        with action_col2:
            confirm_clear = st.checkbox("Confirmar limpeza total", value=False)
            if st.button("Limpar tudo"):
                if not confirm_clear:
                    st.error("Confirme a limpeza total antes de prosseguir.")
                else:
                    _save_vocab_entries([])
                    st.success("Glossario limpo.")

        st.divider()
        st.caption("Editar entrada")
        if selected:
            idx = options.index(selected)
            current_source, current_target = entries[idx]
            edit_col1, edit_col2 = st.columns(2)
            with edit_col1:
                edit_source = st.text_input(
                    "Termo errado (editar)",
                    value=current_source,
                    key="edit_source",
                )
            with edit_col2:
                edit_target = st.text_input(
                    "Correcao (editar)",
                    value=current_target,
                    key="edit_target",
                )
            if st.button("Salvar edicao"):
                if not edit_source.strip() or not edit_target.strip():
                    st.error("Preencha os dois campos.")
                else:
                    entries[idx] = (edit_source.strip(), edit_target.strip())
                    _save_vocab_entries(entries)
                    st.success("Entrada atualizada.")
        else:
            st.caption("Selecione uma entrada para editar.")

source_mode = st.radio(
    "Origem da transcricao consolidada",
    options=["Selecionar arquivo (Browse)"],
    index=0,
    horizontal=True,
)

uploaded_transcript = st.file_uploader(
    "Selecione o arquivo transcricao_completa.txt",
    type=["txt"],
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
    if not uploaded_transcript:
        st.error("Selecione um arquivo transcricao_completa.txt.")
    else:
        safe_name = _slugify(Path(uploaded_transcript.name).stem)
        manual_session_dir = (
            BASE_OUTPUT
            / "transcripts"
            / "manual_sessions"
            / f"manual_session_{safe_name}_{int(time.time())}"
        )
        manual_session_dir.mkdir(parents=True, exist_ok=True)
        target_path = manual_session_dir / f"transcricao_completa_{safe_name}.txt"
        target_path.write_bytes(uploaded_transcript.read())
        with st.spinner("Gerando resumo/ata..."):
            try:
                output_path = run_summary_pipeline(manual_session_dir, meeting_type)
                st.session_state.summary_output = output_path
                st.success(f"Resumo gerado: {output_path.name}")
                st.button(
                    "Abrir pasta da sessao (manual)",
                    on_click=open_folder,
                    args=(manual_session_dir,),
                )
            except Exception as exc:
                st.error(f"Falha ao gerar resumo/ata: {exc}")

if st.session_state.summary_output:
    st.button(
        "Abrir pasta da sessao",
        on_click=open_folder,
        args=(st.session_state.summary_output.parent,),
    )

