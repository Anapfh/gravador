🟢 Implementar o ADR-002 — Pipeline de Resumo / Ata Corporativa
(Especificação funcional escrita)

Este texto é o que orienta toda a implementação.
Depois que concordarmos, o código só executa o que está aqui.

1️⃣ Objetivo do Pipeline

O pipeline de resumo/ata corporativa tem como objetivo:

Transformar uma transcrição confiável em um documento corporativo claro, estruturado e auditável,
sem nunca alterar ou sobrescrever a transcrição original.

Ele não cria informação, não deduz decisões e não completa lacunas.

2️⃣ Entradas e Saídas (contrato)
📥 Entrada obrigatória

Um arquivo de transcrição .txt

Considerado fonte primária

Pode ser:

vazio

curto

longo

📤 Saída

Um arquivo derivado, nunca a transcrição

Formato padrão: Markdown (.md)

Local: output/summaries/

📌 Regra absoluta:

Se a transcrição for vazia ou inválida, o resumo NÃO é gerado.

3️⃣ Regras de Comportamento (não negociáveis)
🔒 Regra 1 — Transcrição é imutável

Nunca é reescrita

Nunca recebe preâmbulo

Nunca recebe prompt

Nunca recebe resumo

🔒 Regra 2 — Preâmbulo só existe em memória

É apenas prompt para LLM

Nunca é salvo em disco

Nunca aparece no .txt

🔒 Regra 3 — Nada é inventado

O pipeline não pode:

criar decisões

criar responsáveis

criar prazos

inferir participantes

Se não estiver explícito na transcrição:

não aparece na ata

4️⃣ Fluxo Lógico do Pipeline
transcrição.txt
      ↓
validação de conteúdo
      ↓
(se necessário) chunking semântico
      ↓
preâmbulo adequado ao contexto
      ↓
LLM
      ↓
ata.md

5️⃣ Validação inicial (gate de segurança)

Antes de qualquer LLM:

Caso A — Transcrição vazia

Pipeline encerra

Retorna mensagem:

“Não há fala suficiente para gerar ata ou resumo.”

Caso B — Transcrição muito curta

Ata simples

Poucas seções preenchidas

Nenhuma extrapolação

Caso C — Transcrição longa

Entra o ADR-003 (chunking)

📌 Isso garante:

previsibilidade

economia de tokens

zero alucinação estrutural

6️⃣ Estrutura padrão da ATA (Markdown)

A estrutura oficial é:

# Ata da Reunião

## Contexto
(Data, tipo de reunião, breve descrição objetiva)

## Participantes
(Somente se explicitamente citados)

## Principais Assuntos
- …

## Decisões Tomadas
- …

## Ações e Responsáveis
- …

## Pendências / Próximos Passos
- …


📌 Se uma seção não tiver conteúdo, ela:

pode ficar vazia ou

pode ser omitida
(dependendo do preâmbulo)

7️⃣ Tipos de Contexto (preâmbulos)

O pipeline aceita um contexto explícito, por exemplo:

reuniao_interna

reuniao_externa

contratos_ti

treinamento

Cada contexto define:

tom do texto

foco do resumo

rigor formal

📌 Contexto nunca é inferido automaticamente.
Sempre vem do usuário ou do fluxo.

8️⃣ Papel do LLM no pipeline

O LLM:

reestrutura informação

organiza o que já existe

resume sem inventar

Ele não decide, não interpreta intenção, não completa silêncio.

9️⃣ Erros tratados explicitamente

O pipeline deve tratar:

transcrição vazia

transcrição incoerente

erro de LLM

timeout

falta de contexto

Em todos os casos:

transcrição permanece intacta

erro é explícito

nenhum arquivo inválido é gerado

10️⃣ Resultado esperado (critério de sucesso)

Consideramos o ADR-002 bem implementado quando:

✔️ Ata nunca contém informação inexistente
✔️ Transcrição nunca é alterada
✔️ Áudios ruins não geram documentos falsos
✔️ O comportamento é previsível e auditável
✔️ Um auditor consegue entender a origem de cada informação

### ADR-002 — Estrutura de Resumo/Ata Corporativa
- Status: Aprovado
- Data: 2026-01-19
- Escopo: LLM + Preâmbulos

✔️ Pipeline mínimo implementado e testado
✔️ Gate de transcrição vazia validado
✔️ Testes manuais executados com sucesso
