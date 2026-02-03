@echo off
cd /d C:\gravador_transcritor

call .venv311_ok\Scripts\activate.bat

streamlit run app.py

echo.
echo Processo encerrado. Pressione qualquer tecla para sair...
pause > nul

