DECISION_DIARIZATION_POC.md

# DECISÃO TÉCNICA — POC de Diarização para Reuniões (Etapa 2.2)

## 📌 Contexto

Durante testes com transcrição de reuniões corporativas (Teams),
foi identificado que, mesmo com o áudio contendo claramente mais de um falante,
a transcrição gerada pelo Whisper apresenta predominantemente apenas a fala
do locutor dominante.

Os logs do pipeline indicam uso intensivo de VAD (Voice Activity Detection),
com descarte significativo de trechos de áudio, o que é esperado em cenários
de reuniões online com múltiplos participantes, compressão e cancelamento de eco.

Esse comportamento é aceitável para cenários de fala individual,
mas **insuficiente para reuniões corporativas**, como as realizadas na Vale.

---

## 🔍 Evidência técnica observada

Exemplos recorrentes nos logs:

- `VAD filter removed XX:YY of audio`
- Grande número de segmentos com apenas um fluxo textual
- Falta de representação consistente de múltiplos falantes

Apesar disso:
- O áudio original contém claramente mais de uma voz
- O problema não está na captura, mas no processamento

---

## ❌ Alternativas consideradas e descartadas

### 1. Ajustar sensibilidade de microfone
Descartado, pois o áudio já contém as falas de todos os participantes.

### 2. Desativar ou reduzir VAD
Descartado como solução definitiva:
- Aumenta ruído
- Prejudica qualidade do texto
- Não resolve separação de falantes

### 3. Refino estrutural ou sumarização
Descartado como solução para este problema específico,
pois atua após a transcrição e não corrige perda de fala.

---

## ✅ Decisão adotada

Foi decidido seguir com uma **Prova de Conceito (POC) de diarização**,
utilizando a combinação:

- **pyannote.audio** — para identificação de falantes e segmentação temporal
- **faster-whisper** — para transcrição de cada segmento diarizado

Essa abordagem segue o **padrão de mercado** para transcrição de reuniões,
utilizado por soluções como Otter.ai, Fireflies e plataformas corporativas.

---

## 🧩 Arquitetura prevista (alto nível)

Áudio da reunião
↓
Diarização (pyannote)
↓
Segmentos por falante (timestamps + speaker_id)
↓
Transcrição por segmento (Whisper)
↓
Refino estrutural determinístico
↓
[Opcional] Sumarização com preâmbulos


---

## 🎯 Objetivo da POC

Validar se a diarização:

- Captura falas de múltiplos participantes
- Reduz perda de conteúdo relevante
- Mantém qualidade aceitável de transcrição
- É viável computacionalmente no ambiente atual (CPU)

A POC **não altera o pipeline principal** e será conduzida de forma isolada.

---

## 🚫 Fora de escopo da POC

- Integração imediata com UI (Streamlit)
- Ajustes finos de performance
- Identificação nominal de falantes
- Persistência definitiva do novo formato

Esses pontos serão avaliados apenas após validação da POC.

---

## 🧠 Impacto esperado

- Melhoria significativa na cobertura de falas em reuniões
- Base sólida para atas, resumos e decisões
- Preparação do pipeline para cenários corporativos reais

---

## 📍 Próximo passo

Após o registro desta decisão:

1. Implementar a **POC de diarização em módulo isolado**
2. Testar com áudio real de reunião
3. Avaliar resultados qualitativos
4. Decidir sobre integração no pipeline principal

Este documento marca oficialmente o início da **Etapa 2.2 — Diarização (POC)**.
Decisão: ambientes segregados por função
Motivo: dependências de ML possuem ciclos de vida incompatíveis
Impacto: maior estabilidade, reprodutibilidade e facilidade de debug
Alternativas rejeitadas: ambiente único, uso de versões latest