# Gravador e Transcritor de Ãudio Local (CLI)

Ferramenta local (CLI / desktop) para **gravaÃ§Ã£o de Ã¡udio com qualidade** e **transcriÃ§Ã£o offline** usando Whisper.

Projeto focado em:
- confiabilidade
- previsibilidade
- uso local
- arquitetura simples e extensÃ­vel (CLI â†’ Streamlit)

---

## Status do Projeto

Fase 1 concluída (gravação e transcrição).

---

## ðŸŽ¯ Objetivo

Permitir que o usuÃ¡rio:
1. Grave Ã¡udio localmente com microfones modernos (Windows, AGC)
2. Gere arquivos WAV compatÃ­veis com Whisper
3. Transcreva o Ã¡udio localmente, sem depender de serviÃ§os externos

---

## ðŸ§± Arquitetura

CLI (cli_local.py)
â”œâ”€â”€ core/recorder.py â†’ captura de Ã¡udio (SoundDevice)
â”œâ”€â”€ core/whisper_core.py â†’ transcriÃ§Ã£o (faster-whisper)
â”œâ”€â”€ refiners/ â†’ pÃ³s-processamento determinÃ­stico
â””â”€â”€ summarizers/ â†’ sumarizaÃ§Ã£o (opcional)


---

## ðŸŽ™ï¸ Captura de Ã¡udio

- Backend: `sounddevice`
- Taxa: 16 kHz, mono
- CompatÃ­vel com:
  - Intel Smart Sound
  - Realtek
  - Microfones com AGC

### DecisÃ£o importante
RMS **nÃ£o Ã© usado como critÃ©rio de validaÃ§Ã£o**.  
A validaÃ§Ã£o Ã© feita por **variaÃ§Ã£o do sinal**, conforme documentado em `docs/`.

---

## ðŸ§  TranscriÃ§Ã£o

- Backend: `faster-whisper`
- Modelo padrÃ£o: `small`
- ExecuÃ§Ã£o: **offline**
- Retorno estruturado (`dict`), texto tratado no CLI

> ObservaÃ§Ã£o (Windows): o aviso de *symlink* do HuggingFace Ã© esperado e nÃ£o impacta o funcionamento.

---

## â–¶ï¸ Como usar

### 1. Gravar Ã¡udio
```bash
python cli_local.py gravar
2. Transcrever Ã¡udio
python cli_local.py transcrever -a output/audio/arquivo.wav
ðŸ“ Estrutura de diretÃ³rios
output/
 â”œâ”€â”€ audio/        â†’ arquivos WAV
 â””â”€â”€ transcripts/  â†’ transcriÃ§Ãµes TXT
ðŸ“š DocumentaÃ§Ã£o tÃ©cnica
Consulte o diretÃ³rio docs/ para:

decisÃµes arquiteturais (ADR)

liÃ§Ãµes aprendidas

postmortem tÃ©cnico da pipeline de transcriÃ§Ã£o

ðŸš§ PrÃ³ximos passos planejados
Interface Streamlit

Ajustes finos de UX

Empacotamento desktop (opcional)





