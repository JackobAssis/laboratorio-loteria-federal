# Laboratório Estatístico da Loteria Federal

**Laboratório didático** para demonstrar que, sob hipótese de independência, histórico não altera `1/100000 (0,001%)` por bilhete, medir custo de ilusões (falácia do jogador, overfitting) e fornecer ferramenta de **jogo responsável com atrito** — não um sistema de promessa.

> **Aviso legal 18+:** Se o sorteio for independente e aleatório, o histórico **NÃO** altera a probabilidade do próximo sorteio. Nenhum padrão sem `p<0.05 out-of-sample + BH` é vantagem. Cada bilhete tem `1/100000` fixo, ROI esperado `≈ -1`. Jogue com responsabilidade. **CVV 188 (24h) • www.cvv.org.br** • `federal gerar --aceite` exige 18+ e 3 caixas de aceite. Uso educacional.

## Princípios (com harm reduction)
- Separa probabilidade teórica vs frequência observada.
- Nunca usa falácia do jogador; atraso ≠ maior chance.
- Testa H0/H1 com p-value, IC, correção múltipla (Bonferroni/BH).
- Evita overfitting: treino/val/validação/teste temporal + walk-forward + penalidade complexidade.
- **Jogo responsável:** 18+, atrito 3 caixas (`aceite`, `18+`, `responsável`), rate-limit 10/min, custo `n*5 R$` e perda esperada exibidos, `POST /api/gerar` exige aceite, CLI `federal gerar --aceite`.
- Tudo reproduzível com `seed` + `hash` + `DATABASE_URL` (SQLite→Postgres).

## Arquitetura
`DATA → FEATURES → ESTATÍSTICA → PROBABILIDADE → ESTRATÉGIAS → SIMULAÇÃO → BACKTEST → RELATÓRIO`

```
src/federal_lab/
  config/        # Settings (pydantic, .env)
  data/          # collector, parser, validator, repository (SQLite)
  statistics/    # frequency, distribution, independence, significance, confidence, correlations
  probability/   # theoretical, empirical, comparisons
  features/      # digits, endings, ranges, parity, sums, repetitions
  strategies/    # random, frequency, recency, distribution, combined
  simulation/    # monte_carlo, backtest, benchmark
  ranking/       # scoring, ranking (experimental)
  reports/       # generator, charts
  cli/           # federal fetch/validate/analyze/...
```

## Instalação
```bash
python -m venv .venv && source .venv/bin/activate
pip install -e ".[dev,ml,web]"
# ou completo
pip install -e ".[dev,ml,web]" && pip install fastapi uvicorn jinja2 python-multipart tabulate scikit-learn
```

## Interface Web (nova)
Dashboard interativo em **FastAPI + Chart.js** (e alternativa Streamlit).
```bash
# FastAPI (recomendado)
federal web --port 8000
# abra http://127.0.0.1:8000 → dashboard, /docs → OpenAPI, /reports/*.png → gráficos
# ou
uvicorn federal_lab.web.app:app --reload --port 8000

# Streamlit
pip install streamlit
streamlit run src/federal_lab/web/streamlit_app.py
```
Endpoints: `GET /`, `GET /api/status|frequency|distribution|tests|probability|overfitting|ml|report`, `POST /api/simulate|backtest|upload`.
Frontend: `src/federal_lab/web/templates/dashboard.html:1` (Tailwind + Chart.js, 6 abas: Estatística, Testes, Probabilidade, Monte Carlo, Backtest, Overfitting/ML), upload CSV/JSON drag-and-drop.

## Uso CLI
```bash
federal fetch --file data/raw/federal.csv          # importa
federal validate
federal analyze
federal probability
federal simulate --strategy random --iterations 10000
federal backtest --strategies random,frequency,combined
federal compare --strategies random,frequency,recency
federal report   # gera reports/relatorio.md + PNGs
federal web --port 8000  # inicia dashboard
```

## Dados
- CSV esperado: `concurso,data,posicao,numero,valor,tipo_extracao` — `data/raw/federal_exemplo.csv` (100) e `federal_escala.csv` (600)
- Banco: `data/database/federal.db` (SQLite) ou `DATABASE_URL=postgresql://...` (Postgres via `psycopg[binary]`, `Repository` detecta e usa `ON CONFLICT`)
- Hash SHA256 + `coleta_metadata` detecta alteração histórica.
- Fonte oficial `servicebus.caixa.gov.br` com fallback cache (evita scraping frágil).

## Metodologia
Ver `METHODOLOGY.md`, `STATISTICS.md`, `ARCHITECTURE.md`, `LIMITATIONS.md`.

## Testes
```bash
pytest -q
```

## Reproducibilidade
Todas simulações aceitam `--seed`. Backtest nunca usa dado futuro (corte temporal estrito).

## Limitações
Ver `LIMITATIONS.md` — não prometer lucro; ML só após estatística clássica validada.
