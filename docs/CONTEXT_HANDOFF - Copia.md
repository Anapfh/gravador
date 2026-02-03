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
### Funcionalidades deliberadamente fora do escopo atual

- Controles de Pausar / Retomar gravação via UI (Issue 2)
  - Botões removidos temporariamente do Streamlit
  - Motivo: evitar UX enganosa e WAV inconsistente
  - Implementação planejada após fechamento do Bundle RAW
# CONTEXT_HANDOFF — Projeto Gravador / Transcritor Local

## 📌 Objetivo deste documento
Este documento registra o **handoff formal de contexto** após o fechamento da **Etapa 1 — Bundle Canônico RAW**.

Ele existe para:
- Evitar reabertura de decisões já tomadas
- Permitir continuidade do projeto sem reanálise histórica
- Servir como contrato entre etapas do pipeline

Este arquivo **não é log**, **não é diário** e **não é roadmap**.

---

## ✅ Estado atual do projeto (congelado)

### Etapa 1 — Captura RAW
**STATUS: CONCLUÍDA**

A Etapa 1 foi oficialmente concluída com:
- Captura de áudio local estabilizada
- Qualidade de entrada validada (sem AGC e sem aprimoramentos)
- Geração de WAV consistente e reprocessável
- Erros anteriores de transcrição prematura diagnosticados e documentados
- Histórico versionado e auditável no GitHub

O pipeline até este ponto é considerado **estável e confiável**.

---

## 📦 Definição oficial — Bundle Canônico RAW

Um Bundle Canônico RAW representa uma sessão de gravação **pronta para consumo** por etapas posteriores.

### Artefatos obrigatórios
- Arquivo de áudio WAV (mono, 16kHz, PCM)
- Metadados associados (raw.meta.json ou equivalente lógico)
- Logs de geração (quando aplicável)

### Invariantes
- O áudio RAW **não sofre pós-processamento**
- O arquivo RAW **não é sobrescrito**
- Cada sessão gera um bundle independente
- O RAW pode ser reprocessado indefinidamente

---

## 🚦 Gate entre Etapas (decisão arquitetural)

### Regra não negociável
> **Nenhuma transcrição pode ocorrer diretamente a partir do WAV.**

A transcrição (Etapa 2) **só é permitida** quando:
- O Bundle RAW está completo
- O status do bundle é explicitamente considerado **READY**

Esta regra existe para evitar:
- Transcrição parcial
- Perda de contexto
- Inconsistências históricas
- Regressão do erro documentado no postmortem

---

## 🧠 Decisões técnicas congeladas

As decisões abaixo **não devem ser reabertas**:

- Desativação de AGC e aprimoramentos do driver de áudio
- Conversão e padronização para mono / 16kHz no pipeline
- Separação explícita entre Etapa 1 (captura) e Etapa 2 (transcrição)
- Proibição de transcrição implícita ou automática sem gate
- Uso de documentação formal (postmortem, lessons learned)

Essas decisões já estão refletidas no código e na documentação.

---

## 🎛️ Funcionalidades deliberadamente fora do escopo atual

As seguintes funcionalidades **não fazem parte da Etapa 1** e **não bloqueiam a entrega**:

- Controles de **Pausar / Retomar** gravação via Streamlit (Issue 2)
  - Botões foram removidos temporariamente da UI
  - Motivo: evitar UX enganosa e geração de WAV inconsistente
  - Implementação prevista apenas após estabilização completa do Bundle RAW

---

## 📄 Documentos de referência (fonte de verdade)

Para entendimento completo do histórico e decisões, consultar:

- `POSTMORTEM_TRANSCRICAO.md`
- `LESSONS_LEARNED_PIPELINE.md`
- `DECISIONS.md`
- `STATUS_ATUAL.md`
- `DOCUMENT_MAP.md`

Este `CONTEXT_HANDOFF.md` **não substitui** esses documentos; ele os consolida.

---

## ▶️ Próxima etapa esperada

