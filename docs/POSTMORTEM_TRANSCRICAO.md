Perfeito — **agora sim podemos fechar este capítulo com engenharia de verdade** ✅
O sistema **funciona**, o texto **é gerado**, o pipeline **está íntegro** e vocês **não vão mais perder tempo com isso**.

Abaixo está um **documento `.md` completo**, pensado para ser colocado em
`docs/POSTMORTEM_TRANSCRICAO.md` (ou nome equivalente), e **linkado ao `DECISIONS.md`**.

Ele documenta:

* ✅ o que estava errado
* ✅ por que era difícil de detectar
* ✅ o que foi corrigido (tecnicamente)
* ✅ quais regras nasceram disso
* ✅ próximos avanços claros (sem promessas mágicas)

---

```md
# Postmortem – Estabilização do Pipeline de Transcrição
Projeto Gravador Transcritor

**Status:** Resolvido e estabilizado  
**Período:** Jan/2026  
**Impacto:** Alto (pipeline inutilizável sem correção)  
**Resultado final:** Transcrição correta, persistida e auditável

Este documento registra de forma definitiva tudo o que ocorreu durante
a investigação do problema de **transcrições geradas vazias**, mesmo com
o Whisper funcionando corretamente.

Ele deve ser lido em conjunto com:
- `DECISIONS.md`
- `LESSONS_LEARNED_AND_NOTES.md`
- ADRs existentes do projeto

---

## 1. Sintoma observado

- Execução completa do pipeline sem exceções
- Whisper processava o áudio por ~18 minutos
- JSON bruto (`*_whisper_raw.json`) continha:
  - milhares de caracteres
  - centenas de segmentos
- Arquivo final `.txt` era criado com **0 KB**

Ou seja:
> Tudo parecia funcionar, mas o resultado final era inutilizável.

---

## 2. Hipóteses iniciais (descartadas)

As seguintes hipóteses **não eram a causa**:

- ❌ Whisper não reconheceu fala  
- ❌ Áudio inválido ou silencioso  
- ❌ Problema de encoding  
- ❌ Erro de permissão ao salvar arquivo  
- ❌ Problema de chunking  
- ❌ Timeout ou interrupção  

Todas foram descartadas com logs, métricas e dumps intermediários.

---

## 3. Evidência chave (ponto de virada)

Os logs mostraram claramente:

```

[DEBUG] Text length: 36670
[DEBUG] Segments count: 557

````

E o JSON bruto continha texto completo e coerente.

👉 **Conclusão inequívoca**:  
O problema ocorria **após o ASR**, na fase de **refinadores**.

---

## 4. Causa raiz real

### 4.1 Refinadores apagavam texto válido

Alguns refinadores (`orality`, `repetition`, `hallucination`, `lexical`)
podiam retornar:

- string vazia `""`
- estruturas não-string (ex: tuple)
- ou texto semanticamente inválido

O pipeline fazia:

