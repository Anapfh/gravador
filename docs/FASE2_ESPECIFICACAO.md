# Fase 2 - Especificacao Tecnica

## Objetivo
Evoluir o projeto para suportar gravacao longa com continuidade e pausa/retomada, mantendo a Fase 1 intacta e estavel.

## Principios
1. Compatibilidade total com o fluxo atual (sem flags novas, comportamento identico).
2. Gravacao e transcricao continuam desacopladas.
3. CLI simples, sem dependencia de UI grafica.
4. Mudancas incrementais, isoladas e reversiveis.

## Escopo
### Inclui
1. Gravacao longa por chunks de tempo (padrao 10 minutos).
2. Sequenciamento de arquivos e transcricoes por chunk.
3. Concatenacao do texto final com continuidade logica.
4. Pausa e retomada via modo interativo de teclado.

### Nao inclui
1. Diarizacao.
2. Refinadores ou sumarizadores automaticos.
3. Mudancas no core atual de transcricao (faster-whisper).

## Arquitetura proposta
### Novos modulos
1. `core/recorder_long.py`
- Responsavel por capturar audio continuamente.
- Gera arquivos WAV por tempo fixo.
- Exponde callbacks ou eventos de ciclo (on_chunk_start, on_chunk_end).

2. `core/cli/mic_cli_long.py`
- Novo CLI para gravacao longa.
- Orquestra chunking, transcricao e agregacao.
- Nao altera `core/cli/mic_cli.py`.

### Integracao com transcricao
- Cada chunk gera um WAV fechado.
- A transcricao roda por chunk, em ordem.
- Saidas:
  - `output/audio/<session>_chunk_001.wav`
  - `output/transcripts/<session>_chunk_001.txt`
  - `output/transcripts/<session>_full.txt`

## Parametros de CLI planejados
1. `--long`
Ativa o modo de gravacao longa.

2. `--chunk-minutes 10`
Define duracao de cada chunk. Valores recomendados: 5 a 10 minutos.

3. `--session-name reuniao_geral`
Nome base dos arquivos da sessao.

4. `--pause-mode keyboard`
Modo de pausa. Inicialmente apenas `keyboard`.

5. `--transcribe-mode inline|queue`
Inline transcreve ao fim de cada chunk. Queue transcreve ao final da sessao.

## Modo pausa/retomar
### Modo interativo (teclado)
- `P` para pausar.
- `R` para retomar.
- `Q` para finalizar.

### Comportamento esperado
1. Ao pausar, o WAV atual e fechado e persistido.
2. Nenhum audio e gravado enquanto pausado.
3. Ao retomar, inicia novo chunk com novo indice.

## Logs e observabilidade
1. Log de inicio e fim de cada chunk.
2. Log de eventos de pausa e retomada.
3. Log de transcricao por chunk e agregacao final.

## Riscos e mitigacoes
1. Perda de audio ao pausar
- Mitigacao: flush e fechamento imediato do WAV antes de pausar.

2. Drift de tempo entre chunks
- Mitigacao: usar timestamps e indice sequencial, sem sobreposicao.

3. Latencia de transcricao
- Mitigacao: permitir `--transcribe-mode queue`.

4. Arquivos grandes demais
- Mitigacao: chunk padrao 10 minutos, com possibilidade de 5.

## Criterios de aceite
1. `mic_cli.py` continua funcionando sem mudanca de comportamento.
2. `mic_cli_long.py` grava por 30+ minutos com 0 perda.
3. Chunks e transcricoes numerados corretamente.
4. Pausa e retomada funcionam sem gerar audio vazio.
5. Transcricao final concatena todos os chunks em ordem.

