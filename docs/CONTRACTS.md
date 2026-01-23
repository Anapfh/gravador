# CONTRACTS.md

Contratos técnicos obrigatórios do projeto.

---

## Contrato de Áudio

- Captura no sample rate NATIVO do dispositivo
- Nunca forçar 16kHz na captura
- WAV em PCM_16
- Mono
- Sem normalização ou ganho

---

## Contrato de ASR

- Sempre retorna string
- Nunca retorna None
- Nunca apaga texto válido

---

## Contrato de Refinadores

- Nunca retornam string vazia se havia texto
- Falham com fallback
- Nunca inventam conteúdo

---

## Contrato do Orquestrador

- Nunca permite apagar texto válido
- Pipeline encerra se transcrição for vazia