```python
text = refinador(text)
````

Sem validação defensiva.

Resultado:

* texto válido do Whisper era **substituído**
* pipeline seguia normalmente
* arquivo final era salvo vazio

📌 **Falha silenciosa**, a pior categoria de bug.

---

## 5. Erro de design identificado

O erro **não estava nos refinadores individualmente**, mas no contrato implícito:

> O pipeline assumia que todo refinador sempre melhora o texto.

Essa suposição é **falsa em sistemas reais**.

---

## 6. Correção aplicada (definitiva)

### 6.1 Regra de ouro implementada

> **Nenhum refinador pode apagar texto válido.**

### 6.2 Implementação adotada

Foi criado um consumo defensivo:

* Refinador só substitui o texto se:

  * retornar `str`
  * e não estiver vazia
* Caso contrário:

  * o texto anterior é preservado

Isso garante:

* zero perda silenciosa
* estabilidade do pipeline
* refinadores realmente opcionais

---

## 7. Outras correções importantes

### 7.1 Retornos polimórficos tratados

Funções que retornam `(text, metadata)` passaram a ser consumidas corretamente.

### 7.2 Logs estruturados adicionados

* ASR
* métricas de áudio
* tamanho de texto
* persistência

### 7.3 Dumps intermediários

* JSON bruto do Whisper salvo para auditoria
* Métricas persistidas separadamente

---

## 8. Por que isso não pode voltar a acontecer

Agora o sistema tem:

* contratos explícitos
* logs claros
* métricas reais
* fallback automático
* evidência persistida

Qualquer regressão:

* será visível
* será auditável
* não será silenciosa

---

## 9. Regras consolidadas (link com DECISIONS.md)

Este postmortem fundamenta as seguintes decisões:

* Refinadores são **opcionais**
* Texto bruto do ASR é **fonte de verdade**
* Pipeline nunca confia cegamente em retornos
* Logs são parte da funcionalidade, não “debug”

Essas regras estão formalizadas em `DECISIONS.md`.

---

## 10. Próximos avanços (com o problema resolvido)

Agora que o pipeline está estável, os próximos passos são seguros:

### 10.1 Performance

* Avaliar `faster-whisper`
* GPU opcional
* Modelos maiores (medium/large)

### 10.2 Qualidade

* Refinadores com métricas próprias
* Lexical mais contextual
* Pontuação semântica opcional

### 10.3 Produto

* Resumo automático
* Indexação por tópico
* Busca semântica

### 10.4 Operação

* Modo diagnóstico on/off
* Flags de pipeline
* Perfis de execução

---

## 11. Conclusão

Este problema consumiu tempo porque:

* era silencioso
* parecia “funcionar”
* não quebrava nada explicitamente

Ele foi resolvido quando:

* logs foram ativados
* contratos foram respeitados
* engenharia substituiu suposição

📌 **Este documento existe para garantir que esse tempo nunca mais seja perdido.**

Fim do postmortem.

```

---

## Recomendações finais (fora do documento)

Sugiro agora:

1. 🔒 **Commitar este momento como “baseline estável”**
2. 📄 Linkar este postmortem no `DECISIONS.md`
3. 🧭 Seguir para performance e produto sem medo
4. 🚀 Vocês estão prontos para escalar

Parabéns — isso foi **engenharia madura, não tentativa e erro**.
```
## 12. Como o problema foi efetivamente resolvido (uso de LOG)

Esta seção documenta **o método técnico utilizado para isolar e resolver
definitivamente o problema**, com foco no uso de **logging estruturado**.

O objetivo é garantir que:
- o mesmo método possa ser reaplicado no futuro
- problemas semelhantes não sejam investigados “no escuro”
- o time saiba exatamente **onde instrumentar o código**

---

### 12.1 Princípio adotado

> **Antes de alterar comportamento, tornar o sistema observável.**

Nenhuma correção definitiva foi aplicada sem antes:
- comprovar o estado real dos dados
- observar entradas e saídas de cada etapa
- eliminar hipóteses com evidência concreta

---

### 12.2 Onde os LOGs foram adicionados

Os logs foram introduzidos **apenas nos pontos críticos do pipeline**, sem
poluir o código ou alterar interfaces.

#### 1️⃣ Core ASR (`core/whisper_core.py`)

Foram adicionados logs diagnósticos logo após o carregamento do áudio
e após a execução do Whisper.

**Objetivo:** confirmar se o Whisper realmente produzia texto.

Logs incluíram:

```text
[DEBUG] Audio shape
[DEBUG] Sample rate
[DEBUG] Duration (s)
[DEBUG] RMS energy
[DEBUG] Whisper elapsed
[DEBUG] Text length
[DEBUG] Segments count
Perfeito. Abaixo está a **versão expandida e precisa do `POSTMORTEM_TRANSCRICAO.md`**, **focada especificamente em “como foi resolvido”**, com **ênfase prática no uso de LOG**: **onde**, **como**, **por que** e **o que cada log revelou**.

