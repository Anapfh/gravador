# 📌 Roadmap & Issues do Projeto

Este documento consolida as **issues iniciais do projeto** e serve como:
- registro de escopo
- memória técnica
- guia de evolução
- base para criação das issues no GitHub

As issues estão organizadas de forma incremental, respeitando decisões já consolidadas e evitando regressões no core.

---

## 🧱 Issue 1 — Streamlit UI (MVP)

### Título
Streamlit interface for local recording and transcription (MVP)

### Descrição
Criar uma interface Streamlit mínima para uso local que replique o comportamento já estável do CLI, sem alterar o core do projeto.

O objetivo é validar a experiência de uso em interface gráfica mantendo o pipeline atual (gravação → transcrição) intacto.

### Escopo
- Botão **Gravar**
- Exibição de **status de gravação** (gravando / parado + tempo decorrido)
- Botão **Transcrever**
- Exibição do **texto transcrito**

### Fora de escopo
- Pausar / retomar gravação
- Alterações no `core/`
- Configurações avançadas
- Pós-processamento (refiners / LLM)

### Critérios de aceite
- Interface roda via `streamlit run`
- Gravação gera WAV válido (mesmo comportamento do CLI)
- Transcrição usa `core/whisper_core.py`
- Texto exibido corresponde ao arquivo `.txt`
- Core permanece congelado

### Labels sugeridos
`enhancement`, `ui`, `streamlit`, `mvp`

---

## 🎧 Issue 2 — Recording controls: pause / resume

### Título
Add pause and resume controls to audio recording

### Descrição
Adicionar controles de **pausar** e **retomar** a gravação de áudio, garantindo que o arquivo final seja consistente e compatível com o pipeline de transcrição existente.

Esta issue envolve mudança de estado interno da gravação e não deve ser implementada junto ao MVP da UI.

### Escopo
- Botão **Pausar**
- Botão **Retomar**
- Definição clara do comportamento de pausa
- WAV final válido e transcritível

### Questões a decidir
- Pausa gera silêncio ou interrompe captura?
- WAV final é contínuo ou concatenação?
- Impacto nos timestamps do Whisper?

### Critérios de aceite
- Gravação com pausa/retomada funcional
- WAV final transcritível
- Sem regressão na gravação simples
- Comportamento documentado

### Dependências
- Issue 1 concluída

### Labels sugeridos
`enhancement`, `audio`, `ux`, `design-decision`

---

## 🧠 Issue 3 — Local LLM post-processing with Ollama

### Título
Add optional local LLM post-processing using Ollama

### Descrição
Adicionar uma etapa opcional de pós-processamento usando **Ollama** para gerar resumos, atas ou interpretações a partir da transcrição já existente.

O uso de LLM deve ser **opt-in** e não interferir no pipeline principal.

### Escopo
- Entrada: texto transcrito
- Saída: resumo / ata / interpretação
- Execução local via Ollama
- Integração desacoplada do core

### Fora de escopo
- Uso de Ollama para ASR
- Dependência obrigatória
- Execução automática no MVP

### Critérios de aceite
- Pipeline funciona sem Ollama instalado
- Uso de Ollama é explícito
- Falha do Ollama não quebra o fluxo principal

### Labels sugeridos
`enhancement`, `llm`, `ollama`, `optional`

---

## ⚙️ Issue 4 — Centralize runtime configuration via TOML

### Título
Centralize runtime configuration via TOML

### Descrição
Centralizar configurações de execução em arquivos TOML para evitar parâmetros hardcoded no código.

### Escopo
- Modelo Whisper
- Idioma
- Caminhos de output
- Flags como `beam_size`, `vad_filter`

### Critérios de aceite
- CLI e UI leem configurações do TOML
- Valores default documentados
- Compatibilidade mantida

### Labels sugeridos
`enhancement`, `config`, `tech-debt`

---

## 📚 Issue 5 — Expand technical documentation and lessons learned

### Título
Expand technical documentation and lessons learned

### Descrição
Consolidar decisões técnicas, erros comuns e soluções encontradas durante o desenvolvimento do pipeline de gravação e transcrição.

### Escopo
- AGC / Intel Smart Sound
- RMS vs variação de sinal
- Windows + HuggingFace cache
- Decisão do backend de ASR

### Critérios de aceite
- Documentação clara no diretório `docs/`
- Referências cruzadas no README
- Conteúdo versionado

### Labels sugeridos
`documentation`, `tech-debt`

---

## 🧭 Observações finais

- As issues refletem o estado atual e o roadmap inicial do projeto
- Nenhuma issue reabre decisões já consolidadas
- Evolução deve respeitar a ordem proposta

Este documento serve como **fonte única de verdade** para planejamento e evolução do projeto.
