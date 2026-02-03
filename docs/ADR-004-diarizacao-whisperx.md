# ADR-004: Diarização via WhisperX (Pyannote + Whisper Integrado)

## Status: Proposta → Aprovada (2026-01-30)

## Contexto
POC pyannote nativo (`pyannote_poc.py`): 
- Tempo: 30-90min CPU/reunião longa [STATUS_TECNICO_ATUAL.md].
- Funciona (segments.json), mas sem transcrição → Integração manual cara.
- Problema: Perda palavras + 1 speaker dominante (VAD agressivo) [DECISION_DIARIZATION_POC.md].

Alternativas:
1. Pyannote full + Whisper manual: Lento, 2 venvs, chunking custom.
2. Whisper medium/large: Rápido, mas sem speakers.
3. **WhisperX**: Pyannote VAD/diarize + Whisper align + speakers/timestamps.

## Decisão
Adotar **WhisperX** (`large-v2` PT-BR):
- Ganho: Speakers SPEAKER_XX + 90% cobertura + timestamps + 20min CPU.
- Tradeoff: +1 dep (whisperx), mas single-pipeline.
- Rejeitado: Pyannote nativo (lento, sem ASR).

## Impacto
- `transcribefile.py`: +`diarize=True` flag → JSON com speakers/text.
- Novo `requirements_whisperx.txt`.
- Teste: "Reunião com Bezzi_diar.wav" → WER <15%.
- Gate Etapa2 preservado [POSTMORTEM_TRANSCRICAO.md].

## Follow-up
- Commit: `feat(diarization): WhisperX integration`.
- Update: ISSUES.md, LESSONS_LEARNED_PIPELINE.md.