👉 **Você pode substituir ou acrescentar este conteúdo no arquivo
`docs/POSTMORTEM_TRANSCRICAO.md`**, como uma seção própria.

---

````md
## 12. Como o problema foi efetivamente resolvido (uso de LOG)

Esta seção documenta **o método técnico utilizado para isolar e resolver
definitivamente o problema**, com foco no uso de **logging estruturado**.

O objetivo é garantir que:
- o mesmo método possa ser reaplicado no futuro
- problemas semelhantes não sejam investigados “no escuro”
- o time saiba exatamente **onde instrumentar o código**

---

### 12.1 Princípio adotado

> **Antes de alterar comportamento, tornar o sistema observável.**

Nenhuma correção definitiva foi aplicada sem antes:
- comprovar o estado real dos dados
- observar entradas e saídas de cada etapa
- eliminar hipóteses com evidência concreta

---

### 12.2 Onde os LOGs foram adicionados

Os logs foram introduzidos **apenas nos pontos críticos do pipeline**, sem
poluir o código ou alterar interfaces.

#### 1️⃣ Core ASR (`core/whisper_core.py`)

Foram adicionados logs diagnósticos logo após o carregamento do áudio
e após a execução do Whisper.

**Objetivo:** confirmar se o Whisper realmente produzia texto.

Logs incluíram:

```text
[DEBUG] Audio shape
[DEBUG] Sample rate
[DEBUG] Duration (s)
[DEBUG] RMS energy
[DEBUG] Whisper elapsed
[DEBUG] Text length
[DEBUG] Segments count
````

**O que isso revelou:**

* o áudio era válido
* havia energia suficiente (RMS > 0)
* Whisper produziu milhares de caracteres
* o problema NÃO estava no ASR

---

#### 2️⃣ Dump do resultado bruto do Whisper

Além dos logs em console, foi salvo um arquivo:

```text
output/transcripts/<nome>_whisper_raw.json
```

**Conteúdo:**

* `text`
* `segments`
* `language`
* probabilidades internas

**O que isso revelou:**

* o texto completo existia
* centenas de segmentos estavam presentes
* o Whisper estava funcionando corretamente

Esse dump foi decisivo para **descartar o ASR como causa raiz**.

---

#### 3️⃣ Pipeline (`transcribe_file.py`)

Foram mantidos logs de alto nível:

```text
[PIPELINE] Etapa 1/3 — ASR
[PIPELINE] Etapa 2/3 — Refinadores
[PIPELINE] Etapa 3/3 — Salvando arquivos
```

E as métricas finais foram logadas indiretamente via `metrics.json`.

**Objetivo:** confirmar que:

* todas as etapas eram executadas
* nenhuma exceção interrompia o fluxo
* o erro era silencioso

---

### 12.3 O que os LOGs permitiram concluir

Com base nos logs, foi possível afirmar com certeza que:

* ✔️ Whisper produziu texto válido
* ✔️ O texto chegou ao pipeline
* ❌ O texto era perdido **após o ASR**
* ❌ Nenhuma exceção era lançada
* ❌ O arquivo era salvo corretamente, porém vazio

Isso isolou o problema **exclusivamente na lógica dos refinadores**.

---

### 12.4 Como o LOG levou à causa raiz

Ao cruzar:

* `Text length` do Whisper (LOG)
* conteúdo do `*_whisper_raw.json`
* `text_length` salvo em `metrics.json`

ficou evidente que:

> O texto era apagado **entre a etapa 2 (Refinadores) e a etapa 3 (Persistência)**.

Isso direcionou a investigação para:

* retornos vazios (`""`)
* retornos polimórficos (`tuple`)
* substituições não defensivas no pipeline

Sem os logs, esse comportamento pareceria “mágico”.

---

### 12.5 Correção aplicada com base nos LOGs

Com a causa raiz identificada, a correção foi simples e segura:

* nenhum refinador passou a ser confiável por padrão
* o pipeline passou a validar explicitamente cada retorno
* texto só é substituído se o refinador produzir algo melhor

Essa correção **não teria sido possível com segurança sem os logs**.

---

### 12.6 Regra definitiva criada a partir do uso de LOG

> **Se um sistema não é observável, ele não é depurável.**

Regras derivadas:

* Logs são parte da funcionalidade
* Dumps intermediários são aceitáveis em modo diagnóstico
* Nenhuma correção estrutural deve ser feita sem evidência

Essas regras estão refletidas em:

* `DECISIONS.md`
* `LESSONS_LEARNED_AND_NOTES.md`

---

### 12.7 Diretriz para o futuro

Sempre que surgir um problema complexo:

1. Ativar logs antes de alterar lógica
2. Logar entradas e saídas reais
3. Persistir estado intermediário se necessário
4. Eliminar hipóteses com evidência
5. Só então aplicar correção

Esse método evitou retrabalho e levou à solução definitiva.

---

**Resumo:**
O problema foi resolvido não por tentativa e erro, mas por **observabilidade
estruturada**, usando logs no lugar certo, no momento certo.

```

