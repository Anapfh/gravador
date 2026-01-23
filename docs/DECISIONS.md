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

Resumo:
- Necessidade de pós-processamento determinístico
- Mitigação de alucinação fonética e semântica
- Fundamentação para criação de refinadores isolados

---

### ADR-002 — Estrutura de Resumo / Ata Corporativa
- **Status:** Aprovado  
- **Data:** 2026-01-19  
- **Escopo:** LLM + Preâmbulos  

Status de implementação:
- Pipeline mínimo implementado
- Gate de transcrição vazia validado
- Ata nunca é gerada sem transcrição válida

---

### ADR-003 — Chunking Semântico para LLM
- **Status:** Aprovado  
- **Data:** 2026-01-19  

Objetivo:
- Reduzir alucinação
- Garantir escalabilidade para textos longos

---

## 3. Decisões Arquiteturais e Operacionais

### Uso de LLM local para sumarização (Ollama)
- **Data:** 2026-01-20  

Decisão:
- Uso exclusivo para saídas derivadas (ata / resumo)
- Nenhuma reutilização de código externo
- Execução sem estado e sem histórico

Motivação:
- Eliminar custos variáveis
- Garantir previsibilidade
- Controle total do pipeline

---

### Seleção explícita de engine de ASR
- **Data:** 2026-01-20  

Decisão:
- Whisper local como engine padrão
- GPT-4o-mini-transcribe mantido apenas como opção futura
- Seleção feita via configuração
- Nenhum serviço externo inicializado no import

Motivação:
- Execução offline
- Redução de dependências
- Previsibilidade operacional

---

### Ativação opt-in de limpeza de oralidade e repetição
- **Data:** 2026-01-20  

Decisão:
- Refinadores determinísticos
- Atuação apenas sobre padrões explícitos
- Totalmente configuráveis e reversíveis

Motivação:
- Melhorar legibilidade
- Reduzir ruído para geração de atas

---

## 4. Robustez do Pipeline de Transcrição

### Preservação da transcrição válida
- **Data:** 2026-01-20  

Decisão:
1. A transcrição bruta gerada pelo ASR **nunca é descartada**
2. Refinadores tornam-se **não destrutivos**
3. Caso refinadores resultem em texto vazio, ocorre fallback automático
4. Métricas são preservadas ao longo do pipeline

Consequências:
- Eliminação de falhas por “transcrição vazia”
- Pipeline resiliente a áudio baixo e repetitivo
- Base sólida para análises lexicais futuras

---

## 5. Gravação de Áudio no Windows

### Sample rate nativo obrigatório
- **Data:** 2026-01-20  

Decisão:
- A gravação deve usar **o sample rate nativo do dispositivo**
- No Windows, 48000 Hz é considerado padrão operacional

Motivação:
- PortAudio (WASAPI) exige compatibilidade exata
- Sample rate divergente causa falha imediata

---

### Abandono de sounddevice e PyAudio (Windows)
- **Data:** 2026-01-20  

Decisão:
- Abandonar sounddevice e PyAudio para captura no Windows
- Padronizar gravação via **FFmpeg (CLI)**

Motivação:
- Erros recorrentes (-9996, -9997, -9999)
- Limitações do stack Windows + drivers
- Estabilidade comprovada do FFmpeg

---

### Separação entre Gravação e Streamlit
- **Data:** 2026-01-20  

Decisão:
- Streamlit **não grava áudio**
- Gravação ocorre exclusivamente via CLI
- Streamlit apenas consome WAVs prontos

Motivação:
- Evitar conflitos de runtime
- Estabilidade da aplicação

---

## 6. Alinhamento de Imports à Estrutura Real do Projeto
- **Data:** 2026-01-20  

Decisão:
- Imports devem refletir **exatamente** a estrutura em disco
- Não assumir empacotamento inexistente
- Core permanece estável; orquestração adapta

Consequências:
- Eliminação de ImportError e ModuleNotFoundError
- Clareza de responsabilidades

---

## 7. Execução de Scripts e Resolução de Paths

### Regra canônica de execução
- **Data:** 2026-01-20  

Decisão:
1. O projeto **não depende do diretório corrente (cwd)**
2. Scripts em `tests/` devem resolver paths via `Path(__file__)`
3. `cli_local.py` é **ancorado na raiz do projeto**
4. Nenhum script pode chamar outro por path relativo

Padrão obrigatório:

```python
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent
```

Motivação:
- Reprodutibilidade
- Execução consistente em Windows, venv, CI e Streamlit
- Eliminação definitiva de erros “can’t open file”

Status:
- Aplicado em `download_and_transcribe_youtube.py`
- Aplicado em `cli_local.py`

---

## 8. Componentes Fora do Pipeline Oficial

Arquivos mantidos apenas como referência histórica:

- `summarizer.py`
- `gemma.py` (modo CLI isolado)

Status:
- Não devem ser usados em produção
- Não integram o pipeline oficial

---

## 9. Integração com Streamlit

Decisão:
- Streamlit é **camada de interface**
- Pipeline CLI é a fonte de verdade
- Streamlit pode chamar o pipeline por função ou subprocess

Motivação:
- Isolamento
- Testabilidade
- Robustez

