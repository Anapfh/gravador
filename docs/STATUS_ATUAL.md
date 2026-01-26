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

# Status Atual do Projeto

## Última Issue Concluída
Issue 4 — Configuração via TOML

## Estado do Sistema
- Gravação local estável
- Streamlit MVP funcional
- Transcrição Whisper local funcional
- Configuração via TOML validada e logada

## Decisões Consolidadas
- Core não recebe idioma forçado
- TOML é opcional
- Defaults seguros no código
- Logs obrigatórios para rastreabilidade

## Próxima Issue
Issue 2 — Pausar / Retomar gravação via UI

## Observação
Troca de contexto realizada para segurança e continuidade.

## Última Issue Concluída
Issue 2 — Pausar / Retomar gravação via UI

## Estado Atual
- Gravação local com pause/resume estável (CLI)
- Core preservado, stream contínuo
- WAV único garantido
- Thread-safe (Event-based)

## Observações
- main.py oficialmente deprecado
- Streamlit não impactado

## 🔁 Troca de Contexto / Continuidade

- Data: YYYY-MM-DD
- Motivo da troca de contexto:
  (ex: estouro de contexto, troca de prompt, reinicialização da sessão)

- Estado do projeto no momento da troca:
  - Última issue concluída:
  - Issue em andamento:
  - Código estável até:
  - Pendências abertas:

- Riscos conhecidos:
  - (ex: documentação a unificar, testes pendentes, refatoração planejada)

- Próximos passos claros:
  1.
  2.
  3.

