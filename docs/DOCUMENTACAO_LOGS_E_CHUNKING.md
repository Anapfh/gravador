Perfeito. Abaixo está a **documentação completa em formato `.md`**, já **consolidada**, cobrindo **chunking de áudio, logging, transparência de progresso e performance**, alinhada ao padrão do projeto, sem duplicações e sem comportamento inventado.

👉 Você pode salvar exatamente este conteúdo como, por exemplo:
`DOCUMENTACAO_LOGS_E_CHUNKING.md`

---

```md
# Documentação — Chunking de Áudio e Logging de Progresso

**Projeto:** Gravador e Transcritor  
**Status:** Implementado e Ativo  
**Última atualização:** 2026-01-21  

Este documento descreve a **implementação de chunking de áudio** e de
**logging estruturado de progresso**, adotada para resolver problemas de
lentidão percebida, ausência de feedback visual e dificuldade de diagnóstico
durante transcrições longas em CPU.

As decisões aqui descritas **não alteram interfaces públicas**, **não inventam
comportamento** e **preservam a qualidade da transcrição**.

---

## 1. Problema Identificado

Durante a transcrição de arquivos de áudio longos (especialmente provenientes
do YouTube), foram observados os seguintes problemas:

- Longos períodos sem qualquer saída no terminal
- Sensação de travamento do processo
- Dificuldade em identificar gargalos de performance
- Ausência de progresso percentual ou etapas visíveis
- Falta de logs técnicos para correção rápida

Esses problemas são inerentes ao funcionamento padrão do Whisper em CPU,
que **não fornece callbacks nativos de progresso**.

---

## 2. Decisão Técnica

### 2.1 Ativação de Chunking de Áudio

Foi adotado **chunking sequencial de áudio**, dividindo arquivos longos em
janelas fixas de tempo (chunks), processadas uma a uma.

**Motivações:**

- Permitir progresso visível (% concluído)
- Evitar perda total em caso de falha
- Melhorar percepção de responsividade
- Viabilizar logs granulares de performance

O chunking é implementado **exclusivamente no core de transcrição** e não
altera a interface pública do pipeline.

---

### 2.2 Logging Estruturado

Foi ativado logging estruturado para diagnóstico técnico, com as seguintes
diretrizes:

- `print()` → feedback humano (CLI)
- `logging` → diagnóstico técnico persistente
- Logs gravados em `logs/pipeline.log`
- Logs ativos por padrão
- Nível INFO (sem verbosidade excessiva)

---

## 3. Estrutura de Logs

```

logs/
└── pipeline.log

```

O diretório é criado automaticamente na execução.

---

## 4. Chunking de Áudio

### 4.1 Estratégia

- Tamanho fixo de chunk: **5 minutos (300s)**
- Processamento sequencial
- Concatenação do texto final
- Cada chunk é independente

### 4.2 Feedback no Terminal

Durante a execução, o usuário visualiza mensagens como:

```

[INFO] Áudio: 1834s | 7 chunks
[1/7] Transcrevendo 0s–300s (14%)
[2/7] Transcrevendo 300s–600s (28%)
...
[INFO] Transcrição concluída (100%)

```

Isso elimina completamente a sensação de travamento.

---

## 5. Logging de Performance

### 5.1 Por Chunk

Para cada chunk, são registrados:

- Índice do chunk
- Intervalo de tempo do áudio
- Tempo de processamento do chunk

Exemplo em log:

```

Chunk 3 processed in 42.18s

```

---

### 5.2 Por Etapa do Pipeline

O pipeline é dividido em etapas explícitas:

1. ASR (Whisper)
2. Refinadores
3. Persistência

Cada etapa tem seu tempo registrado:

```

Stage 1: ASR finished in 312.4s
Stage 2: Refiners finished in 4.2s
Pipeline finished in 328.9s

```

---

## 6. Transparência no Pipeline

O `transcribe_file.py` agora emite mensagens claras de progresso:

```

[PIPELINE] Etapa 1/3 — ASR
[PIPELINE] Etapa 2/3 — Refinadores
[PIPELINE] Etapa 3/3 — Salvando arquivos

```

Isso permite identificar rapidamente:
- Onde o processo está
- Onde está lento
- Se algo realmente travou

---

## 7. Impacto em Performance

### 7.1 Performance Real

- Chunking **não reduz significativamente** o tempo total bruto
- O ganho principal é:
  - percepção de progresso
  - resiliência
  - capacidade de diagnóstico

### 7.2 Performance Percebida

- Nenhum período longo de silêncio
- Feedback contínuo
- Confiança no processo em execução

---

## 8. Qualidade da Transcrição

- O modelo Whisper utilizado **não foi alterado**
- Parâmetros de decodificação permanecem conservadores
- Não há perda semântica ou lexical
- Refinadores continuam atuando normalmente

Chunking **não altera a qualidade do texto final**.

---

## 9. Alinhamento com Governança

Esta implementação está alinhada com:

- ADR-001 — Transcrição imutável
- ADR-003 — Chunking semântico (conceito aplicado ao áudio)
- DECISIONS.md — Robustez, previsibilidade e transparência

Não há quebra de contratos nem alteração de interface pública.

---

## 10. Conclusão

Com a adoção de chunking de áudio e logging estruturado:

- O pipeline tornou-se transparente
- A correção de problemas ficou mais rápida
- A experiência do usuário melhorou drasticamente
- A arquitetura permaneceu estável e previsível

Este documento deve ser consultado sempre que houver ajustes relacionados
a performance, logging ou transcrição de áudio longo.


exemplo real

(.venv311) C:\gravador_transcritor>python tests\download_and_transcribe_youtube.py
▶ Baixando áudio do YouTube...
[youtube] Extracting URL: https://www.youtube.com/watch?v=EIp1YZpJ2Mw
[youtube] EIp1YZpJ2Mw: Downloading webpage
[youtube] EIp1YZpJ2Mw: Downloading tv client config
[youtube] EIp1YZpJ2Mw: Downloading player c1c87fb0-main
[youtube] EIp1YZpJ2Mw: Downloading tv player API JSON
[youtube] EIp1YZpJ2Mw: Downloading android sdkless player API JSON
WARNING: [youtube] EIp1YZpJ2Mw: Some web client https formats have been skipped as they are missing a url. YouTube is forcing SABR streaming for this client. See  https://github.com/yt-dlp/yt-dlp/issues/12482  for more details
[info] EIp1YZpJ2Mw: Downloading 1 format(s): 251
[download] C:\gravador_transcritor\output\audio\youtube_teste.wav has already been downloaded
[ExtractAudio] Destination: C:\gravador_transcritor\output\audio\youtube_teste.wav
Deleting original file C:\gravador_transcritor\output\audio\youtube_teste.orig.wav (pass -k to keep)
▶ Iniciando transcrição...
[PIPELINE] Iniciando transcrição
[PIPELINE] Etapa 1/3 — ASR
[INFO] Carregando modelo Whisper: small
[INFO] Áudio: 2315s | 8 chunks
[1/8] Transcrevendo 0s–300s (12%)
[2/8] Transcrevendo 300s–600s (25%)
