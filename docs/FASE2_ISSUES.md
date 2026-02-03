# Fase 2 - Issues Tecnicas (Checklist)

## Epic: Gravacao longa com continuidade
- [ ] Definir duracao padrao de chunk (recomendado 10 minutos)
- [ ] Implementar geracao de WAVs sequenciais por tempo
- [ ] Padrao de nomes para sessao e chunks
- [ ] Persistencia de WAVs com fechamento seguro
- [ ] Transcricao por chunk em ordem
- [ ] Agregacao do texto final em arquivo unico
- [ ] Logs de inicio/fim por chunk

## Epic: Pausar e retomar gravacao
- [ ] Definir interface de controle (teclado)
- [ ] Implementar comandos P/R/Q no CLI longo
- [ ] Garantir fechamento do WAV ao pausar
- [ ] Retomar sempre em novo chunk
- [ ] Logar eventos de pausa/retomada

## Epic: CLI e compatibilidade
- [ ] Criar `core/cli/mic_cli_long.py`
- [ ] Manter `core/cli/mic_cli.py` inalterado
- [ ] Flags novas para `mic_cli_long.py`
- [ ] Documentar uso no docs/99_roadmap.md

## Epic: Testes e validacao manual
- [ ] Teste 30 minutos com chunks de 10 minutos
- [ ] Teste 15 minutos com chunks de 5 minutos
- [ ] Teste com pausa/retomada 3x
- [ ] Validar ausencia de audio vazio
- [ ] Validar transcricao concatenada correta

