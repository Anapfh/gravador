# Gravador e Transcritor de Audio Local (CLI/Streamlit)

Ferramenta local para gravacao de audio e transcricao offline usando faster-whisper.

Projeto focado em:
- confiabilidade
- previsibilidade
- uso local
- arquitetura simples e extensivel (CLI -> Streamlit)

---

## Status do Projeto

- Fase 1 concluida (gravacao e transcricao).
- Fase 2.1/2.2/2.3 concluidas (chunking, pause/resume, transcricao consolidada).
- Pipeline de resumo/ata governado e Streamlit com UX atualizado.

---

## Objetivo

Permitir que o usuario:
1. Grave audio localmente com microfones modernos (Windows, AGC)
2. Gere arquivos WAV compativeis com Whisper
3. Transcreva o audio localmente, sem depender de servicos externos

---

## Arquitetura

- CLI (core/cli/mic_cli.py) para gravacao e transcricao
- Streamlit (app.py) para UI
- Refiners deterministas (refiners/)
- Summarizers governados (summarizers/ + core/summarizers/pipeline.py)

---

## Como usar

### 1) Gravar/transcrever via CLI (continuo)
```bash
python core/cli/mic_cli.py --chunk-minutes 10
```

Saida:
```
output/session_YYYY-MM-DD_HH-MM/
  audio_0001.wav
  transcricao_0001.txt
  transcricao_completa.txt
```

### 2) Rodar o Streamlit
```bash
streamlit run app.py
```

### 3) Resumo/Ata (pipeline governado)
No Streamlit, selecione a sessao e o tipo de reuniao. O pipeline:
- aplica refinadores deterministas
- injeta preambulo em memoria
- gera o arquivo final (resumo/ata)

---

## Documentacao
Consulte `docs/` para:
- ADRs e decisoes
- lessons learned
- postmortem
- catalogo de preambulos (`docs/PREAMBLES.md`)

