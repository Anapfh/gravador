# Roadmap

Este roadmap descreve apenas itens planejados e nao implementados.

## Fase 2 (concluida): gravacao longa e controle de pausa

Objetivo:
1. Suportar gravacao longa por chunks de tempo.
2. Manter continuidade logica na transcricao.
3. Permitir pausa e retomada sem gerar audio vazio.

Decisoes propostas:
1. Chunk padrao de 10 minutos (ajustavel para 5).
2. CLI separada para modo longo, mantendo o CLI atual intacto.
3. Pausa via teclado (P/R/Q) no modo longo.

Saidas esperadas:
1. WAVs sequenciais por chunk.
2. Transcricoes por chunk.
3. Transcricao final agregada em arquivo unico.

## Fase 3 (concluida): refinadores + pipeline governado

Inclui:
1. Pipeline de resumo/ata com refinadores antes do LLM.
2. Preâmbulos por tipo de reuniao (catalogo em docs/PREAMBLES.md).
3. Integracao no Streamlit.

Saidas esperadas:
1. Resumo/ata em Markdown por sessao.

Objetivo:
1. Limpeza de oralidade e repeticoes.
2. Segmentacao para legibilidade.
3. Correcoes terminologicas por dominio.

Saidas esperadas:
1. Texto final refinado.
2. Arquivos auxiliares de metrics e logs.

## Fase 4 (planejada): sumarizacao

Objetivo:
1. Resumos estruturados por topicos.
2. Atas e highlights de reunioes.
3. Opcional integracao com modelos locais.

## Fase 5 (planejada): diarizacao

Objetivo:
1. Separar falas por participante.
2. Integrar diarizacao antes da transcricao por segmento.
3. Avaliar impacto de performance em CPU.
## Fase 1 — Gravação e Transcrição
Status: ✅ Concluída

- Gravação via microfone funcional
- Transcrição com faster-whisper (CPU / int8)
- Encoding UTF-8 corrigido
- CLI validada no Windows
