from __future__ import annotations

import logging
import os
from typing import Optional

import numpy as np
import speech_recognition as sr
from faster_whisper import WhisperModel


class MicRecorder:
    def __init__(
        self,
        model: str = "base",
        device: str = "auto",
        compute_type: str = "int8",
        sample_rate: int = 16000,
        energy: int = 300,
        pause: float = 0.8,
        dynamic_energy: bool = False,
        mic_index: Optional[int] = None,
        language: Optional[str] = None,
        download_root: str = "~/.cache/whisper",
    ) -> None:
        if not logging.getLogger().handlers:
            logging.basicConfig(
                level=logging.INFO,
                format="%(asctime)s %(levelname)s %(name)s: %(message)s",
            )

        self.logger = logging.getLogger(__name__)
        self.language = language

        model_root = os.path.expanduser(download_root)
        self.model = WhisperModel(
            model,
            device=device,
            compute_type=compute_type,
            download_root=model_root,
        )

        self.recognizer = sr.Recognizer()
        self.recognizer.energy_threshold = energy
        self.recognizer.pause_threshold = pause
        self.recognizer.dynamic_energy_threshold = dynamic_energy

        self.source = sr.Microphone(sample_rate=sample_rate, device_index=mic_index)
        with self.source:
            self.recognizer.adjust_for_ambient_noise(self.source)

    def record_until_stop(self) -> str:
        self.logger.info("Listening until silence...")
        with self.source as microphone:
            audio = self.recognizer.listen(microphone)
        return self.transcribe_audio(audio.get_raw_data())

    def record_for_duration(self, seconds: float) -> str:
        self.logger.info("Recording for %.2f seconds...", seconds)
        with self.source as microphone:
            audio = self.recognizer.record(microphone, duration=seconds)
        return self.transcribe_audio(audio.get_raw_data())

    def transcribe_audio(self, audio_bytes: bytes) -> str:
        if not audio_bytes:
            return ""

        audio = np.frombuffer(audio_bytes, dtype=np.int16).astype(np.float32) / 32768.0

        kwargs = {}
        if self.language:
            kwargs["language"] = self.language

        segments, _info = self.model.transcribe(audio, **kwargs)
        text = "".join(segment.text for segment in segments).strip()
        return text
