# DECISIONS — Registro de Decisões Técnicas

**Status:** Ativo  
**Última atualização:** 2026-01-20  
**Natureza:** Documento canônico de histórico decisório

Este documento registra **decisões técnicas efetivamente tomadas**, seu
contexto, motivação e impacto no projeto.

Ele complementa os ADRs:
- ADRs definem **arquitetura e princípios**
- DECISIONS registram **decisões operacionais e evolutivas**

Este documento existe para **evitar regressões, retrabalho e rediscussões**.

---

## 1. Regras de Uso deste Documento

- Decisões aqui registradas **não são reabertas**
- Mudanças de direção exigem **nova entrada**
- ADRs aprovados **não são reescritos**
- DECISIONS podem complementar ADRs sem substituí-los

---

## 2. ADRs Aprovados (Referência)

### ADR-001 — Qualidade da Transcrição em PT-BR

- **Status:** Aprovado  
- **Data:** 2026-01-19  
- **Escopo:** ASR + Pós-processamento  
- **Referência:** `docs/ADR-001-transcricao.md`

**Resumo:**
- Identificação de falhas de inteligibilidade e alucinação
- Necessidade de pós-processamento robusto
- Fundamentação para criação de refinadores determinísticos

---

### ADR-002 — Estrutura de Resumo / Ata Corporativa

- **Status:** Aprovado  
- **Data:** 2026-01-19  
- **Escopo:** LLM + Preâmbulos  
- **Referência:** `docs/ADR-002 — Estrutura de ResumoAta Corporativa.md`

**Status de Implementação:**
- Pipeline mínimo implementado (`corporate_minutes.py`)
- Gate de segurança para transcrição vazia validado
- Testes manuais executados com sucesso (`fake_llm`)
- Ata **não é gerada** sem transcrição válida

---

### ADR-003 — Chunking Semântico para LLM

- **Status:** Aprovado  
- **Data:** 2026-01-19  
- **Escopo:** Textos longos / LLM  
- **Referência:** `docs/ADR-003 — Chunking Semântico para LLM.md`

**Objetivo:**
- Evitar perda de contexto
- Reduzir alucinação em textos longos

---

## 3. Decisões Arquiteturais e Operacionais

### Uso de LLM local para sumarização (Ollama)

- **Data:** 2026-01-20

Após análise de repositórios públicos e modelos pagos,
foi adotado **LLM local via Ollama** para sumarização e geração de atas.

**Decisão:**
- Uso exclusivo para saídas derivadas (ata / resumo)
- Nenhum código externo reutilizado
- Implementação sem estado, sem histórico e sem inferência

**Motivação:**
- Eliminar custos variáveis
- Garantir previsibilidade
- Manter controle total do pipeline

---

### Ativação de limpeza leve de oralidade e repetição

- **Data:** 2026-01-20

Foi ativada limpeza **opt-in** de termos de oralidade e
repetições mecânicas no pós-processamento da transcrição.

**Decisão:**
- Atuação apenas sobre termos explícitos
- Sem alteração semântica
- Totalmente configurável e reversível via config

**Motivação:**
- Melhorar legibilidade da transcrição
- Reduzir ruído para geração de atas e resumos

---

### Engine de ASR com fallback explícito

- **Data:** 2026-01-20

Foi definida seleção explícita de engine de ASR via configuração.
Observação:
- No estado atual do projeto, Whisper local está ativo como engine efetiva.
- A opção GPT-4o permanece desabilitada por decisão de custo.


**Decisão:**
- Whisper local como default operacional
- GPT-4o-mini-transcribe mantido como opção futura
- Nenhum serviço externo inicializado no import

**Motivação:**
- Evitar dependências obrigatórias
- Garantir execução offline
- Prevenir falhas por configuração incompleta

---

## 4. Avaliação Geral da Arquitetura

- **Data:** 2026-01-19

Após revisão completa da estrutura de diretórios e do fluxo real
de execução, fica registrado que a arquitetura por camadas:

áudio → core (ASR) → refiners → transcrição (fonte primária)
→ summarizers (LLM) → artefatos derivados

