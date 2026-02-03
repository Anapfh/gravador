import whisperx
device = "cpu"
audio = whisperx.load_audio("audio.wav")
model = whisperx.load_model("large-v2", device, compute_type="float32")
result = model.transcribe(audio, batch_size=16)
# Align
model_a, metadata = whisperx.load_align_model(language_code="pt", device=device)
result = whisperx.align(result["segments"], model_a, metadata, audio, device, return_char_alignments=False)
# Diarize
diarize_model = whisperx.DiarizationPipeline(use_auth_token=HF_TOKEN, device=device)
diarize_segments = diarize_model(audio)
result = whisperx.assign_word_speakers(diarize_segments, result)
# Output: result com 'speaker': 'SPEAKER_00'
