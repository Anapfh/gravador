# PROJECT_RULES — Gravador & Transcritor

**Status:** Ativo  
**Última atualização:** 2026-01-20  
**Natureza:** Documento canônico (contrato operacional do projeto)

Este documento define as **regras de ouro obrigatórias** do projeto, com o objetivo de:

- evitar regressões funcionais e arquiteturais  
- impedir looping de decisões já tomadas  
- garantir rastreabilidade técnica  
- preservar ganhos já homologados  

---

## 1. Princípios Fundamentais (Imutáveis)

1. **Nada homologado é reescrito. Apenas estendido.**  
   Correções são permitidas. Reinterpretações não.

2. **Responsabilidade única por camada.**  
   Nenhuma camada assume papel de outra, mesmo temporariamente.

3. **A transcrição é fonte primária imutável.**  
   Nunca é sobrescrita, enriquecida ou reinterpretada.

4. **Todo ganho técnico vira regra ou módulo isolado.**  
   Se resolveu um problema, deve virar:
   - configuração explícita, ou  
   - refinador dedicado.

5. **Decisões técnicas precedem mudanças relevantes.**  
   Código não decide arquitetura sozinho.

---

## 2. Arquitetura Oficial (Contrato)

áudio / vídeo
↓
core (ASR)
↓
refiners (qualidade / limpeza)
↓
transcrição (.txt – fonte primária)
↓
LLM (preâmbulo + regras, apenas em memória)
↓
saídas derivadas (ata, resumo, material)

yaml
Copiar código

### Papéis por camada

- **core/**  
  Execução de ASR (Whisper / outros).  
  Não contém regras linguísticas.  
  Não depende de UI.

- **refiners/**  
  Limpeza, qualidade e heurísticas.  
  Determinísticos e isolados.  
  Ativáveis via config.

- **config/**  
  Controle de comportamento.  
  Opt-in explícito.  
  Versionado.

- **docs/**  
  ADRs, decisões e regras.  
  Fonte de verdade.

- **app.py / CLI**  
  Orquestração e UX.  
  Nunca lógica de negócio profunda.

---

## 3. Regras de Alteração de Código (Enforcement)

### É proibido

- Chamar ASR fora de `core/`
- Colocar heurística linguística no `core/`
- Modificar arquivos de transcrição gerados
- Inicializar serviços externos no momento do import
- Reintroduzir comportamento já descartado em ADR

### É obrigatório

- Criar **novo refinador** para cada problema resolvido
- Tornar comportamento configurável sempre que possível
- Preservar assinaturas após homologação
- Registrar exceções no `DECISIONS.md`

---

## 4. Regra de Revisão de Documentação (Crítica)

Qualquer alteração funcional exige **revisão prévia dos documentos oficiais**.

Antes de alterar código, é obrigatório revisar:

- ADR-001 — Transcrição  
- ADR-002 — Estrutura de Ata / Resumo  
- ADR-003 — Chunking Semântico  
- DECISIONS.md  
- PROJECT_RULES.md  

Mudanças que violem decisões existentes são consideradas **regressão arquitetural**.

---

## 5. Homologação e Congelamento

Uma funcionalidade é considerada **homologada** somente quando:

- possui módulo isolado  
- possui configuração explícita (ou justificativa documentada)  
- está registrada em ADR ou DECISIONS  

Após homologação:

- assinaturas não mudam  
- comportamento base não muda  
- melhorias são apenas incrementais  

---

## 6. Uso de Projetos Externos (Canibalização)

É permitido:

- analisar padrões, ideias e conceitos  

É proibido:

- copiar código integral  
- importar arquitetura externa  
- adaptar o projeto ao código externo  

Regras obrigatórias:

- reimplementar no modelo arquitetural interno  
- registrar a análise no `DECISIONS.md`  
- citar referência externa (sem reutilização direta de código)

---

## 7. UX e Transparência Operacional

- UX não pode mascarar limitações técnicas  
- Feedback visual deve ser honesto e explícito  
- Estados críticos devem ser visíveis ao usuário:
  - gravando
  - finalizado
  - erro
- Controles visuais devem refletir a realidade técnica  

UX que induz interpretação incorreta é considerado bug.

---

## 8. Gestão de Regressões

Sempre que um problema já resolvido reaparecer:

1. Revisar `DECISIONS.md`
2. Identificar onde a regra deixou de ser aplicada
3. Corrigir o ponto de fuga
4. Atualizar o documento, se necessário

Nunca rediscutir decisões antes de revisar o histórico.

---

## 9. Changelog e Rastreabilidade

Todo arquivo alterado deve conter:

- changelog resumido
- data
- natureza da mudança
- documentos revisados

Exemplo obrigatório:

v1.2.1

Ajuste de UX de gravação

Documentos revisados: ADR-001, DECISIONS.md

yaml
Copiar código

---

## 10. Status do Documento

Este documento é:

- contrato operacional do projeto  
- fonte de verdade  
- não é sugestão  

Qualquer violação deve ser:

- justificada  
- documentada  
- temporária  