---

Se quiser, no próximo passo posso:
- 🔗 ajustar referências cruzadas entre `POSTMORTEM_TRANSCRICAO.md` e `DECISIONS.md`
- 🧪 criar uma seção “Checklist de Diagnóstico” reutilizável
- 🧭 padronizar níveis de log (`INFO`, `DEBUG`, `ERROR`) no projeto

# Postmortem — CLI de Gravação de Áudio

## Contexto

Este documento registra o estado atual do desenvolvimento do CLI de gravação,
as decisões tomadas, problemas encontrados, correções aplicadas e próximos passos.

O objetivo é evitar regressões e retrabalho futuro.

---

## Estado Atual (Confirmado Funcional)

### CLI (`cli_local.py`)

- Modo interativo funcional
- Comandos disponíveis:
  - `gravar [tipo]`
  - `p` → pausar
  - `r` → retomar
  - `f` → finalizar
  - `s` → status
  - `Enter` → sair do CLI
- Estados bem definidos:
  - `idle`
  - `recording`
  - `paused`
- Gravação WAV gerada corretamente em:
📄 POSTMORTEM_CLI_GRAVACAO.md
# Postmortem — CLI de Gravação de Áudio

## Contexto

Este documento registra o estado atual do desenvolvimento do CLI de gravação,
as decisões tomadas, problemas encontrados, correções aplicadas e próximos passos.

O objetivo é evitar regressões e retrabalho futuro.

---

## Estado Atual (Confirmado Funcional)

### CLI (`cli_local.py`)

- Modo interativo funcional
- Comandos disponíveis:
  - `gravar [tipo]`
  - `p` → pausar
  - `r` → retomar
  - `f` → finalizar
  - `s` → status
  - `Enter` → sair do CLI
- Estados bem definidos:
  - `idle`
  - `recording`
  - `paused`
- Gravação WAV gerada corretamente em:


output/recordings/


### Decisões Importantes

- O CLI **não executa transcrição**
- O CLI **não chama outros scripts automaticamente**
- O CLI é responsável **apenas por gravação e controle**
- O Streamlit atua como frontend e orquestrador

Essas decisões preservam:
- simplicidade
- previsibilidade
- separação de responsabilidades

---

## Problemas Encontrados e Corrigidos

### 1. Argparse bloqueando modo interativo
**Causa:** argparse sendo chamado mesmo sem argumentos  
**Correção:** modo interativo quando `len(sys.argv) == 1`

### 2. WAV não era gerado
**Causa:** uso incorreto de `bytes` com `soundfile.write`  
**Correção:** concatenação correta de `numpy.ndarray`

### 3. UX confusa ao usar comandos fora de estado válido
**Causa:** mensagens genéricas  
**Correção:** mensagens explícitas por estado (`idle`, `recording`, `paused`)

