# BASELINE_PROJETOS_TECNICOS.md

## 1. Objetivo do Documento
Este documento consolida lições aprendidas, decisões arquiteturais e boas práticas
identificadas durante o desenvolvimento de projetos técnicos que envolvem:
- Machine Learning
- Processamento de áudio
- Integração de múltiplas bibliotecas de terceiros
- Ambientes Python complexos

O objetivo é evitar retrabalho, erros recorrentes e perda de tempo em projetos futuros.

---

## 2. Princípios Fundamentais

### 2.1 Nenhuma biblioteca ML é realmente “plug and play”
Projetos que envolvem:
- PyTorch
- Lightning
- HuggingFace
- pyannote
- Whisper

possuem **forte acoplamento de versões**.

> Atualizar “só uma lib” quase sempre quebra o sistema.

---

### 2.2 Pip não resolve incompatibilidade arquitetural
Reinstalar pacotes raramente resolve quando o problema é:
- versão do modelo ≠ versão da lib
- runtime moderno executando modelo antigo
- dependências transitivas conflitantes

A solução correta é:
- congelar versões
- separar ambientes
- documentar compatibilidades

---

## 3. Ambientes Devem Ser Isolados por Função

### Exemplo correto:
- `.venv_app` → gravação / UI / streamlit
- `.venv_transcription` → whisper
- `.venv_diarization` → pyannote

Nunca misturar:
- diarização + UI + experimentos no mesmo venv

---

## 4. Processamento de Áudio (Regra de Ouro)

❌ Nunca processar áudio longo de uma vez  
✅ Sempre dividir em blocos (chunking)

Motivos:
- consumo de memória não linear
- travamentos silenciosos
- tempo imprevisível

Padrão recomendado:
- converter para WAV (mono, 16kHz)
- chunks de 5 a 10 minutos
- processamento incremental
- merge posterior

---

## 5. Modelos Pré-treinados Têm Contexto Histórico

Sempre verificar:
- versão do modelo
- versão da biblioteca usada no treino
- versão do torch usada no treino

Avisos como:
> “Model was trained with torch 1.10, yours is 2.x”

❗ Não devem ser ignorados em produção.

---

## 6. Logs Não São Ruído, São Diagnóstico

Logs detalhados:
- não significam erro
- indicam progresso interno
- ajudam a identificar travamentos reais

Regra prática:
- Se não há log por muito tempo + CPU ativa → provavelmente travado
- Ctrl+C para identificar ponto exato do bloqueio

---

## 7. Quando Parar e Replanejar

É correto parar quando:
- tempo cresce sem progresso
- erros começam a “se repetir em camadas”
- solução vira tentativa e erro

Parar, documentar e redefinir arquitetura **é ganho de produtividade**, não atraso.

---

## 8. Checklist Rápido Antes de Iniciar Novo Projeto

- [ ] Objetivo simples validado?
- [ ] Ambiente isolado criado?
- [ ] requirements.txt congelado?
- [ ] Estratégia de chunking definida?
- [ ] Logs configurados?
- [ ] Documento de contexto criado?

---

## 9. Lição Final

Projetos técnicos falham menos por falta de código  
e mais por falta de **decisão arquitetural explícita**.

Este baseline existe para garantir que decisões importantes
não precisem ser reaprendidas a cada novo projeto.


# BASELINE_PROJETOS_TECNICOS

> **Objetivo**: Este documento consolida lições aprendidas, decisões arquiteturais e boas práticas reutilizáveis para qualquer projeto técnico (IA, dados, backend, automação), evitando retrabalho, perda de contexto e falhas recorrentes de ambiente.

---

## 1. PRINCÍPIO FUNDAMENTAL

> **Projeto técnico não começa com código. Começa com controle de contexto e arquitetura.**

Sempre que um projeto envolver:

* múltiplas dependências
* bibliotecas de ML/IA
* ambientes (WSL, Docker, venv, CUDA)

👉 **O baseline é obrigatório antes de qualquer feature.**

