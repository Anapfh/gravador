"""
recorder.py

Módulo canônico de gravação de áudio do projeto.

Responsabilidades:
- Capturar áudio localmente no Windows
- Compatível com microfones modernos (Intel Smart Sound / AGC)
- Gerar WAV mono 16kHz (compatível com Whisper)
- Não aplicar regras inválidas baseadas em RMS bruto

Decisão técnica:
- RMS NÃO é critério de bloqueio
- Validação baseada em variação do sinal (std)

Fontes:
- docs/DECISIONS.md
- docs/POSTMORTEM_TRANSCRICAO.md
- docs/LESSONS_LEARNED_PIPELINE_TRANSCRICAO.md
"""

from __future__ import annotations

import logging
import re
import threading
import time
from datetime import datetime
from pathlib import Path
from typing import Optional

import numpy as np
import sounddevice as sd
import soundfile as sf

logger = logging.getLogger(__name__)

# ---------------------------------------------------------
# Parâmetros de áudio (Whisper-friendly)
# ---------------------------------------------------------
SAMPLE_RATE = 16000
CHANNELS = 1
DTYPE = "float32"

MIN_SECONDS = 1.0
TARGET_PEAK = 0.9
MIN_STD = 1e-5  # variação mínima para considerar áudio válido


# ---------------------------------------------------------
# Utilidades
# ---------------------------------------------------------
def normalize_filename(name: str) -> str:
    name = name.strip().lower()
    name = re.sub(r"\s+", "_", name)
    name = re.sub(r"[^a-z0-9_\-]", "", name)
    return name or "gravacao"


def select_input_device() -> int:
    default_input = sd.default.device[0]
    if default_input is not None and default_input >= 0:
        return default_input

    for idx, dev in enumerate(sd.query_devices()):
        if dev.get("max_input_channels", 0) >= CHANNELS:
            return idx

    raise RuntimeError("Nenhum dispositivo de entrada encontrado")


def normalize_audio(audio: np.ndarray) -> np.ndarray:
    peak = float(np.max(np.abs(audio)))
    if peak <= 0:
        return audio
    return audio / peak * TARGET_PEAK


def compute_rms(audio: np.ndarray) -> float:
    if audio.size == 0:
        return 0.0
    return float(np.sqrt(np.mean(np.square(audio))))


def has_signal_variation(audio: np.ndarray) -> bool:
    return audio.size > 0 and float(np.std(audio)) > MIN_STD


# ---------------------------------------------------------
# API principal
# ---------------------------------------------------------
def record_until_stop(
    output_dir: Path,
    base_name: str,
    stop_event: Optional[threading.Event] = None,
    pause_event: Optional[threading.Event] = None,
    show_timer: bool = True,
) -> Path:
    """
    Grava áudio até o usuário encerrar (ENTER) ou stop_event.

    Retorna:
        Path do arquivo WAV gerado.

    Lança:
        RuntimeError em caso de áudio inválido.
    """

    output_dir.mkdir(parents=True, exist_ok=True)

    safe_name = normalize_filename(base_name)
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    output_path = output_dir / f"{safe_name}_{timestamp}.wav"

    device = select_input_device()
    device_info = sd.query_devices(device)
    logger.info("Microfone selecionado: %s", device_info["name"])

    frames: list[np.ndarray] = []
    internal_stop = stop_event or threading.Event()

    def callback(indata, _frames, _time, status):
        if status:
            logger.warning("Status de captura: %s", status)
        if pause_event is not None and pause_event.is_set():
            return
        frames.append(indata.copy())

    def timer(start_time: float):
        while not internal_stop.is_set():
            if pause_event is not None and pause_event.is_set():
                time.sleep(0.2)
                continue
            elapsed = int(time.time() - start_time)
            print(
                f"\r🎙️ Gravando... {elapsed//60:02d}:{elapsed%60:02d}",
                end="",
                flush=True,
            )
            time.sleep(1)

    print(f"🎛️ Microfone: {device_info['name']}")
    print("🎙️ Gravando... pressione ENTER para finalizar\n")

    start_time = time.time()

    if show_timer:
        threading.Thread(target=timer, args=(start_time,), daemon=True).start()

    with sd.InputStream(
        samplerate=SAMPLE_RATE,
        channels=CHANNELS,
        dtype=DTYPE,
        device=device,
        callback=callback,
    ):
        if stop_event is None:
            input()
            internal_stop.set()
        else:
            stop_event.wait()

    print()

    audio = np.concatenate(frames, axis=0) if frames else np.array([], dtype=DTYPE)
    duration = audio.shape[0] / SAMPLE_RATE

    if duration < MIN_SECONDS:
        raise RuntimeError("Áudio muito curto para transcrição")

    audio = normalize_audio(audio)

    rms = compute_rms(audio)
    std = float(np.std(audio))

    logger.info(
        "Gravação encerrada | duração=%.2fs | rms=%.6f | std=%.6f",
        duration,
        rms,
        std,
    )

    print(f"🔊 RMS: {rms:.6f} | Δ sinal (std): {std:.6f}")

    if not has_signal_variation(audio):
        raise RuntimeError("Áudio inválido (sem variação detectável)")

    sf.write(output_path, audio, SAMPLE_RATE)
    logger.info("Arquivo salvo: %s", output_path)

    return output_path


# ---------------------------------------------------------
# CHANGELOG
# ---------------------------------------------------------
# 2026-01-23
# - Removido RMS como critério de bloqueio
# - Validação baseada em variação de sinal (std)
# - Normalização obrigatória antes da validação
# - Logs enriquecidos para diagnóstico
# - Compatibilidade confirmada com Intel Smart Sound
