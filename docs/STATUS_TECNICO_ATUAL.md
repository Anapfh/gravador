# STATUS_TECNICO_ATUAL

> **Projeto:** Gravador + Transcrição + (Diarização opcional)
> **Data:** 2026-01-30
> **Responsável:** Ana Paula Horta
> **Objetivo deste documento:** Congelar o estado técnico real do projeto para permitir retomada segura, evitar retrabalho e apoiar decisões de escopo.

---

## 1. Visão Executiva

* O projeto **funciona parcialmente**: captura de áudio + Whisper (transcrição) é viável e entrega valor.
* A **diarização com pyannote** executa, mas é **cara, lenta e frágil** no stack atual (CPU/WSL).
* Os principais bloqueios **não são bugs**, e sim **incompatibilidades estruturais e custo computacional**.
* Decisão implícita até aqui: **diarização NÃO é fase 1** do produto.

Status resumido:

* 🟢 Whisper (transcrição): **Aprovado**
* 🟡 Diarização (pyannote): **Experimental / Opcional**
* 🔴 Ambiente único para tudo: **Reprovado**

---

## 2. Ambiente Atual (Congelado)

### Sistema

* OS: Ubuntu 22.04 via WSL2
* Execução: CPU
* Memória: OK
* Disco: OK

### Python

* Versão: 3.10
* Ambientes:

  * `venv_diarization` (ativo para testes de diarização)

### Bibliotecas Relevantes

* torch: 2.2.2
* torchaudio: 2.2.2
* pyannote.audio: 3.1.1
* pytorch-lightning: 2.x
* lightning-fabric: 2.2.5
* whisper: funcional em outro venv

⚠️ Observação crítica:
Modelos de diarização usados foram treinados com **torch 1.x** e **pyannote 0.x**.

---

## 3. O Que Funciona

### ✅ Funcional

* Download e autenticação no HuggingFace
* Carregamento do pipeline `pyannote/speaker-diarization`
* Execução do pipeline até a fase de embeddings
* Whisper (transcrição) funciona bem em isolamento

### ⏱️ Comportamento Esperado (mas custoso)

* Carregamento inicial do pipeline: ~90s
* Diarização CPU para áudio longo (30–60min): **30–90 minutos**

---

## 4. O Que NÃO Funciona (ou Não Vale a Pena Agora)

### ❌ Não Funcional / Não Recomendado

* Diarização + Whisper no mesmo venv
* Atualizar torch para versões novas esperando compatibilidade retroativa
* Depender de pip install incremental para “consertar” arquitetura
* Processar arquivos longos (.m4a) sem chunking explícito

### ❌ Riscos Técnicos Confirmados

* Travamentos longos sem feedback
* Incompatibilidade silenciosa de modelos
* Alto tempo de CPU sem ganho proporcional de valor

---

## 5. Causas Raiz Identificadas

1. **Mismatch de versões** (modelo antigo × runtime moderno)
2. **Arquitetura monolítica** (tudo no mesmo ambiente)
3. **Escopo avançado cedo demais** (diarização antes do produto base)
4. **Processamento pesado em CPU**

---

## 6. Decisões Tomadas Até Aqui

* ✔️ Separar ambientes por domínio (Whisper ≠ Diarização)
* ✔️ Documentação antes de mais código
* ✔️ Diminuição de escopo para preservar entrega
* ✔️ Diarização passa a ser **feature opcional**

---

## 7. Próximas Decisões em Aberto

* [ ] Whisper como produto principal (transcrição + resumo)
* [ ] Diarização como módulo isolado (sim/não)
* [ ] Uso de casos reais para validar valor do speaker
* [ ] Eventual migração para GPU ou serviço externo

---

## 8. Critério de Alerta de Estouro de Contexto

Se qualquer um ocorrer:

* repetição de decisões
* reinstalação cega de dependências
* perda de rastreabilidade

➡️ **Parar código e atualizar documentação imediatamente**.

---

## 9. Referência Cruzada

* BASELINE_PROJETOS_TECNICOS.md
* CONTEXT_HANDOFF.md
* Logs do projeto (stdout)

---

**Documento vivo.** Atualizar a cada mudança estrutural relevante.

---

## 10. Atualizacao 2026-02-03 (Windows / Fase 1-3)

Resumo:
- CLI continuo com chunking, pause/resume e transcricao consolidada.
- Streamlit com UX atualizado (status, tempo, pausa/retomar por arquivos).
- Pipeline governado de resumo/ata com refinadores e preambulos em memoria.
- Preambulos ampliados e catalogados em docs/PREAMBLES.md.
- README e roadmap atualizados.

Proxima fase (pendente final):
- Pausa/retomar com "gap zero" (exige ajuste no core de gravacao).

Futuro:
- Fase 6: automacao pos-reuniao.
- Fase 7: diarizacao real.
