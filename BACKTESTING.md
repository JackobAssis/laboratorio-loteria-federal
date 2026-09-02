# Backtesting

- **Regra**: para testar concurso N, dados disponíveis = concursos `< N`. Seleção calculada antes de revelar N.
- **Loop**: `Backtester.run(df, estrategia, min_history=20)` retorna por concurso: selecao, sorteados, acertos, custo, retorno, ROI, drawdown, ROI acumulado.
- **Walk-forward**: `walk_forward(train_size=50, test_size=10)` janela deslizante — detecta overfitting (performance cai fora da amostra = overfit).
- **Métricas**: média/mediana/desvio ROI, IC via t, ROI total, taxa acerto, distribuição. `Benchmark.compare_backtests` agrega; `significancia_vs_baseline` faz Mann-Whitney + t-test.
- **Overfitting**: separar treino/validação/teste temporal; penalidade complexidade no `Scorer`; comparar múltiplos testes com BH.
- **Causalidade**: histórico não causa futuro se sorteio independente; backtest mede apenas aderência amostral.

Reproduzível: seed fixa; hash dos dados registrado.
