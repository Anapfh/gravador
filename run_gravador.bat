@echo off
REM Executa o fluxo completo: gravar audio do sistema e opcionalmente transcrever.

REM === Ajuste se o caminho do projeto/venv mudar ===
cd /d C:\gravador_transcritor

call .venv311\Scripts\activate.bat

if not exist "main.py" (
    echo main.py nao encontrado em C:\gravador_transcritor
    goto :END
)

python main.py

:END
echo.
echo Processo encerrado. Pressione qualquer tecla para sair...
pause > nul