---

## 2. CONTROLE DE CONTEXTO (OBRIGATÓRIO)

### 2.1 Arquivos mínimos de controle

Todo projeto deve possuir, desde o início:

* `BASELINE_PROJETOS_TECNICOS.md`
* `CONTEXT_HANDOFF_YYYYMMDD.md`
* `STATUS_TECNICO_ATUAL.md`

### 2.2 Regra de ouro

Se qualquer uma das situações abaixo ocorrer:

* dependências começam a conflitar novamente
* decisões precisam ser reexplicadas
* sensação de "acho que já tentamos isso"
* logs não explicam mais o estado do sistema

➡️ **PARAR CÓDIGO IMEDIATAMENTE** e atualizar a documentação antes de seguir.

---

## 3. LIÇÕES APRENDIDAS (EXTRAÍDAS DO PROJETO WHISPER / DIARIZAÇÃO)

### 3.1 Pip NÃO é ferramenta de arquitetura

❌ `pip install` não resolve incompatibilidade estrutural.

✔️ O que resolve:

* versionamento fechado
* ambientes imutáveis
* requirements por domínio (ex: whisper ≠ diarização)

---

### 3.2 Nunca misturar domínios frágeis no mesmo ambiente

| Domínio  | Característica                      |
| -------- | ----------------------------------- |
| Whisper  | Tolerante, rápido, fácil            |
| Pyannote | Frágil, lento, altamente versionado |

➡️ **Nunca compartilhar o mesmo `venv`.**

---

### 3.3 Torch novo quebra modelo antigo

Se aparecer a mensagem:

> Model was trained with torch X, yours is Y

Significa:

* comportamento indefinido
* travamentos longos
* resultados imprevisíveis

✔️ Solução correta:

* usar torch compatível
* ou aceitar que o modelo é legado

---

### 3.4 Diarização é custo, não padrão

Para áudios longos (~30 min):

* Whisper: ~10 min CPU
* Pyannote: 30–90 min CPU

➡️ Só usar diarização quando:

* houver valor claro de negócio
* houver fallback

---

### 3.5 "Funcionou ontem" não é sucesso

Sem:

* requirements fixos
* README de ambiente
* CONTEXT_HANDOFF

➡️ Projeto **não é reproduzível**.

---

## 4. ORDEM CORRETA DE PROJETO (PADRÃO REUTILIZÁVEL)

### Fase 1 — Base sólida

* documentação
* controle de contexto
* arquitetura mínima

### Fase 2 — Produto funcional

* fluxo simples
* valor entregue rápido
* poucas dependências

### Fase 3 — Incrementos

* features opcionais
* módulos isolados
* flags de ativação

---

## 5. PADRÃO DE ARQUITETURA RECOMENDADO

```
audio/
  capture/
  files/
nlp/
  whisper/
  summarizer/
optional/
  diarization/
```

Cada domínio:

* ambiente próprio
* dependências próprias
* fallback claro

---

## 6. PADRÃO DE LOGS

Formato obrigatório:

```
YYYY-MM-DD HH:MM:SS | LEVEL | domain.event | key=value
```

Exemplo:

```
2026-01-30 10:49:56 | INFO  | diarization.started | audio=meeting.m4a
2026-01-30 10:50:30 | WARN  | diarization.slow_step | step=embeddings
2026-01-30 10:52:10 | ERROR | diarization.failed | reason=timeout
```

---

## 7. CHECKLIST "SE QUEBRAR"

1. Ambiente é reproduzível?
2. Requirements estão fixos?
3. Domínios estão separados?
4. Logs explicam o estado?
5. Decisões estão documentadas?

Se qualquer resposta for **NÃO** → voltar para documentação.

---

## 8. REGRA FINAL

> **Código pode ser refeito. Histórico perdido não.**

Sempre documentar antes de avançar.

---

**Status do documento**: v1.0
**Origem**: Projeto Whisper + Diarização
**Uso**: Base para todos os projetos futuros