yaml
Copiar código

está correta, consistente e alinhada com os ADRs aprovados.

Nenhuma violação de responsabilidade entre camadas foi identificada.

Este registro é **informativo** e não altera ADRs existentes.

---

## 5. Componentes Obsoletos / Fora do Pipeline Oficial

Os componentes abaixo permanecem no repositório **apenas como referência
histórica ou uso manual**, não integrando o pipeline homologado.

### summarizer.py
- **Motivo:** geração manual de Markdown, sem LLM ou ADR-002
- **Status:** Obsoleto — não utilizar em produção

### gemma.py (modo CLI isolado)
- **Motivo:** ferramenta auxiliar para testes manuais
- **Status:** Fora do pipeline oficial

Esses arquivos **não devem ser utilizados** por `app.py` nem por fluxos automatizados.

---

## 6. Projetos Externos Analisados (Referência Histórica)

Os projetos abaixo foram analisados apenas como referência conceitual
e **não fazem parte da evolução ativa do projeto**:

- `meeting-summaries-main`
- `meeting_minutes_generator-main`

**Decisão:**
- Nenhum código foi reutilizado
- Apenas ideias conceituais foram avaliadas
- Não entram mais na evolução do projeto

---

## 7. Regra Final

Este documento é **fonte de verdade histórica**.

Antes de qualquer alteração funcional relevante:
1. Revisar este arquivo
2. Verificar se a decisão já existe
3. Criar nova entrada **apenas se necessário**

Rediscussão sem revisão histórica é considerada **falha de processo**.

### Definição explícita de sample rate para gravação de áudio (Windows)

- **Data:** 2026-01-20

Durante testes de gravação no Windows utilizando `sounddevice` + PortAudio,
foi identificado erro recorrente:

PortAudioError: Invalid sample rate [PaErrorCode -9997]


Após inspeção direta do dispositivo de entrada via Python:

