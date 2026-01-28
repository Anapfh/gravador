# Lições Aprendidas — Pipeline de Transcrição

**Projeto:** Gravador e Transcritor  
**Período:** Janeiro/2026  
**Status:** Consolidado  
**Objetivo:** Evitar regressões e repetir decisões corretas

Este documento registra as **principais lições aprendidas** durante a evolução
do pipeline de transcrição de áudio, especialmente em cenários de **áudio longo,
execução em CPU e uso do Whisper**.

As lições aqui descritas foram obtidas **empiricamente**, a partir de erros reais,
logs e comportamento observado em execução.

---

## 1. Whisper em CPU é lento, mas previsível

### Observação
- Whisper em CPU (FP32) pode levar vários minutos para áudios longos
- Longos períodos sem saída **não indicam travamento**

### Lição
> Silêncio no terminal ≠ processo travado.

### Decisão
- Sempre fornecer feedback de progresso explícito
- Nunca assumir erro apenas por lentidão

---

## 2. Progresso visível é obrigatório em áudio longo

### Observação
- Whisper não fornece callbacks de progresso
- Usuário tende a interromper processos aparentemente “parados”

### Lição
> Transparência de progresso é requisito funcional, não luxo.

### Decisão
- Implementar chunking de áudio
- Exibir percentuais e etapas claras no terminal

---

## 3. Chunking lógico (`clip_timestamps`) NÃO funciona no Whisper

### Observação
- Uso de `clip_timestamps` resultou em texto vazio
- ASR executou até 100% sem erro, mas sem conteúdo

### Lição
> `clip_timestamps` não corta áudio; filtra segmentos internos.

### Decisão
- Proibir chunking lógico
- Usar exclusivamente **chunking físico (WAV real)**

---

## 4. Chunking físico é a única abordagem segura

### Observação
- Cortes físicos do WAV funcionam consistentemente
- Cada chunk gera texto real

### Lição
> Whisper precisa “ver” um áudio completo por execução.

### Decisão
- Criar arquivos temporários WAV por chunk
- Concatenar texto final

---

## 5. Nunca confiar que ASR retorna texto

### Observação
- Whisper pode retornar `text=None` ou `""`
- Isso ocorre sem exceções explícitas

### Lição
> ASR pode falhar silenciosamente.

### Decisão
- Orquestrador deve blindar retorno
- Texto final **sempre deve ser string**

---

## 6. Refinadores nunca podem quebrar o pipeline

### Observação
- Refinadores retornando `None` quebraram a persistência
- O erro ocorreu após ASR bem-sucedido

### Lição
> Refinadores são opcionais; pipeline não é.

### Decisão
- Refinadores devem sempre retornar `str`
- Orquestrador deve validar antes de usar

---

## 7. Defesa em profundidade é obrigatória

### Observação
- Blindar apenas um ponto não foi suficiente
- Erros surgiram em camadas diferentes

### Lição
> Cada camada deve proteger seu próprio contrato.

### Decisão
- Core garante `str`
- Refinadores garantem `str`
- Orquestrador garante `str` antes de salvar

---

## 8. Arquivos nunca devem deixar de ser gerados

### Observação
- Erros tardios impediram escrita do arquivo
- Trabalho completo foi perdido

### Lição
> Perder resultado após processamento completo é inaceitável.

### Decisão
- Mesmo texto vazio deve gerar arquivo
- Persistência é etapa crítica, não opcional

---

## 9. `cwd` é fonte recorrente de bugs no Windows

### Observação
- Execuções a partir de `tests/` quebraram paths relativos
- Subprocess herdou contexto errado

### Lição
> Nunca confiar no diretório corrente.

### Decisão
- Resolver paths via `Path(__file__)`
- `cli_local.py` ancorado na raiz

---

## 10. Scripts em `tests/` não são testes unitários

### Observação
- `tests/` contém scripts de integração e orquestração
- Execução direta causou confusão de contexto

### Lição
> `tests/` ≠ pytest.

### Decisão
- Executar scripts de `tests/` sempre a partir da raiz
- Documentar esse uso explicitamente