### Etapa 2 — Transcrição
A próxima etapa do projeto deverá:
- Consumir exclusivamente Bundles RAW válidos
- Respeitar o gate definido
- Tratar transcrição como processo determinístico e reexecutável
- Manter rastreabilidade entre RAW → texto → refinamentos

Qualquer avanço além disso **deve partir deste contexto**.

---

## 🧾 Nota final
Este documento marca o encerramento consciente da Etapa 1.

Reabrir decisões aqui descritas só deve ocorrer mediante:
- novo postmortem
- nova etapa formal
- justificativa técnica explícita

# 🔄 CONTEXT_HANDOFF.md  
## Mudança de Contexto – Encerramento Técnico e Preparação para Novo Ciclo

---

## 1. OBJETIVO DESTE DOCUMENTO

Este documento formaliza a **mudança de contexto** do trabalho atual, garantindo que:

- Nenhuma decisão técnica seja perdida
- As lições aprendidas fiquem registradas
- O próximo contexto comece de forma limpa, consciente e estruturada

---

## 2. CONTEXTO ENCERRADO

### Projeto / Ciclo
- Pipeline de gravação, transcrição, refino e POC de diarização
- Exploração técnica envolvendo:
  - Streamlit
  - Whisper / faster-whisper
  - pyannote.audio
  - Ambientes Python isolados (venv)
  - Integração com Hugging Face

### Status
✔ Funcional para gravação e transcrição  
✔ POC de diarização tecnicamente validada (com restrições de ambiente)  
✔ Decisões arquiteturais documentadas  
✔ Baseline técnico consolidado  

---

## 3. PRINCIPAIS LIÇÕES APRENDIDAS (SÍNTESE)

As lições completas foram consolidadas em:

📄 **BASELINE_PROJETOS_TECNICOS.md**

Resumo executivo:

- Ambiente é parte do código
- pip não resolve compatibilidade, apenas executa ordens
- Ambientes não se “consertam”, são recriados
- Um ambiente = um propósito
- Fixar versões não é opcional
- Warning ignorado vira erro crítico depois
- Tecnologias sensíveis (ML/áudio) exigem isolamento rigoroso

---

## 4. DECISÕES TÉCNICAS IMPORTANTES

- Separação clara de ambientes por domínio
- Não misturar:
  - UI / App
  - Processamento de dados
  - ML pesado (torch, diarização)
- Uso consciente de tokens, modelos gated e dependências sensíveis
- Registro explícito de decisões arquiteturais (ADR)

---

## 5. MOTIVO DA MUDANÇA DE CONTEXTO

O contexto atual atingiu um **ponto natural de encerramento**:

- Complexidade de ambiente controlada
- Conhecimento consolidado
- Risco de desgaste cognitivo ao insistir no mesmo ciclo

A mudança de contexto é **estratégica**, não abandono.

---

## 6. O QUE FICA CONGELADO (NÃO ALTERAR)

- Baseline técnico validado
- Decisões sobre ambientes e dependências
- Estrutura conceitual do pipeline
- Documentação produzida

Qualquer evolução futura deve **partir desse estado**, não refazê-lo.

---

## 7. PRÓXIMO CONTEXTO (ABERTO)

### Estado
🟢 Novo contexto será iniciado **limpo**, com:

- Baseline aplicado desde o início
- Decisões conscientes de stack
- Menos exploração reativa, mais execução guiada

### Regras para o novo contexto
- Aplicar o baseline desde o primeiro comando
- Criar ambientes dedicados desde o início
- Documentar decisões conforme surgirem
- Evitar exploração sem critério

---

## 8. REGRA DE OURO PARA O NOVO CICLO

> **Não repetir erros que já foram pagos com tempo.**

O conhecimento deste projeto agora é **ativo**, não histórico.

---

## 9. STATUS FINAL

✔ Contexto encerrado com sucesso  
✔ Conhecimento preservado  
✔ Base sólida para novos projetos  

---

**Este documento marca oficialmente a transição de contexto.**
