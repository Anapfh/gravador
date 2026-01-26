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

## Issue 4 — Transcrição no Streamlit
- [x] Transcrição automática pós-gravação
- [x] Transcrição manual via botão
- [x] Salvamento em output/transcripts
- [x] Logs e tratamento de erro
- [x] Pipeline estável
## Bundle Canônico

- raw: ATIVO
- refined: PLANEJADO (pasta refiners)
- summarization/meta: PLANEJADO (pasta summarizers)

O bundle raw é a fonte oficial e imutável da transcrição.
## 🔁 Troca de Contexto — 2026-01-26

Motivo:
- Complexidade crescente na integração Streamlit × CLI
- Código funcional, porém com ajustes estruturais necessários
- Decisão consciente para preservar estabilidade

Estado preservado:
- Core de gravação estável
- Transcrição local funcional
- Bundle RAW parcialmente integrado
- Recorder Streamlit criado

Próximo contexto:
- Consolidar app.py declarativo
- Validar UI sem bloqueio
- Fechar Etapa 1 (Bundle RAW)
## 🔁 Troca de Contexto — 2026-01-26

Motivo:
- Integração Streamlit × CLI exigiu ajustes estruturais
- Código funcional, porém com ciclo de execução incompatível com UI declarativa
- Decisão consciente para preservar estabilidade e clareza

Estado preservado:
- Core de gravação CLI estável
- Wrapper recorder_streamlit criado
- Transcrição local funcional
- Configuração TOML validada
- UI Streamlit renderizando corretamente

Próximo contexto:
- Finalizar Etapa 1 — Bundle Canônico RAW
- Consolidar geração automática pós-transcrição
- Iniciar Etapa 2 — refiners
