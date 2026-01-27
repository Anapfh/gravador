# CONTEXT_HANDOFF.md
## Protocolo Oficial de Continuidade de Contexto

Este documento define como o projeto **Gravador Transcritor Local**
deve ser retomado em novos contextos (novos prompts, novas sessões ou novos colaboradores),
sem perda de histórico técnico ou decisões arquiteturais.

---

## 📌 Estado Consolidado do Projeto

### Arquitetura
- Interface principal via **Streamlit**
- Execução **declarativa** (sem main(), sem blocos CLI)
- Gravação via:
  - `core/recorder.py` → CLI (inalterado)
  - `core/recorder_streamlit.py` → UI (não bloqueante)

### Funcionalidades estáveis
- Gravação de áudio local
- Transcrição local via Whisper (faster-whisper)
- Configuração via `config.toml`
- Logs estruturados

---

## 🧭 Etapas do Projeto

### Etapa 1 — Bundle Canônico RAW (em andamento)
- Geração de:
  - áudio bruto
  - transcrição bruta
- Versionamento automático
- Não sobrescrever artefatos

### Etapa 2 — Refiners (planejada)
- Limpeza de oralidade
- Remoção de repetições
- Segmentação semântica

### Etapa 3 — Summarizers (planejada)
- Resumo estruturado
- Atas / minutes
- Integração opcional com Ollama

---

## 🚫 O que NÃO deve ser refeito

- Arquitetura de gravação
- Core CLI
- Integração Whisper
- Separação UI x Core
- Decisões já documentadas em `docs/DECISIONS.md`

---

## 🔁 Protocolo de Troca de Contexto

Sempre que houver:
- troca de prompt
- sessão interrompida
- necessidade de retomada futura

Deve-se:
1. Atualizar `docs/STATUS_ATUAL.md`
2. Registrar decisões em `docs/DECISIONS.md`
3. Garantir que este arquivo (`CONTEXT_HANDOFF.md`) reflita o estado atual

---

## 🎯 Texto Padrão para Retomada (Prompt)

```text
Projeto: Gravador Transcritor Local
Etapa atual: Etapa 1 — Bundle Canônico RAW
Estado: app.py consolidado, UI Streamlit declarativa,
recorder_streamlit ativo, CLI preservado.
Objetivo: continuar sem refatorar o que já está estável.
