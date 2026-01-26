# DOCUMENT_MAP.md

Mapa de documentos do projeto.

- PROJECT_GUARDRAILS.md → regra suprema
- CONTRACTS.md → contratos técnicos
- DECISIONS.md → decisões irreversíveis
- POSTMORTEM_*.md → causas e correções
- LESSONS_LEARNED_*.md → aprendizado consolidado
- ADR-002.md → ata corporativa
- ANTI_HALLUCINATION_POLICY.md → controle de IA
- CHANGE_CHECKLIST.md → evolução segura

### Protocolos de Continuidade

- `PROJECT_RULES.md` → Regras oficiais do projeto
- `STATUS_ATUAL.md` → Estado vivo + Troca de Contexto
- `DECISIONS.md` → Decisões técnicas consolidadas

⚠️ Nenhum novo documento deve ser criado para tratar de continuidade ou
troca de contexto fora desses arquivos.
- core/ → áudio e ASR
- refiners/ → pós-processamento determinístico
- summarizers/ → LLM local (Ollama)
- app.py → UX Streamlit