---

## 11. Logging acelera correção mais do que otimização prematura

### Observação
- Sem logs, problemas pareciam aleatórios
- Com logs, causa raiz ficou evidente

### Lição
> Observabilidade vem antes de performance.

### Decisão
- Logging estruturado por etapa
- Tempo por chunk e por fase
- Logs ativos por padrão

---

## 12. Cache de modelo Whisper é obrigatório

### Observação
- Reload de modelo causava lentidão desnecessária
- Modelo é pesado e imutável

### Lição
> Recarregar modelo é desperdício.

### Decisão
- Cache global de modelos Whisper
- Um load por execução

---

## 13. Interface estável é mais importante que “correção rápida”

### Observação
- Várias correções poderiam quebrar interface
- Isso causaria efeito cascata

### Lição
> Quebrar interface resolve um bug e cria cinco.

### Decisão
- Interfaces públicas não são alteradas
- Correções são internas e defensivas

---

## 14. Whisper não fornece garantias fortes — o pipeline deve fornecer

### Observação
- Whisper falha silenciosamente em vários cenários
- Não há exceções claras

### Lição
> O pipeline deve ser mais confiável que a engine.

### Decisão
- Tratar Whisper como componente não confiável
- Orquestrador assume responsabilidade final

---

## 15. Documentar lições aprendidas evita regressões

### Observação
- Muitos erros foram “óbvios” apenas depois
- Sem registro, tendem a reaparecer

### Lição
> Memória de time precisa ser escrita.

### Decisão
- Manter documentos de lições aprendidas
- Integrar com DECISIONS.md quando aplicável

---

## Conclusão Geral

O pipeline atual só atingiu estabilidade após:

- abandonar suposições implícitas
- adotar engenharia defensiva
- aceitar limitações reais do Whisper
- priorizar transparência e robustez

Este documento deve ser consultado **antes de qualquer refatoração
ou otimização futura**.

# Lições Aprendidas e Notas Arquiteturais
Projeto Gravador e Transcritor

**Status:** Documento vivo  
**Última atualização:** 2026-01-22

Este documento consolida **lições aprendidas**, **armadilhas encontradas**
e **regras práticas** descobertas durante a implementação e estabilização
do pipeline de transcrição.

Ele complementa e referencia diretamente:
- `DECISIONS.md`
- ADRs do projeto (`ADR-001`, `ADR-002`, `ADR-003`)

Nenhuma regra aqui substitui o `DECISIONS.md`; este documento **explica o porquê**.

---

## 1. Whisper pode funcionar perfeitamente e ainda assim “não funcionar”

### O que aconteceu
- Whisper executou por mais de 18 minutos
- Gerou centenas de segmentos
- Texto completo estava presente no JSON bruto
- Arquivo final `.txt` foi salvo vazio

### Lição aprendida
> **Pipeline bem-sucedido ≠ resultado correto**

O Whisper pode:
- retornar texto válido
- sem lançar exceção
- e esse texto ser perdido **depois**, por lógica de pós-processamento

### Documento relacionado
- `DECISIONS.md` → DEC-001, DEC-002

---

## 2. Falhas silenciosas são mais perigosas que exceções

### O que aconteceu
- Refinadores retornaram valores válidos do ponto de vista de tipo
- Mas semanticamente destrutivos (`""`, `tuple`, etc.)
- Nenhuma exceção foi levantada

### Lição aprendida
> **Falha silenciosa é pior que crash explícito**

### Regra prática
- Toda etapa que transforma texto deve ser **defensiva**
- Nunca assumir que “retornar algo” é suficiente

### Documento relacionado
- `DECISIONS.md` → DEC-003, DEC-009

---

## 3. Refinadores não são filtros obrigatórios

### O que aconteceu
- Um refinador apagou texto válido
- Pipeline seguiu normalmente
- Resultado final foi perdido

### Lição aprendida
> **Refinadores são opcionais; o texto bruto não**

### Regra prática
- Refinadores só podem substituir texto se:
  - retornarem `str`
  - e não estiver vazia
- Caso contrário, o texto anterior deve ser preservado