---

## Comportamento Deliberadamente NÃO Implementado

### Enter finalizar gravação automaticamente

**Motivo:**
- Evitar finalizações acidentais
- Evitar mistura de responsabilidades
- Manter compatibilidade com Streamlit

Atualmente:
- `Enter` = sair do CLI
- `f` = finalizar gravação

---

## Próximos Passos (Propostos)

Nenhum dos itens abaixo é bug fix — são **evoluções**.

### 1. UX opcional
- Confirmar saída se houver gravação ativa
- Ex:


Há gravação em andamento. Finalizar antes de sair? (s/n)


### 2. Orquestração de pipeline
- Após `finalizar`, permitir:
- chamada opcional de `transcribe_file.py`
- apenas via flag ou modo explícito

### 3. Integração Streamlit
- Streamlit chamar:
- `cli_local.py gravar`
- depois `transcribe_file.py`
- CLI permanece simples

---

## Conclusão

O CLI está:
- estável
- funcional
- previsível
- seguro

O comportamento atual é **intencional** e **correto**.
As expectativas adicionais devem ser tratadas como evolução de produto,
não correção de erro.

Este documento deve ser atualizado apenas após mudanças deliberadas.

📄 POSTMORTEM — CLI GRAVADOR & PIPELINE DE TRANSCRIÇÃO
Projeto: Gravador + Transcritor (CLI + Streamlit)

Data: 2026-01-22
Status: Funcional, com pendências de robustez e performance

1. Contexto Geral

Este documento consolida toda a evolução, decisões técnicas, problemas encontrados e aprendizados durante o desenvolvimento do:

CLI de gravação de áudio (cli_local.py)

Pipeline de transcrição (Whisper)

Integração futura com Streamlit (frontend)

O objetivo principal é evitar regressões, retrabalho e perda de contexto ao continuar o projeto em novos prompts ou por novos desenvolvedores.

2. Onde paramos (estado atual confirmado)
✅ Funcionalidades já existentes
CLI (cli_local.py)

Modo interativo funcional

Atalhos disponíveis:

g → iniciar gravação

p → pausar

r → retomar

f → finalizar gravação

s → status

Enter → sair do CLI

Gravação de áudio em WAV funcionando

Arquivos gerados em:

output/recordings/


Estado persistido em:

output/recording_state.json

Pipeline de transcrição

Whisper executa corretamente

Chunking de áudio implementado

Logs de progresso existentes

Arquivos .json e .txt gerados corretamente

3. Problemas encontrados (e resolvidos)
3.1 Argparse bloqueava modo interativo

Causa: argparse sendo executado mesmo sem argumentos
Correção:

Se len(sys.argv) == 1, entra diretamente no modo interativo

3.2 WAV não era gerado

Causa: uso incorreto de bytes com soundfile.write
Correção:

Uso correto de numpy.ndarray + np.concatenate

3.3 CLI “travava” durante gravação

Causa: gravação bloqueante na mesma thread do input()
Correção:

Gravação movida para thread dedicada

CLI continua responsivo a p / r / f

3.4 Lentidão aparente ao finalizar gravação

Causa:

Concatenação de buffer grande em memória

Escrita síncrona do WAV

Ausência de feedback visual

Correção aplicada:

Logs progressivos:

tempo gravado

tamanho aproximado em MB

Logs explícitos ao finalizar e salvar WAV

4. Problema ainda em aberto (diagnosticado, NÃO aplicado)
4.1 Estado “órfão” persistido
Sintoma

recording_state.json permanece com:

{ "status": "recording" }


após abortos (Ctrl+C)

Nova execução do CLI herda estado inválido

Comandos como g e f ficam incoerentes

Usuário fica preso em “Finalizando…”

🎯 Decisão técnica (JÁ DEFINIDA, AINDA NÃO IMPLEMENTADA)

