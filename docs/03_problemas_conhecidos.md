# Problemas conhecidos

Este documento lista problemas ja observados e como resolver rapidamente.

## 1. PyAudio nao instala via pip

Sintoma:
1. Erros de compilacao ou falta de build tools.

Causa:
1. No Windows, o PyAudio precisa de wheel compativel.

Solucao:
1. Baixar wheel `PyAudio-0.2.14-cp311-cp311-win_amd64.whl` no GitHub.
2. Instalar com `pip install .\wheels\PyAudio-0.2.14-cp311-cp311-win_amd64.whl`.

## 2. ctranslate2 tenta carregar ROCm

Sintoma:
1. Erro de DLL ou tentativa de backend ROCm em Windows.

Solucao:
1. Forcar CPU na chamada do CLI: `--device cpu --compute-type int8`.
2. Confirmar que o pacote instalado eh CPU-only.

## 3. Acentuacao quebrada em transcricao

Sintoma:
1. Texto com caracteres como `GravaÃ§Ã£o`.

Causa:
1. Leitura do arquivo com encoding incorreto.

Solucao:
1. O arquivo ja eh salvo com `utf-8-sig`.
2. No PowerShell, leia com `Get-Content output\transcricao.txt -Encoding UTF8`.

## 4. Aviso do Git no VS Code

Sintoma:
1. VS Code informa que ha muitos arquivos e limita recursos do Git.

Causa:
1. Muitos arquivos grandes ou binarios dentro do repo, como venvs e wheels.

Solucao:
1. Ajustar `.gitignore` para excluir `venv`, `wheels`, `logs`, `output` e caches.
2. Opcionalmente mover venv para fora do repo.

## 5. Microfone nao inicia

Sintoma:
1. Erro ao abrir device ou capturar audio.

Causa comum:
1. Permissao de microfone desativada no Windows.

Solucao:
1. Habilitar permissao de microfone no sistema.
2. Confirmar o device correto com `--mic-index`.

