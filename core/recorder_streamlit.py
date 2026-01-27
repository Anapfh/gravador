import threading
import logging
from pathlib import Path
from core.recorder import record_until_stop

logger = logging.getLogger(__name__)


class StreamlitRecorder:
    """
    Controlador de gravação para Streamlit.
    O core decide o nome final do arquivo.
    """

    def __init__(self, output_dir: Path, base_name: str):
        self.output_dir = output_dir
        self.base_name = base_name
        self.final_audio_path: Path | None = None

        self._thread = None
        self._stop_event = threading.Event()

    def _run(self):
        self.final_audio_path = record_until_stop(
            self.output_dir,
            self.base_name,
            self._stop_event,
        )
        logger.info("Gravação concluída | path=%s", self.final_audio_path)

    def start(self):
        if self.is_running():
            logger.warning("Gravação já em andamento")
            return

        self._stop_event.clear()

        self._thread = threading.Thread(
            target=self._run,
            daemon=True,
        )
        self._thread.start()

        logger.info("Thread de gravação iniciada")

    def stop(self):
        if not self.is_running():
            logger.warning("Stop chamado sem gravação ativa")
            return

        logger.info("Finalizando gravação via Streamlit")
        self._stop_event.set()
        self._thread.join(timeout=10)

    def is_running(self) -> bool:
        return self._thread is not None and self._thread.is_alive()
