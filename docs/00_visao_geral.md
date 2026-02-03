# Visao geral

Este projeto eh um gravador de audio via microfone com transcricao local usando faster-whisper em CPU. A Fase 1 (gravacao + transcricao) esta concluida e validada no Windows 64-bit com Python 3.11.

Principais caracteristicas:
1. Captura de audio do microfone via SpeechRecognition + PyAudio.
2. Transcricao local via faster-whisper + ctranslate2 em CPU (int8).
3. Saida em texto simples, com encoding explicito para preservar acentuacao.
4. Transcricao consolidada por sessao (modo continuo).
5. Pipeline governado de resumo/ata com refinadores deterministas.

Estrutura relevante:
1. `core/cli/mic_cli.py` executa gravacao, salva WAV temporario e transcreve.
2. `core/whisper_core.py` configura o backend faster-whisper com `device=cpu` e `compute_type=int8`.
3. `output/transcricao.txt` eh o arquivo final da Fase 1.

Escopo atual:
1. Fase 1 concluida e estavel.
2. Fase 2 (chunking/pause/resume) concluida.
3. Pipeline de resumo/ata integrado ao Streamlit.
4. Diarizacao permanece apenas no roadmap.

Requisitos resumidos:
1. Windows 64-bit.
2. Python 3.11.
3. venv `.venv311_ok` ativo.
4. PyAudio instalado via wheel compativel com cp311 e win_amd64.

