# 📌 Status do Projeto — Configuração via TOML

## Última Issue Trabalhada
Issue 4 — Configuração via TOML

## Estado atual
- Transcrição Whisper local estável
- Streamlit MVP funcional
- Configuração centralizada em `config/transcription.toml`
- Defaults seguros mantidos no código

## Decisões consolidadas
- Idioma Whisper é automático
- TOML é opcional
- Core não recebe parâmetros inválidos
- Refinadores são controlados via config

## Arquivos impactados
- config/transcription.toml
- transcriber.py

## Próximo passo sugerido
- Testar variações de config
- Avaliar exposição de config na UI (futuro)
- Depois seguir para Issue 2 (Pause/Resume)
