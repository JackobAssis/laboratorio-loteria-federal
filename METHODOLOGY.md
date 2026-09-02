# Metodologia

1. **Coleta**: `LocalFileSource` ou `OfficialSource` → `Parser` → `Validator` → `Repository`. Hash SHA256 + metadata (fonte, período) registrados.
2. **Descritiva**: frequência 0–9 global e por posição, pares/trincas, terminações 1–4d, faixas, soma dígitos, paridade, repetições, sequências.
3. **Atraso (gap)**: calcula concursos desde última ocorrência; testa H0: gaps ~ Geométrica(p) via KS; nunca converte gap em probabilidade aumentada.
4. **Aleatoriedade**: Chi2 uniformidade, Chi2 independência, runs test, autocorrelação lag1, permutation/bootstrap.
5. **Probabilidade**: teórica (uniforme 1/100k por prêmio, binomial para paridade, DP para soma) vs empírica (Wilson 95%). `ProbabilityComparison` testa p_hat = p_teorica.
6. **Múltiplos testes**: Bonferroni e BH disponíveis; documentar método escolhido.
7. **Estratégias vs baseline**: random, frequency, recency, distribution, combined — todas comparadas contra random com IC e teste t/Mann-Whitney.
8. **Backtest**: para N, só dados <N. Métricas: acertos, custo, retorno, ROI, drawdown. Walk-forward com janela deslizante.
9. **Overfitting**: treino/validação/teste temporal, penalidade complexidade no score.
10. **Relatório**: `ReportGenerator` monta MD com H0/H1, p-values, IC, interpretação e resposta final: “há evidência?” Se p≥0.05 → “Não foi encontrada evidência suficiente” (resultado válido).
