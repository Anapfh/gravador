# Fase 1: gravacao e transcricao

A Fase 1 cobre o ciclo completo: inicializar microfone, gravar, transcrever e finalizar sem crash.

## Fluxo tecnico

1. O microfone eh inicializado com SpeechRecognition + PyAudio.
2. O audio eh gravado por tempo fixo ou ate silencio.
3. O audio bruto eh convertido em WAV temporario.
4. O faster-whisper transcreve em CPU (int8).
5. O texto final eh salvo em `output/transcricao.txt`.

## Comando de teste final

```powershell
python core/cli/mic_cli.py --duration 10
```

Saida esperada no log:
1. Indicacao de gravacao do microfone.
2. Salvamento do WAV temporario.
3. Deteccao de idioma.
4. Salvamento da transcricao.

Arquivo de saida:
1. `output/transcricao.txt`

## Observacao de encoding

A transcricao eh escrita com UTF-8 com BOM (`utf-8-sig`) para evitar caracteres quebrados ao abrir no Notepad e no PowerShell antigo.

Exemplo de leitura correta no PowerShell:

```powershell
Get-Content output\transcricao.txt -Encoding UTF8
```

