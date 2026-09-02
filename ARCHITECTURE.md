# Arquitetura

Fluxo: **coleta → validação → persistência → features → estatística → probabilidade → estratégias → simulação/backtest → ranking → relatório**

- `config.Settings`: única fonte de verdade (env `FEDERAL_*`).
- `data.Repository`: SQLite com esquema `concursos|premios|coleta_metadata|analises|simulacoes|backtests`. `insert_lote` é transacional.
- `data.DataSource`: interface desacoplada; `OfficialSource` tenta API Caixa, fallback para cache local (evita scraping frágil nos módulos estatísticos).
- `features.*`: extração sem leakage (apenas histórico).
- `statistics`: cada teste declara H0/H1, justificativa, limitações (ver `STATISTICS.md`).
- `probability`: `TheoreticalProbability` enumera 00000–99999 (100k combinações) para distribuição exata; `EmpiricalProbability` usa Wilson CI.
- `simulation`: `MonteCarloSimulator` com seed; `Backtester.run` itera concursos em ordem e nunca expõe futuro; `walk_forward` para overfitting.
- `ranking`: score experimental com penalidade de complexidade, nunca apresentado como probabilidade real.