### Documento relacionado
- `DECISIONS.md` → DEC-003

---

## 4. Retornos polimórficos exigem consumo explícito

### O que aconteceu
- `cut_hallucinated_tail` retorna `(text, metrics)`
- Pipeline assumia retorno simples (`str`)
- Texto foi substituído por estrutura inválida

### Lição aprendida
> **Não basta documentar retorno; é preciso consumi-lo corretamente**

### Regra prática
- Pipeline deve:
  - extrair explicitamente o texto
  - ignorar metadados quando não necessários
  - nunca propagar estruturas inesperadas

### Documento relacionado
- `DECISIONS.md` → DEC-002, DEC-012

---

## 5. Chunking em Whisper é mais complexo do que parece

### O que aconteceu
- Tentativas de chunking lógico falharam
- Tentativas de chunking físico manual falharam
- APIs esperadas não existiam na lib oficial

### Lição aprendida
> **Whisper oficial não foi projetado para chunking manual**

### Regra prática
- Com `openai-whisper`:
  - usar transcrição do áudio completo
- Chunking deve ser tratado como:
  - problema de UX
  - ou resolvido com outra engine (ex: faster-whisper)

### Documento relacionado
- `DECISIONS.md` → DEC-004, DEC-005

---

## 6. Logs salvaram o projeto

### O que aconteceu
- Sem logs, tudo parecia “funcionar”
- Com logs, ficou claro:
  - texto existia
  - onde ele era perdido
  - por qual etapa

### Lição aprendida
> **Observabilidade precede otimização**

### Regra prática
- Logs estruturados são obrigatórios em:
  - ASR
  - refinadores
  - persistência
- Dumps intermediários são aceitáveis em modo diagnóstico

### Documento relacionado
- `DECISIONS.md` → DEC-006, DEC-007

---

## 7. Métricas não podem confiar em suposições

### O que aconteceu
- `metrics.json` mostrava `text_length = 0`
- Whisper tinha produzido texto válido

### Lição aprendida
> **Métricas devem refletir o estado final real**

### Regra prática
- Métricas devem ser calculadas:
  - após todas as transformações
  - sobre o texto realmente persistido

### Documento relacionado
- `DECISIONS.md` → DEC-009

---

## 8. Contratos importam mais que implementação

### O que aconteceu
- Refinadores estavam corretos isoladamente
- O contrato implícito entre eles não estava

### Lição aprendida
> **Pipeline é um sistema, não uma soma de funções**

### Regra prática
- Contratos devem ser:
  - explícitos
  - documentados
  - blindados no consumo

### Documento relacionado
- `DECISIONS.md` → DEC-012

---

## 9. Documentar evita regressões invisíveis

### O que aconteceu
- Problemas só ficaram claros após investigação longa
- Sem documentação, eles seriam reintroduzidos facilmente

### Lição aprendida
> **Memória técnica precisa ser escrita**

### Regra prática
- Toda falha relevante deve gerar:
  - uma decisão (`DECISIONS.md`)
  - ou uma lição aprendida (este documento)

### Documento relacionado
- `DECISIONS.md` → DEC-013

---

## 10. Conclusão geral

O pipeline só se estabilizou quando:

- suposições foram eliminadas
- contratos ficaram explícitos
- refinadores passaram a ser opcionais de fato
- logs expuseram o fluxo real dos dados

Este documento existe para garantir que:
- esses erros **não retornem**
- novas pessoas entendam o contexto
- decisões futuras sejam informadas pela experiência real

---

**Este documento deve ser lido junto com `DECISIONS.md`.  
Nenhuma mudança estrutural deve ignorar essas lições.**

## Lições Aprendidas — Pipeline de Gravação e Transcrição

### 1. Captura de áudio é o fator mais crítico
Modelos ASR não compensam áudio ruim.

### 2. Bluetooth não é device primário para ASR
Deve ser fallback apenas.

### 3. AGC e normalização são obrigatórios no Windows
Uso de:
- acompressor
- dynaudnorm

é indispensável.

