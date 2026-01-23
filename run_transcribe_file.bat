@echo off
REM Gera resumo/MD a partir de uma transcricao .txt usando summarize_transcript.py (Gemma).

cd /d C:\gravador_transcritor
call .venv311\Scripts\activate.bat

echo ==============================================
echo   GERAR RESUMO / MD (Gemma)
echo ==============================================
echo.
echo Opcional: informe o caminho do arquivo .txt
echo de transcricao (ENTER para usar o mais recente
echo em output\transcripts):
set /p TXT_PATH=

if "%TXT_PATH%"=="" (
    echo.
    echo Nao informado. Buscando o .txt mais recente em output\transcripts...
    for /f "delims=" %%A in ('dir /b /a-d /o-d "output\transcripts\*.txt" 2^>nul') do (
        set LATEST_TXT=output\transcripts\%%A
        goto FOUND_TXT
    )
    echo Nenhum arquivo .txt encontrado em output\transcripts.
    goto END
) else (
    set LATEST_TXT=%TXT_PATH%
)

:FOUND_TXT
if not exist "%LATEST_TXT%" (
    echo Arquivo de transcricao nao encontrado: %LATEST_TXT%
    goto END
)

echo.
echo Arquivo de transcricao selecionado:
echo   %LATEST_TXT%
echo.

echo Tipo de sessao para o resumo:
echo   treinamento
echo   reuniao_interna
echo   reuniao_externa
echo   curso
echo   outro
echo.
echo Informe o tipo de sessao [treinamento]:
set /p SESSION_TYPE=
if "%SESSION_TYPE%"=="" set SESSION_TYPE=treinamento

echo.
echo Titulo/assunto para o resumo (ex: Treinamento UN8 - Sinalizacao e Circulacao de Mina):
set /p TITLE=
if "%TITLE%"=="" set TITLE=Sessao

echo.
echo Deseja anexar a transcricao completa no final do .md? [S/N] (padrao: N):
set /p ATTACH_TXT=
if /I "%ATTACH_TXT%"=="S" (
    set ATTACH_FLAG=--anexar-transcricao
) else (
    set ATTACH_FLAG=
)

echo.
echo >> Gerando resumo com Gemma...
python summarize_transcript.py -i "%LATEST_TXT%" -t "%SESSION_TYPE%" -s "%TITLE%" %ATTACH_FLAG%

:END
echo.
echo Processo encerrado. Pressione qualquer tecla para sair...
pause > nul