---

## 10. Avaliação Geral

Após revisão completa:

- Arquitetura por camadas está correta
- Não há violações de responsabilidade
- Pipeline é estável, auditável e previsível

Este documento é **fonte de verdade histórica**.

Antes de qualquer alteração funcional:
1. Revisar este arquivo
2. Verificar decisões existentes
3. Criar nova entrada apenas se necessário

Rediscussão sem revisão histórica é considerada **falha de processo**.
DECISÃO DE ENGENHARIA (FINAL)

Vamos aplicar defesa em profundidade, em 3 camadas mínimas:

Whisper Core → sempre retorna str

Refinadores → nunca retornam None

Orquestrador (transcribe_file.py) → garante string final antes de salvar

Isso encerra definitivamente:

crashes tardios

perda de transcrição pronta

sensação de “trabalhou tudo e perdeu”

Perfeito. Entendido **sem ambiguidade** 👍
Vou fazer **três coisas**, exatamente no escopo que você pediu:

1. **Alterar o texto das REGRAS DO PROJETO**, incorporando explicitamente o diretório de prompts
2. **Registrar formalmente o diretório `C:\gravador_transcritor\Prompts` na documentação**
3. **Estabelecer a obrigação de apontamento para prompts em TODO código alterado** (docstring + changelog)

Sem inventar comportamento, sem mexer em arquitetura, sem tocar em decisões já vencidas.

---

## 1️⃣ Texto das REGRAS DO PROJETO — **VERSÃO ATUALIZADA (substituir)**

```md
REGRAS DO PROJETO

✅ todos os códigos corrigidos

✅ arquivos completos (copiar e substituir com segurança)

✅ alterar somente o necessário, de forma localizada e rastreável

✅ todo código alterado DEVE conter:
   - docstring explicativa
   - changelog no padrão do projeto
   - apontamento explícito para documentos e/ou prompts utilizados

✅ respeitar rigorosamente a estrutura real do projeto:
   - core/
   - refiners/
   - output/

✅ consultar obrigatoriamente:
   - documentos em docs/
   - prompts canônicos em Prompts/
     (C:\gravador_transcritor\Prompts)

✅ todo código que consuma LLM, organize texto ou gere saídas derivadas
   DEVE registrar em docstring quais prompts são lidos/utilizados

✅ diagnóstico sempre objetivo:
   - sem voltar no tempo
   - sem reabrir decisões já vencidas
   - sem regressões
   - sem perda parcial ou total de código já pacificado/homologado

❌ não inventar comportamento

❌ não inferir regras fora dos documentos e prompts canônicos

❌ não quebrar interface pública existente

❌ não ignorar contratos documentais (ADR, DECISIONS, PROJECT_RULES)

Vou organizar por arquivo, para você copiar e substituir com segurança.

Entregáveis esperados:
- todos os códigos corrigidos
- completos
- alterados somente onde necessário
- com docstrings, changelog e referências documentais
- mantendo o padrão do projeto em termos de documentação
```

---

## 2️⃣ Registro documental — **Diretório de Prompts**

Este ponto **precisa existir formalmente** na documentação do projeto.

### 📁 Diretório canônico de prompts

```
C:\gravador_transcritor\Prompts
```

### 📄 Conteúdo esperado (exemplos)

* `PROMPT_CANONICO_LLM.md`
* prompts de ata / resumo
* prompts por tipo de sessão (reunião, treinamento, curso, etc.)
* prompts de validação / controle de alucinação

📌 **Regra explícita**:

> Prompts são **documentos canônicos**, não strings soltas no código.

Isso está **alinhado** com:

* `PROJECT_GUARDRAILS.md`
* `ANTI_HALLUCINATION_POLICY.md`
* `PROMPT_CANONICO_LLM.md` 

---

## 3️⃣ Padrão obrigatório a partir de agora (para TODO código alterado)

### 📌 Em docstrings (exemplo de padrão)

```python
"""
summary_pipeline.py

Responsabilidade:
- Geração de resumo/ata a partir de transcrição imutável

Fontes canônicas consultadas:
- docs/ADR-002 — Estrutura de Ata Corporativa
- docs/ADR-003 — Chunking Semântico
- Prompts/PROMPT_CANONICO_LLM.md
- Prompts/ATA_REUNIAO_INTERNA.md

Observação:
- Prompts são lidos como fonte de regra, não inferidos.
"""
```

---

### 📌 Em changelog (exemplo de padrão)

```text
CHANGELOG
2026-01-22
- Ajuste documental
- Inclusão de referência explícita ao diretório Prompts/
- Nenhuma alteração de comportamento
```

---

## 🟢 Conclusão objetiva

* ✔️ Regras do projeto atualizadas
* ✔️ Diretório `Prompts/` formalmente reconhecido como canônico
* ✔️ Obrigação explícita de apontamento para prompts
* ✔️ Nenhuma mudança funcional
* ✔️ Nenhuma decisão reaberta
* ✔️ Nenhuma regressão

A partir daqui, **todo código que eu te entregar**:

* já virá com **referência explícita aos prompts**
* tanto em **docstring** quanto em **changelog**
* e sempre citando o caminho `Prompts/...`