### 4. Whisper funciona melhor com áudio limpo a 16kHz mono
Volume artificial sem controle degrada a transcrição.

### 5. Seleção automática de device evita erros humanos
O sistema deve se adaptar ao hardware ativo.

Resultado:
- aumento significativo de qualidade
- redução de erros
- pipeline estável

# Lessons Learned — Pipeline Gravador–Transcritor

## Context

Durante o desenvolvimento do projeto **Gravador Transcritor Local**, foi identificado um problema na geração de transcrições a partir de gravações locais de áudio.

Embora o sistema tenha conseguido gerar:
- o arquivo de áudio (`.wav`)
- o arquivo de transcrição (`.txt` / `.json`)

o resultado da transcrição apresentou falhas relevantes, como:
- transcrição parcial do áudio
- cortes indevidos no conteúdo
- erros semânticos em trechos específicos

Este documento registra as **lições aprendidas**, com foco em evitar recorrência e fortalecer a arquitetura do pipeline.

---

## O que aconteceu

A **Etapa 2 — Transcrição** foi executada antes do encerramento formal da **Etapa 1 — Bundle Canônico RAW**.

Na prática:
- o áudio ainda não havia sido declarado como finalizado
- o estado da gravação não estava explicitamente encerrado
- não existia garantia de integridade, duração final ou estabilidade do arquivo de áudio

Mesmo assim, o pipeline permitiu que a transcrição fosse iniciada.

---

## Impacto

A execução prematura da transcrição resultou em:
- processamento de áudio incompleto ou ainda em escrita
- perda de partes do conteúdo gravado
- transcrição incorreta ou truncada
- resultados não reprodutíveis e difíceis de auditar

Importante: o problema **não está relacionado à qualidade do modelo de transcrição**, mas sim à ordem e aos contratos entre as etapas do pipeline.

---

## Causa-raiz

A causa principal foi a **ausência de um gate explícito entre as etapas do pipeline**.

Em particular:
- não havia um critério formal de “áudio fechado”
- o Bundle RAW ainda não estava canonizado
- a Etapa 2 não validava se o Bundle RAW estava em estado `READY`

Isso permitiu que a transcrição fosse executada sobre dados instáveis.

---

## Lição Aprendida (Principal)

> **A transcrição só é confiável quando o Bundle Canônico RAW está formalmente fechado.**

Qualquer tentativa de interpretar áudio que:
- ainda esteja sendo gravado
- ainda esteja sendo escrito em disco
- não possua metadados finais consistentes

resultará, inevitavelmente, em erros de transcrição.

---

## Ações Corretivas

A partir deste aprendizado, foram definidas as seguintes ações:

1. **Formalizar o encerramento da Etapa 1**
   - definir critérios objetivos para considerar o áudio finalizado
   - congelar a estrutura e os metadados do Bundle Canônico RAW

2. **Introduzir um gate obrigatório entre etapas**
   - a Etapa 2 só pode iniciar se `bundle.status == READY`

3. **Reforçar a separação de responsabilidades**
   - a Etapa 1 é responsável apenas pela captura e persistência do áudio
   - a Etapa 2 é responsável exclusivamente pela interpretação (transcrição)

---

## Benefícios Esperados

Com essas correções, o pipeline passa a ser:
- previsível
- auditável
- reprocessável
- resiliente a erros de estado

Além disso, elimina-se uma classe inteira de falhas difíceis de diagnosticar.

---

## Conclusão

O problema observado não representou um retrocesso, mas sim um **checkpoint arquitetural importante**.

A experiência reforçou a necessidade de contratos claros entre as etapas do pipeline e consolidou a importância do **Bundle Canônico RAW** como base confiável para todas as etapas posteriores.

### Observação técnica — cálculo de duração de áudio

A biblioteca padrão `wave` do Python suporta apenas arquivos WAV (RIFF).
Ao permitir transcrição de formatos como MP3, M4A e OGG, tornou-se necessário
condicionar o cálculo de duração ao formato do arquivo, evitando falhas
pós-transcrição e garantindo estabilidade da UI.

Decisão: duração é exibida apenas quando disponível de forma confiável.