Ao iniciar o CLI interativo:

detectar estado recording órfão

avisar o usuário

resetar estado para idle

Adicionar LOG explícito:

quando não existe thread ativa

quando a finalização não tem nada para finalizar

❌ Não vamos:

mudar arquitetura

mexer em core/

remover persistência

inventar automações

5. Lições aprendidas (importantes)
5.1 Observabilidade é tão importante quanto performance

Sem logs, lentidão parece bug.
Com logs, o sistema fica confiável.

5.2 Gravação de áudio + CLI exige concorrência

Gravação bloqueante inviabiliza CLI interativo

Thread dedicada é padrão de mercado

5.3 Estado persistido precisa de sanitização

CLIs que sobrevivem a abortos precisam validar estado na inicialização

Estado não pode ser assumido como verdade absoluta

5.4 Separação de responsabilidades foi correta

CLI não executa transcrição

CLI não orquestra pipeline

Streamlit será o orquestrador

Isso evitou várias regressões

6. Pendências atuais (curto prazo)

🔧 Implementar sanitização de estado órfão no startup do CLI

📄 Documentar decisão no DECISIONS.md

🧪 Testar fluxo:

abortar gravação

reiniciar CLI

verificar reset automático para idle

7. Próximos passos recomendados (roadmap)
Curto prazo

✔️ Sanitização de estado órfão

✔️ Documentação final (DECISIONS + POSTMORTEM)

Médio prazo

⚡ Streaming de áudio direto para disco (menos RAM)

⚡ Otimização de performance da transcrição

chunking ajustável

logs de ETA

Longo prazo

🎛️ UX completa no Streamlit:

estado em tempo real

tempo decorrido

feedback visual

📦 Empacotamento em .exe

8. Arquivos e documentos-chave (para ganhar velocidade)
Código

cli_local.py — CLI de gravação (principal)

transcribe_file.py — pipeline de transcrição

core/whisper_core.py — ASR

refiners/ — pós-processamento textual

Documentos

DECISIONS.md

POSTMORTEM_CLI_GRAVADOR.md (este documento)

ADR-001-transcricao.md

ADR-003 — Chunking Semântico para LLM.md

9. Conclusão

O projeto não está falho — ele está maduro.

Os principais problemas encontrados foram:

concorrência

estado persistido

falta de observabilidade

Todos foram:

diagnosticados corretamente

resolvidos ou planejados com clareza

documentados para não se repetir

Este documento deve ser o ponto de retomada oficial no próximo prompt.
---

## 13. Postmortem — Captura de Áudio (Volume Baixo e Regressões)

### 13.1 Sintoma observado

Em regressões posteriores, o sistema passou a gerar:

- Arquivos WAV válidos
- Duração correta
- Tamanho compatível
- **Porém com áudio extremamente baixo**

Isso degradava:
- a qualidade da transcrição
- a confiança no pipeline
- o desempenho do Whisper

---

### 13.2 Fato importante (histórico)

⚠️ **Este problema JÁ HAVIA SIDO RESOLVIDO anteriormente.**

O histórico mostrou que:
- gravações anteriores geravam áudio com volume adequado
- Whisper transcrevia corretamente
- o problema retornou após alterações não alinhadas aos documentos canônicos

Conclusão:
> Trata-se de **regressão por perda de histórico**, não de problema novo.

---

### 13.3 Causa raiz identificada

A causa foi **forçar parâmetros de captura incompatíveis com o dispositivo real**.

Em especial:

- Dispositivo de entrada (Windows / Realtek) opera nativamente em **44.1 kHz ou 48 kHz**
- Alterações recentes passaram a capturar diretamente em **16 kHz**
- No Windows (WASAPI / PortAudio), isso resulta em:
  - atenuação do sinal
  - RMS baixo
  - WAV “válido”, porém com áudio fraco

Este comportamento é **conhecido e documentado empiricamente**.

---

### 13.4 Correção aplicada (definitiva)

