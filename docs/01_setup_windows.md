# Setup no Windows

Este guia prepara o ambiente para executar a Fase 1 com microfone e transcricao local em CPU.

## 1. Criar e ativar o venv

```powershell
python -m venv .venv311_ok
.\.venv311_ok\Scripts\Activate.ps1
python -m pip install --upgrade pip
```

## 2. Instalar dependencias do projeto

```powershell
python -m pip install -r requirements.txt
```

## 3. Instalar PyAudio via wheel (GitHub)

No Windows, o PyAudio costuma falhar se tentar compilar. O fluxo correto eh usar wheel pronto para Python 3.11 e Windows 64-bit.

Exemplo de wheel compativel:
1. `PyAudio-0.2.14-cp311-cp311-win_amd64.whl`

Fluxo sugerido:
1. Baixe o wheel nas releases do GitHub do PyAudio.
2. Coloque o arquivo em `wheels/`.
3. Instale com pip.

```powershell
python -m pip install .\wheels\PyAudio-0.2.14-cp311-cp311-win_amd64.whl
```

Teste imediato:

```powershell
python -c "import pyaudio; print('PyAudio OK')"
```

## 4. Workaround ctranslate2 no Windows (ROCm)

Em alguns ambientes Windows, o ctranslate2 pode tentar carregar backend ROCm e falhar. O workaround adotado no projeto eh forcar CPU no nivel do modelo e do CLI.

Pontos garantidos no codigo:
1. `core/whisper_core.py` usa `device=cpu` e `compute_type=int8`.
2. No CLI, o parametro `--device cpu` e aceito e pode ser usado para reforcar o comportamento.

Exemplo:

```powershell
python core/cli/mic_cli.py --duration 10 --device cpu --compute-type int8
```

Esse ajuste elimina a tentativa de carregar ROCm e mantem a inferencia estavel em CPU.

## 5. Correcao de encoding UTF-8 na saida

A gravacao da transcricao usa encoding explicito para evitar texto corrompido no Windows. O arquivo final eh salvo como UTF-8 com BOM para compatibilidade com editores antigos.

Trecho relevante:

```python
output_path.write_text(text, encoding="utf-8-sig")
```

## 6. Rodar a interface Streamlit (app.py)

```powershell
.\.venv311_ok\Scripts\Activate.ps1
streamlit run app.py
```

Opcional (atalho via batch):

```powershell
run_app_streamlit.bat
```

