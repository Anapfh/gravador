# 🧭 BASELINE_PROJETOS_TECNICOS.md  
## Guia universal para estruturar projetos técnicos sem retrabalho

> Este baseline foi construído a partir de problemas reais de projeto, falhas de ambiente, conflitos de dependências e decisões técnicas mal resolvidas.  
> O objetivo é **evitar erros recorrentes** e **padronizar boas decisões desde o início**.

---

## 1. PRINCÍPIO FUNDAMENTAL

### ❗ Regra nº 1
**Ambiente é parte do código.**

Se o ambiente não está controlado:
- o projeto não é reprodutível
- erros aparecem “do nada”
- tempo é perdido em debug inútil

---

## 2. O ERRO MAIS COMUM EM PROJETOS

### ❌ Anti-padrão
> “Vou rodar `pip install` até funcionar”

Problemas dessa abordagem:
- pip **não resolve compatibilidade**
- versões transitivas entram em conflito
- reinstalar não corrige decisões erradas

📌 **pip executa ordens, não pensa.**

---

## 3. MODELO MENTAL CORRETO

### ✅ Novo modelo
> **Projeto = conjunto de decisões congeladas no tempo**

Inclui:
- versão do Python
- versão de cada biblioteca
- relação entre dependências

Nada é “latest” em projeto sério.

---

## 4. PADRÃO DE AMBIENTES (REGRA UNIVERSAL)

### 🔹 Princípio
**Um ambiente = um propósito**

Nunca misture domínios diferentes no mesmo ambiente.

### ✔ Estrutura recomendada
projeto/
├── .venv_app # UI, Streamlit, APIs
├── .venv_data # pandas, numpy, ETL
├── .venv_ml # torch, modelos, treino
├── .venv_nlp # LLMs, sumarização
└── docs/


📌 Ambientes quebrados **não se consertam**, se recriam.

---

## 5. REGRA DE OURO DO pip

### ❗ pip não decide versões por você

❌ Errado:
```bash
pip install torch
✅ Certo:

pip install torch==2.2.2
Sempre fixe versões de bibliotecas críticas.

6. CHECKLIST ANTES DE INSTALAR QUALQUER BIBLIOTECA
Antes de rodar pip install, responda:

Para que este pacote existe?

Ele depende de quem?

Em qual ambiente ele pertence?

Ele exige GPU, token ou sistema específico?

Ele é sensível à versão do Python?

Se não souber → pare.

7. FIXAÇÃO DE VERSÕES (PADRÃO DE MERCADO)
Regra prática
Core do projeto → versão fixa

Infraestrutura → versão fixa

Auxiliares → podem variar

Exemplo:

python==3.10
numpy==1.26.4
torch==2.2.2
torchaudio==2.2.2
8. COMO REALMENTE RESOLVER CONFLITOS
✔ Estratégia correta
Criar ambiente novo

Instalar mínimo possível

Testar

Evoluir gradualmente

Nunca tente “consertar” um ambiente quebrado.

9. ORDEM CORRETA DE DEBUG
Sempre siga esta ordem:

Ambiente

Versões

Dependências

Dados de entrada

Código

⚠️ Código raramente é o problema inicial.

10. REGRA DOS WARNINGS
❗ Novo baseline
Warning é bug avisando antes

Ignorar warning:

gera dívida técnica

quebra o projeto no futuro

11. ADOÇÃO DE TECNOLOGIAS NOVAS
Antes de adotar qualquer lib/framework, avalie:

Depende de GPU?

Depende de token?

Modelo é gated/privado?

Sensível a versão de torch/numpy?

Se sim → isole em ambiente próprio.

12. DOCUMENTAÇÃO DE DECISÕES
Toda decisão técnica relevante deve gerar um registro:

por que foi escolhida

alternativas descartadas

impactos conhecidos

Padrão recomendado:

docs/
├── ADR_001_ambientes.md
├── ADR_002_dependencias.md
13. MAIOR LIÇÃO APRENDIDA
Projetos quebram mais por ambiente do que por código.

Ambiente mal definido = projeto instável.

14. RESUMO EM UMA FRASE
Se não está versionado, não está controlado.

15. COMO USAR ESTE BASELINE EM QUALQUER PROJETO
Defina o problema

Separe por domínios

Crie ambientes isolados

Fixe versões

Documente decisões

Só então escreva código

16. STATUS DO BASELINE
✔ Validado em projeto real
✔ Reutilizável
✔ Independente de stack
✔ Aplicável a dados, ML, apps e automação

Este documento deve ser lido antes de iniciar qualquer novo projeto técnico.


---

Se quiser, no próximo passo eu posso:

- transformar isso em **template oficial de repositório**
- criar um **checklist operacional (`START_PROJECT.md`)**
- gerar um **ADR inicial padrão**
- ou adaptar este baseline especificamente para **dados / ML / apps**

Você agora tem um **mapa** — e isso muda tudo.
::contentReference[oaicite:0]{index=0}