```python
import sounddevice as sd
sd.query_devices(9, 'input')['default_samplerate']

Decisão:

O sample rate de gravação foi fixado explicitamente em 48000 Hz

A gravação deve sempre usar o sample rate nativo do dispositivo

Evita falhas de inicialização de InputStream no Windows (WASAPI)

Motivação:

PortAudio em modo compartilhado (WASAPI) exige compatibilidade exata

Sample rates divergentes causam falha imediata de stream

48000 Hz é o padrão mais comum em microfones Windows modernos

Essa decisão é considerada obrigatória para execução estável do projeto em Windows.

### Substituição de sounddevice por PyAudio para gravação (Windows)

- **Data:** 2026-01-20

Após múltiplos testes práticos no Windows, foi constatado que a biblioteca
`sounddevice` apresenta instabilidade estrutural com PortAudio nos backends
WDM / WASAPI, gerando erros recorrentes:

- PaErrorCode -9996 (Invalid device)
- PaErrorCode -9997 (Invalid sample rate)
- PaErrorCode -9999 (Unanticipated host error)

Mesmo com configuração correta de device e sample rate, os erros persistem.

**Decisão:**
- Substituir definitivamente `sounddevice` por `PyAudio` na camada de gravação
- Manter a interface pública (`Recorder.start()` / `stop()`)
- Não alterar app.py nem pipeline de transcrição

**Referência técnica:**
- Projeto `whisper_mic`, amplamente utilizado e validado em Windows

**Motivação:**
- Estabilidade real em ambiente Windows
- Controle explícito de buffer e stream
- Eliminação de falhas no nível do driver

Essa decisão é considerada **definitiva para gravação de microfone no Windows**.
### Extensão do Recorder com controle de estado (pause / resume)

- **Data:** 2026-01-20

O módulo `recorder.py` foi estendido para suportar
controle explícito de estado de gravação:

- `start()` → inicia gravação
- `pause()` → pausa captura de áudio
- `resume()` → retoma captura
- `stop()` → finaliza e persiste o WAV

A extensão foi implementada **sem quebra de compatibilidade**,
mantendo a interface pública já utilizada pelo `app.py`.

**Decisão técnica associada:**
- Migração definitiva da captura de áudio para PyAudio
- Uso de buffer manual inspirado no projeto `whisper_mic`

**Motivação:**
- Maior controle de UX
- Preparação para indicadores visuais (tempo, estado, VU meter)
- Estabilidade comprovada no Windows

Essa decisão não altera o pipeline de transcrição nem os refinadores.
### Separação da gravação de áudio do Streamlit (Windows)

**Data:** 2026-01-20

Após múltiplos testes, foi constatado que a captura direta de microfone
via PortAudio (PyAudio / sounddevice) é instável no Windows quando
executada dentro do runtime do Streamlit, resultando no erro recorrente:

`OSError: [Errno -9999] Unanticipated host error`

Mesmo com:
- device correto
- sample rate compatível
- implementação conforme boas práticas
- stream aberto fora de threads de aplicação

o erro persistiu exclusivamente no contexto do Streamlit.

**Decisão:**
- Isolar a gravação de áudio em processo CLI separado
- Streamlit passa a apenas consumir arquivos WAV já gravados

**Motivação:**
- Estabilidade comprovada no Windows
- Eliminação de conflitos de event loop e handles de áudio
- Arquitetura mais previsível e sustentável

Essa decisão é considerada definitiva para ambientes Windows.
## 2026-01-20 — Consolidação de Refino de Transcrição e UX no Windows

### Contexto
Durante a integração final entre CLI, Streamlit e pipeline de transcrição,
foram identificadas limitações estruturais no uso de PyAudio em conjunto
com Streamlit no Windows (PortAudio / WASAPI).

Além disso, iniciou-se a fase de refino determinístico da transcrição,
com foco em qualidade textual, sem uso de LLM e sem violar a transcrição
como fonte primária.

---

### Decisões Tomadas

#### 1. Gravação de áudio no Windows
- **Decisão:** Streamlit NÃO deve gravar áudio diretamente no Windows.
- **Motivo:** Instabilidade recorrente do PyAudio/PortAudio em runtime Streamlit
  (erros -9996 e -9999).
- **Solução adotada:**  
  - Gravação feita exclusivamente via CLI (`cli_local.py gravar`)
  - Streamlit consome apenas arquivos WAV já gravados
- **Status:** Homologado

#### 2. Separação clara de responsabilidades (UX)
- CLI:
  - grava áudio
  - salva WAV confiável
- Streamlit:
  - upload/consumo de WAV
  - transcrição
  - refino
  - geração de ata/resumo
- **Status:** Homologado

---

### Refino de Transcrição (Fase 1)

#### Refinadores implementados
- `refiners/orality.py`
  - Remoção determinística de termos de oralidade configurados
  - Sem inferência semântica
- `refiners/repetition.py`
  - Remoção de repetições mecânicas consecutivas
- `refiners/hallucination.py`
  - Detecção e corte de alucinação local e global (ADR-001)

Todos os refinadores:
- são determinísticos
- são configuráveis via `config/transcription.toml`
- não utilizam LLM
- não inventam conteúdo

---

### Ajustes no Orquestrador
- `transcriber.py` passou a:
  - importar refinadores como módulos isolados
  - aplicar refinadores em pipeline previsível
  - manter API pública estável (`transcribe_audio`)

---

### Status Geral
- Pipeline de gravação (CLI): **Estável**
- Pipeline de transcrição: **Estável e refinado**
- Streamlit: **Estável (sem captura de áudio)**
- Arquitetura: **Alinhada aos ADRs**
- Próxima fase: **Refino lexical e segmentação sintática**
### Registro adicional — Áudio válido com transcrição final vazia (2026-01-20)

Durante teste de gravação via CLI (`python cli_local.py gravar`), foi observado
o seguinte comportamento:

- O áudio foi gravado corretamente (`.wav` gerado com conteúdo audível)
- O Whisper executou a transcrição sem erro
- O arquivo `.txt` de saída foi gerado, porém com conteúdo vazio

#### Interpretação técnica
- O texto bruto gerado pelo ASR não atingiu critérios mínimos de qualidade
  após aplicação dos refinadores ativos
- O refinador de alucinação global classificou o conteúdo como semanticamente inválido
- O pipeline retornou string vazia de forma intencional

#### Status
- Comportamento esperado
- Nenhuma falha de gravação
- Nenhum erro de execução
- Nenhuma correção emergencial necessária

#### Observação
Este registro serve apenas para rastreabilidade do comportamento observado.
O evento reforça a necessidade dos refinadores de correção lexical e segmentação
para reduzir falsos positivos de descarte.
### Diagnóstico — Discrepância entre áudio monitorado e áudio gravado (2026-01-20)

Foi identificado que o áudio monitorado pelo usuário não corresponde
ao dispositivo de captura utilizado pelo PyAudio.

O áudio percebido como "bom" provém do dispositivo:
- Mixagem estéreo (Realtek HD Audio Stereo input)

Enquanto a captura estava ocorrendo via:
- dispositivo padrão / mapeador genérico

Decisão:
- Tornar explícito o uso de `input_device_index` no recorder
- Selecionar entre microfone dedicado ou mixagem estéreo conforme o contexto
### Decisão — Parâmetros de captura de áudio tornados configuráveis (2026-01-20)

Parâmetros críticos de captura de áudio (device index, sample rate e canais)
foram externalizados para configuração (`transcription.toml`).

Motivação:
- variabilidade de dispositivos no Windows
- necessidade de alinhar captura com contexto de uso
- evitar hardcode frágil no recorder

Escopo:
- alteração mínima
- sem impacto no fluxo CLI
- sem alteração de arquitetura
## 2026-01-20 — Consolidação da captura de áudio via FFmpeg no Windows

### Contexto
Durante a evolução do pipeline de gravação e transcrição, foi identificado
erro persistente (`Errno -9999 Unanticipated host error`) ao tentar capturar
áudio via PyAudio/PortAudio no Windows, mesmo após:

- configuração explícita de dispositivo
- uso de sample rate nativo do hardware
- instrumentação com logging detalhado
- validação de múltiplos dispositivos de entrada

Foi confirmado que o projeto **já utilizava anteriormente FFmpeg para captura
de áudio**, e que esta abordagem funcionava de forma estável.

---

### Diagnóstico
- O erro `-9999` é característico de limitações do stack:
  - Windows
  - drivers Realtek / Intel Smart Sound
  - PortAudio
- O erro ocorre mesmo com dispositivos válidos enumerados
- Não há correção confiável via ajustes de código no PyAudio oficial
- O problema não está na lógica do projeto, mas na camada de captura

---

### Decisão
- **Abandonar PyAudio como mecanismo de captura de áudio no Windows**
- **Retomar e padronizar o uso de FFmpeg para gravação via CLI**
- Manter todo o restante do pipeline inalterado:
  - transcriber
  - refinadores
  - Correção

  # Decisões de Arquitetura do Projeto

---

## DEC-2026-01-20 — Robustez do pipeline de transcrição (áudio baixo, alucinação e fallback)

### Contexto

Durante testes em ambiente Windows corporativo, o pipeline de transcrição apresentou comportamentos intermitentes:

* áudio capturado com nível baixo variando conforme driver/dispositivo;
* Whisper processando o áudio integralmente, mas retornando saída posteriormente descartada;
* filtros de alucinação e repetição atuando de forma destrutiva, zerando transcrições válidas.

Esses cenários ocorreram principalmente em treinamentos institucionais, com fala padronizada e repetitiva.

### Problema

A arquitetura anterior permitia que refinadores:

* retornassem string vazia;
* causassem falha terminal (`RuntimeError`) mesmo após transcrição válida;
* perdessem métricas lexicais já calculadas, exigindo recomputação posterior.

Isso tornava o pipeline frágil e sensível a variações de áudio e heurística.

### Decisão

Foram adotadas as seguintes decisões arquiteturais:

1. **Transcrição válida nunca é descartada**
   O Whisper é tratado como fonte primária de verdade. Caso refinadores resultem em texto vazio, o sistema faz fallback automático para o texto bruto.

2. **Filtros tornam-se não destrutivos**
   Refinadores (ex.: `hallucination.py`) passam a **marcar e sinalizar** alucinação, em vez de zerar conteúdo ou causar falha.

3. **Normalização e tolerância a áudio baixo**
   O pipeline passa a normalizar o áudio antes da transcrição e reduz a agressividade de limiares de silêncio, tornando-o resiliente a variações de volume do sistema.

4. **Propagação de métricas ao longo do pipeline**
   Métricas lexicais calculadas em refinadores iniciais são preservadas e disponibilizadas a jusante (ex.: para `lexical.py`), evitando recomputação e perda de sinal.

5. **Interface CLI mantida estável**
   Todos os ajustes foram feitos via configuração e lógica interna, sem introduzir novos parâmetros de linha de comando.

### Consequências

* Eliminação definitiva do erro "Transcrição vazia após processamento" em cenários com áudio válido.
* Pipeline mais robusto para reuniões e treinamentos corporativos.
* Base sólida para análises lexicais, scoring e chunking semântico futuros.
* Maior rastreabilidade e auditabilidade das decisões do sistema.

### Status

Aceita e implementada.
# Decisões de Arquitetura do Projeto

---

## DEC-2026-01-20 — Robustez do pipeline de transcrição (áudio baixo, alucinação e fallback)

### Contexto

Durante testes em ambiente Windows corporativo, o pipeline de transcrição apresentou comportamentos intermitentes:

* áudio capturado com nível baixo variando conforme driver/dispositivo;
* Whisper processando o áudio integralmente, mas retornando saída posteriormente descartada;
* filtros de alucinação e repetição atuando de forma destrutiva, zerando transcrições válidas.

Esses cenários ocorreram principalmente em treinamentos institucionais, com fala padronizada e repetitiva.

### Problema

A arquitetura anterior permitia que refinadores:

* retornassem string vazia;
* causassem falha terminal (`RuntimeError`) mesmo após transcrição válida;
* perdessem métricas lexicais já calculadas, exigindo recomputação posterior.

Isso tornava o pipeline frágil e sensível a variações de áudio e heurística.

### Decisão

Foram adotadas as seguintes decisões arquiteturais:

1. **Transcrição válida nunca é descartada**
   O Whisper é tratado como fonte primária de verdade. Caso refinadores resultem em texto vazio, o sistema faz fallback automático para o texto bruto.

2. **Filtros tornam-se não destrutivos**
   Refinadores (ex.: `hallucination.py`) passam a **marcar e sinalizar** alucinação, em vez de zerar conteúdo ou causar falha.

3. **Normalização e tolerância a áudio baixo**
   O pipeline passa a normalizar o áudio antes da transcrição e reduz a agressividade de limiares de silêncio, tornando-o resiliente a variações de volume do sistema.

4. **Propagação de métricas ao longo do pipeline**
   Métricas lexicais calculadas em refinadores iniciais são preservadas e disponibilizadas a jusante (ex.: para `lexical.py`), evitando recomputação e perda de sinal.

5. **Interface CLI mantida estável**
   Todos os ajustes foram feitos via configuração e lógica interna, sem introduzir novos parâmetros de linha de comando.

### Consequências

* Eliminação definitiva do erro "Transcrição vazia após processamento" em cenários com áudio válido.
* Pipeline mais robusto para reuniões e treinamentos corporativos.
* Base sólida para análises lexicais, scoring e chunking semântico futuros.
* Maior rastreabilidade e auditabilidade das decisões do sistema.

### Status

Aceita e implementada.

---

## DEC-2026-01-20 — Alinhamento de imports à estrutura real do projeto

### Contexto

Durante a consolidação do pipeline de transcrição, ocorreram erros de importação (`ModuleNotFoundError` e `ImportError`) após melhorias arquiteturais. Esses erros surgiram porque alguns trechos de código passaram a assumir uma estrutura de pacote (`transcription.*`) que **não corresponde à estrutura real do projeto em disco**.

A estrutura efetiva do projeto utiliza diretórios lógicos (`core/`, `refiners/`) no mesmo nível dos scripts executáveis, sem empacotamento formal.

### Problema

* Imports apontavam para módulos inexistentes (`transcription.*`).
* Funções eram importadas com nomes não expostos pelo módulo real (`transcribe_audio` vs. `whisper_transcribe`).
* O erro não era de dependência, mas de **contrato e topologia de código**.

### Decisão

Foram adotadas as seguintes decisões:

1. **Respeitar a estrutura real do projeto**
   Os imports devem refletir exatamente os diretórios existentes (`core`, `refiners`), sem criar pacotes conceituais não implementados.

2. **Manter o core estável**
   O módulo `core/whisper_core.py` não foi alterado. Ele expõe funções específicas (`whisper_transcribe`) e retorna estruturas de dados claras.

3. **Orquestração adapta, core não**
   O script `transcribe_file.py` é responsável por adaptar chamadas e extrair o texto bruto do resultado retornado pelo core.

4. **Evitar funções genéricas fictícias**
   Funções como `transcribe_audio` não devem ser assumidas se não fazem parte do contrato explícito do módulo.

### Consequências

* Eliminação definitiva de erros de importação em execução via CLI.
* Maior clareza sobre responsabilidades entre core, orquestração e refinadores.
* Base mais segura para futuras refatorações (empacotamento formal poderá ser feito de forma planejada).

### Status

Aceita e registrada.
🧠 FLUXO FINAL (PARA FIXAR)

transcribe_file.py

chama → whisper_transcribe(...)

recebe → dict

extrai → result["text"]

passa raw_text para:

orality

repetition

hallucination

lexical (depois)

👉 Esse é o contrato correto do pipeline.

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

---

## O que o Streamlit PODE fazer

* Upload de arquivos de áudio
* Inserção de links (ex.: YouTube)
* Disparo da transcrição
* Leitura e exibição dos arquivos gerados em `output/`
* Visualização de logs e status

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

  Resolução de paths em scripts de tests/

Data: 2026-01-20

Durante a execução de scripts localizados no diretório tests/, foi identificado erro recorrente de execução ao chamar o cli_local.py por caminho relativo, resultando em:

can't open file '...\\tests\\cli_local.py'


Decisão:

Scripts localizados em tests/ devem sempre resolver caminhos com base na raiz do projeto, utilizando Path(__file__).

É proibido assumir que a execução ocorrerá a partir da raiz (cwd variável).

O cli_local.py é considerado ancorado na raiz do projeto e deve ser referenciado por path absoluto derivado.

Padrão obrigatório:

from pathlib import Path

CURRENT_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = CURRENT_DIR.parent
CLI_PATH = PROJECT_ROOT / "cli_local.py"


Motivação:

Evitar falhas por execução fora da raiz

Garantir reprodutibilidade em Windows, venv, CI e futuras integrações (ex.: Streamlit)

Manter a arquitetura CLI como fonte de verdade, sem mover arquivos

Status:
✔️ Decisão aceita
✔️ Aplicada no download_and_transcribe_youtube.py
✔️ Não altera arquitetura nem contratos existentes

✅ Decisão que está CORRETA

“Scripts em tests/ devem sempre resolver paths via Path(__file__)”

Ela está 100% alinhada com o projeto.

❌ O que ainda está violando a decisão

Existe alguma chamada residual (provavelmente no cli_local.py antigo ou em versão em cache) que ainda faz:

chamada direta a transcribe_file.py sem path absoluto


C:\gravador_transcritor
├── cli_local.py
├── transcribe_file.py
├── transcriber.py
├── app.py
├── recorder.py
├── config\
│   └── transcription.toml
├── core\
│   └── whisper_core.py
├── refiners\
│   ├── orality.py
│   ├── repetition.py
│   ├── hallucination.py
│   └── lexical.py
├── output\
│   ├── audio\
│   └── transcripts\
└── tests\
    └── download_and_transcribe_youtube.py
