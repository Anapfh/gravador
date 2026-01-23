# Gravador e Transcritor de Áudio Local (CLI)

Ferramenta local (CLI / desktop) para **gravação de áudio com qualidade** e **transcrição offline** usando Whisper.

Projeto focado em:
- confiabilidade
- previsibilidade
- uso local
- arquitetura simples e extensível (CLI → Streamlit)

---

## 🎯 Objetivo

Permitir que o usuário:
1. Grave áudio localmente com microfones modernos (Windows, AGC)
2. Gere arquivos WAV compatíveis com Whisper
3. Transcreva o áudio localmente, sem depender de serviços externos

---

## 🧱 Arquitetura

CLI (cli_local.py)
├── core/recorder.py → captura de áudio (SoundDevice)
├── core/whisper_core.py → transcrição (faster-whisper)
├── refiners/ → pós-processamento determinístico
└── summarizers/ → sumarização (opcional)


---

## 🎙️ Captura de áudio

- Backend: `sounddevice`
- Taxa: 16 kHz, mono
- Compatível com:
  - Intel Smart Sound
  - Realtek
  - Microfones com AGC

### Decisão importante
RMS **não é usado como critério de validação**.  
A validação é feita por **variação do sinal**, conforme documentado em `docs/`.

---

## 🧠 Transcrição

- Backend: `faster-whisper`
- Modelo padrão: `small`
- Execução: **offline**
- Retorno estruturado (`dict`), texto tratado no CLI

> Observação (Windows): o aviso de *symlink* do HuggingFace é esperado e não impacta o funcionamento.

---

## ▶️ Como usar

### 1. Gravar áudio
```bash
python cli_local.py gravar
2. Transcrever áudio
python cli_local.py transcrever -a output/audio/arquivo.wav
📁 Estrutura de diretórios
output/
 ├── audio/        → arquivos WAV
 └── transcripts/  → transcrições TXT
📚 Documentação técnica
Consulte o diretório docs/ para:

decisões arquiteturais (ADR)

lições aprendidas

postmortem técnico da pipeline de transcrição

🚧 Próximos passos planejados
Interface Streamlit

Ajustes finos de UX

Empacotamento desktop (opcional)




