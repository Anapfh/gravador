# Integração com Streamlit

## Objetivo

Este documento registra a decisão e o padrão arquitetural para **reutilizar o Streamlit** como camada de interface do sistema de gravação, transcrição e refinamento textual, **sem comprometer a robustez do pipeline**.

---

## Contexto

Em versões anteriores do projeto, o uso do Streamlit apresentou instabilidade devido a:

* pipeline de transcrição frágil;
* imports inconsistentes;
* refinadores destrutivos que podiam zerar a transcrição;
* mistura de lógica de negócio com lógica de interface.

Após a consolidação do pipeline (core + refiners + orquestrador) e a correção dos fluxos de saída, o projeto atingiu maturidade suficiente para **reintroduzir o Streamlit de forma segura**.

---

## Decisão

O Streamlit será utilizado **exclusivamente como camada de interface (UI)**, respeitando os seguintes princípios:

1. **Separação total de responsabilidades**

   * Streamlit não contém lógica de transcrição.
   * Streamlit não importa Whisper nem refinadores diretamente.
   * Toda lógica reside no pipeline CLI / Python.

2. **Pipeline como fonte de verdade**

   * O fluxo principal é executável via CLI (`cli_local.py`).
   * A UI apenas dispara ações e exibe resultados.

3. **Resiliência da aplicação**

   * Se o Streamlit falhar, o pipeline continua funcional.
   * Erros de processamento não devem derrubar a interface.

---

## Arquitetura Alvo

```
Streamlit (UI)
   ↓
Disparo de ação (função ou subprocess)
   ↓
transcribe_file.py (orquestrador)
   ↓
core/whisper_core.py
   ↓
refiners/*
   ↓
output/
```

### Diretórios de saída

* `output/audio/` → arquivos WAV
* `output/transcripts/` → transcrições textuais
* `output/summaries/` → resumos
* `output/md/` → versões em Markdown
* `output/quality/` → relatórios de qualidade (WPM)

### Arquivos de configuração relevantes

* `vocab.csv` → glossário de correções aplicadas no pós-processamento

---

## O que o Streamlit PODE fazer

* Upload de arquivos de áudio
* Inserção de links (ex.: YouTube)
* Disparo da transcrição
* Leitura e exibição dos arquivos gerados em `output/`
* Visualização de logs e status
* Gestão do glossário (adicionar/editar/remover termos)

---

## O que o Streamlit NÃO deve fazer

* Importar Whisper diretamente
* Manipular áudio em baixo nível
* Decidir regras de refinamento
* Alterar estrutura de pastas
* Substituir o pipeline CLI

Essas restrições evitam:

* travamentos da UI;
* estados inconsistentes;
* bugs difíceis de rastrear;
* regressões arquiteturais.

---

## Estratégias de Integração

### Opção A — Chamada direta de função (recomendada inicialmente)

* Streamlit importa uma função de alto nível do pipeline.
* Execução síncrona, mais simples de debugar.

### Opção B — Chamada via subprocess

* Streamlit executa `cli_local.py`.
* Maior isolamento.
* Útil para ambientes mais restritivos.

Ambas são compatíveis com o padrão adotado.

---

## Benefícios da Abordagem

* Interface desacoplada
* Pipeline testável independentemente
* Facilidade de manutenção
* Base sólida para evolução futura

---

## Status

* **Decisão aceita**
* **Integração permitida**
* **Pipeline pronto para uso com Streamlit**

---

## Observação Final

O Streamlit passa a ser um **componente descartável** do sistema. O valor do projeto reside no pipeline de transcrição e refinamento, não na interface.
