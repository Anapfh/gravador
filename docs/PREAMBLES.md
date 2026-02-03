# Preambulos Disponiveis

Este documento lista os preambulos padrao usados no pipeline de resumo/ata.

## Tipos de reuniao
- daily -> preambles/preamble_daily.txt
- reuniao_interna -> preambles/preamble_reuniao_interna.txt
- reuniao_externa -> preambles/preamble_reuniao_externa.txt
- outro -> preambles/preamble_generico.txt
- kickoff -> preambles/preamble_kickoff.txt
- planejamento_sprint -> preambles/preamble_planejamento_sprint.txt
- retrospectiva -> preambles/preamble_retrospectiva.txt
- incidente_postmortem -> preambles/preamble_incidente_postmortem.txt
- one_on_one -> preambles/preamble_one_on_one.txt

## Regras
- O preambulo e carregado apenas em memoria.
- O preambulo nunca e persistido em disco junto da transcricao.
- Refinadores sempre executam antes do LLM.
