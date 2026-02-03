# CONTEXT_HANDOFF.md

## 1. Objetivo do Documento

Este documento existe para **permitir troca de contexto segura e rápida** em projetos técnicos, evitando perda de histórico, retrabalho e decisões inconsistentes.

Ele deve ser lido **antes de qualquer alteração de código, dependência ou arquitetura**.

---

## 2. Resumo Executivo (TL;DR)

* Projeto envolve **captura de áudio, transcrição (Whisper) e diarização (pyannote)**.
* A complexidade principal não foi código, mas **gestão de ambiente, versões e escopo**.
* O sistema **funcionou parcialmente**, porém a diarização mostrou alto custo computacional e fragilidade.
* Decisão atual: **pausar avanço técnico e documentar baseline** antes de evoluir.

---

## 3. Estado Atual do Projeto

### Funciona

* Ambiente WSL2 ativo
* Ambiente virtual `venv_diarization` criado
* Download e carregamento de modelos HuggingFace funcionando
* Pipeline de diarização carrega corretamente

### Funciona com ressalvas

* Diarização roda, porém:

  * Muito lenta em CPU
  * Sensível a formato de áudio (m4a longo)
  * Alto custo de embeddings

### Não é bug

* Tempo elevado de processamento
* Avisos de incompatibilidade de versões (modelo antigo vs torch novo)

---

## 4. Principais Decisões Técnicas Já Tomadas

* **Não misturar Whisper e Pyannote no mesmo ambiente**
* **Diarização não é fase 1 do produto**
* Pip não resolve arquitetura: versionamento fechado é obrigatório
* Torch novo pode rodar modelos antigos, mas com risco

---

## 5. Problemas Encontrados (Raiz)

* Dependências com expectativas de versões diferentes
* Modelos treinados em torch antigo
* Tentativa de resolver tudo em um único pipeline
* Falta inicial de baseline e handoff

---

## 6. O Que NÃO Fazer ao Retomar

* Não atualizar dependências sem documentar
* Não rodar diarização longa sem timeout
* Não misturar escopos (captura, transcrição, diarização)
* Não tentar otimizar antes de entregar valor

---

## 7. Próximo Passo Oficial

1. Gerar `STATUS_TECNICO_ATUAL.md`
2. Atualizar `BASELINE_PROJETOS_TECNICOS.md` (v1.1)
3. Só então decidir retomada técnica

---

## 8. Regra de Ouro

> Se parecer que estamos reexplicando coisas, **paramos e atualizamos a documentação**.

---

**Documento criado para ser reutilizável em qualquer projeto técnico.**