A correção NÃO envolveu ganho artificial, normalização ou AGC.

Foi aplicada a regra já validada anteriormente:

> 🎙️ **Capturar sempre no sample rate NATIVO do dispositivo.**

Diretrizes consolidadas:
- Não forçar `samplerate` na captura
- Permitir que o driver use o valor nativo
- Gravar WAV em PCM_16
- Deixar qualquer conversão de sample rate para etapas posteriores (ASR)

---

### 13.5 Por que isso não pode voltar a acontecer

Porque agora está **documentado explicitamente** que:

- áudio baixo **não é bug do Whisper**
- áudio baixo **não se resolve com pós-processamento**
- áudio baixo **é erro de captura**
- forçar parâmetros “teóricos” quebra estabilidade no Windows

Qualquer alteração futura na captura **deve obrigatoriamente consultar este documento**.

---

### 13.6 Regra final

> ❗ **Nunca ajustar parâmetros de captura sem consultar o histórico.**  
> ❗ **Nunca “corrigir” áudio baixo com hacks posteriores.**  
> ❗ **A captura correta é a base de todo o pipeline.**

Este postmortem encerra definitivamente o tema.

# Postmortem — Transcrição Parcial e Incorreta

## Contexto

Durante a execução do pipeline do projeto **Gravador Transcritor Local**, foi observado que o sistema conseguiu gerar:
- arquivo de áudio (`.wav`)
- arquivo de transcrição (`.txt`)

Entretanto, a transcrição apresentou problemas relevantes:
- não cobriu todo o áudio gravado
- apresentou cortes indevidos
- gerou trechos semanticamente incorretos

Este postmortem documenta o ocorrido, identifica a causa-raiz e define ações corretivas.

---

## O que aconteceu

A **Etapa 2 — Transcrição** foi executada antes do encerramento formal da **Etapa 1 — Bundle Canônico RAW**.

Na prática:
- o arquivo de áudio ainda não tinha sido explicitamente declarado como finalizado
- não havia garantia formal de integridade, duração final ou estabilidade do WAV
- o pipeline não impunha um gate entre captura (RAW) e interpretação (transcrição)

Mesmo assim, a transcrição foi permitida.

---

## Impacto

A execução prematura da transcrição resultou em:
- processamento de áudio incompleto ou ainda em escrita
- perda de partes do conteúdo gravado
- transcrição truncada ou incorreta
- resultados não reprodutíveis e difíceis de auditar

O problema **não está relacionado à qualidade do modelo de ASR** (Whisper ou GPT-4o), mas à violação da fronteira entre etapas do pipeline.

---

## Causa-raiz

A causa principal foi a **ausência de um critério formal de fechamento da Etapa 1**.

Especificamente:
- o Bundle RAW ainda não estava canonizado
- não existia um estado explícito `READY`
- a Etapa 2 não validava se o áudio estava estável e finalizado

Isso permitiu que a transcrição fosse executada sobre dados ainda instáveis.

---

## Lição Aprendida

> **Transcrição só é confiável quando o Bundle Canônico RAW está formalmente fechado.**

Qualquer tentativa de interpretar áudio que:
- ainda esteja sendo gravado
- ainda esteja sendo escrito em disco
- não possua metadados finais consistentes

resultará, inevitavelmente, em erros.

---

## Ações Corretivas Definidas

1. Formalizar o encerramento da Etapa 1 (Bundle RAW)
2. Introduzir um gate obrigatório entre Etapa 1 e Etapa 2
3. Proibir a execução de transcrição sem Bundle RAW em estado `READY`
4. Documentar explicitamente o contrato entre as etapas do pipeline

---

## Conclusão

O problema observado não representou falha do modelo nem retrocesso técnico, mas sim um **checkpoint arquitetural importante**.

A partir deste postmortem, a separação entre captura (RAW) e interpretação (Transcrição) passa a ser tratada como um contrato obrigatório do sistema.

