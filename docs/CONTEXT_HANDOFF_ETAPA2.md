# CONTEXT_HANDOFF — Etapa 2 | Transcrição (Refinamentos)

## 📌 Objetivo deste documento

Este documento formaliza a **troca de contexto** entre:

- **Etapa 1 — Captura RAW + Estabilização**
- **Etapa 2 — Transcrição (Refinamentos)**

Seu objetivo é:
- Garantir continuidade sem perda de histórico
- Evitar reabertura de decisões já consolidadas
- Definir claramente o escopo permitido da Etapa 2
- Servir como contrato técnico para evolução do projeto

Este documento **não substitui** postmortems, changelogs ou decisões técnicas — ele os referencia.

---

## ✅ Contexto anterior (encerrado)

### Etapa 1 — Bundle Canônico RAW
**STATUS: CONCLUÍDA E MERGEADA**

A Etapa 1 foi oficialmente encerrada após:
- Estabilização da captura de áudio local
- Padronização e validação do áudio RAW
- Identificação e correção de falha estrutural de transcrição prematura
- Implementação de transcrição manual e controlada
- Correção de crash da UI para áudios não-WAV
- Consolidação de documentação técnica e lições aprendidas
- Merge de todos os PRs relevantes no branch principal

O pipeline até este ponto é considerado **estável, auditável e confiável**.

---

## 🎧 Estado herdado do sistema

Ao iniciar a Etapa 2, o sistema apresenta:

- Captura RAW funcional e desacoplada
- Transcrição manual acionada explicitamente via UI
- Suporte a múltiplos formatos de áudio (`wav`, `mp3`, `m4a`, `flac`, `ogg`)
- Exportação de transcrição em `.txt` e `.json`
- UI resiliente a transcrições longas
- Logs confiáveis para diagnóstico

Essas características **não devem ser alteradas** nesta etapa.

---

## 🎯 Escopo oficial da Etapa 2 — Transcrição (Refinamentos)

A Etapa 2 é dedicada exclusivamente a **melhorias na qualidade, utilidade e apresentação da transcrição**, sem impacto na captura de áudio.

Entram no escopo:

### 🧠 Qualidade de Transcrição
- Normalização de texto (pontuação, caixa, espaçamento)
- Redução de repetições e vícios de linguagem
- Tratamento de transcrição bilíngue (pt/en)
- Pós-processamento baseado em heurísticas
- Avaliação de confiança do texto transcrito

### 🕒 Estrutura e Enriquecimento
- Segmentação de transcrição
- Inclusão opcional de timestamps
- Geração de formatos adicionais (ex: SRT)
- JSON enriquecido com metadados úteis

### 🖥️ UX e Operação
- Melhor feedback visual de progresso
- Histórico de transcrições
- Seleção de modelos ou perfis de transcrição
- Opções de exportação e visualização

---

## 🚫 Fora de escopo (decisões congeladas)

As seguintes áreas **não fazem parte da Etapa 2** e não devem ser modificadas:

- Captura de áudio RAW
- StreamlitRecorder
- Configurações de microfone / AGC
- Pausar / retomar gravação
- Estrutura do Bundle RAW
- Gate entre Etapa 1 e Etapa 2

Qualquer mudança nessas áreas exige:
- Novo contexto
- Nova etapa formal
- Novo postmortem (se aplicável)

---

## 🧠 Decisões herdadas (não reabrir)

Permanecem válidas e congeladas:

- Transcrição nunca ocorre automaticamente
- Toda transcrição é uma ação explícita do usuário
- Duração de áudio é calculada apenas quando tecnicamente aplicável
- UI não deve induzir interpretações incorretas
- Logs são parte essencial do pipeline

---

## 📄 Documentos de referência

Para entendimento completo do histórico e das decisões:

- `CONTEXT_HANDOFF.md` (Etapa 1)
- `POSTMORTEM_TRANSCRICAO.md`
- `LESSONS_LEARNED_PIPELINE.md`
- `DECISIONS.md`
- `STATUS_ATUAL.md`
- `changelog.txt`

Este documento **consolida**, mas não substitui, os anteriores.

---

## ▶️ Próximo passo esperado

A Etapa 2 deve iniciar com:
- definição clara de objetivos de refinamento
- criação de issues específicas
- evolução incremental, com PRs pequenos e rastreáveis

Ao final da Etapa 2, será esperado:
- melhoria perceptível da qualidade da transcrição
- preservação total da estabilidade do pipeline
- documentação das novas decisões e aprendizados

---

## 🧾 Nota final

Este documento marca oficialmente o início da **Etapa 2 — Transcrição (Refinamentos)**.

A continuidade do projeto deve respeitar o contexto aqui descrito para evitar regressões, retrabalho e perda de histórico técnico.

