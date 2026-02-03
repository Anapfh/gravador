"""
POC de diarização usando pyannote.audio (SEM transcrição).

Ambiente:
- venv_diarization
- pyannote.audio == 3.1.1
- numpy < 2.0
- huggingface_hub == 0.19.4

Saída:
- output/diarization_poc/segments.json
"""

from pathlib import Path
import json
import logging
import os
import sys
import time

from pyannote.audio import Pipeline

# --------------------------------------------------
# LOGGING
# --------------------------------------------------
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s",
)
logger = logging.getLogger(__name__)

# --------------------------------------------------
# CONFIG
# --------------------------------------------------
AUDIO_FILE = Path("output/audio/Reunião com Bezzi_diar.wav")
OUTPUT_DIR = Path("output/diarization_poc")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

MODEL_ID = "pyannote/speaker-diarization"
HUGGINGFACE_TOKEN = os.environ.get("HUGGINGFACE_TOKEN")

# --------------------------------------------------
# VALIDACOES
# --------------------------------------------------
if not AUDIO_FILE.exists():
    logger.error("Arquivo de áudio não encontrado: %s", AUDIO_FILE)
    sys.exit(1)

if not HUGGINGFACE_TOKEN:
    logger.error("Variável HUGGINGFACE_TOKEN não definida")
    sys.exit(1)

# --------------------------------------------------
# LOAD PIPELINE
# --------------------------------------------------
logger.info("Carregando pipeline de diarização: %s", MODEL_ID)
start = time.time()

pipeline = Pipeline.from_pretrained(
    MODEL_ID,
    use_auth_token=HUGGINGFACE_TOKEN,
)

logger.info("Pipeline carregado em %.1fs", time.time() - start)

# --------------------------------------------------
# RUN DIARIZATION
# --------------------------------------------------
logger.info("Iniciando diarização do áudio")
start = time.time()

diarization = pipeline(str(AUDIO_FILE))

logger.info("Diarização concluída em %.1fs", time.time() - start)

# --------------------------------------------------
# EXTRAI SEGMENTOS
# --------------------------------------------------
segments = []

for turn, _, speaker in diarization.itertracks(yield_label=True):
    duration = turn.end - turn.start
    if duration < 1.0:
        continue

    segments.append(
        {
            "speaker": speaker,
            "start": round(turn.start, 2),
            "end": round(turn.end, 2),
        }
    )

if not segments:
    logger.warning("Nenhum segmento válido detectado")
    sys.exit(0)

logger.info(
    "Falantes detectados: %s",
    sorted(set(s["speaker"] for s in segments)),
)
logger.info("Total de segmentos: %d", len(segments))

# --------------------------------------------------
# OUTPUT
# --------------------------------------------------
output_file = OUTPUT_DIR / "segments.json"
output_file.write_text(
    json.dumps(segments, ensure_ascii=False, indent=2),
    encoding="utf-8",
)

logger.info("Segmentos salvos em %s", output_file)
logger.info("POC de diarização concluída com sucesso")
