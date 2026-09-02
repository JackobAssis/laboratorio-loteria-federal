# Relatório — Laboratório Estatístico da Loteria Federal

> Se o processo de sorteio for independente e aleatório, o histórico NÃO altera a probabilidade do próximo sorteio.

Gerado em: 2026-09-02 18:51

## 1. Resumo
- Concursos analisados: 600
- Período: 2020-01-04 a 2024-12-05
- Fonte: local
- Hash dados: `5f9bd0f63d819d76`

## 2. Dados
- Total de prêmios (linhas): 3000
- Tipo extração predominante: regular

## 3. Estatística Descritiva
### Frequência de algarismos (0-9)
|   algarismo |   observado |   frequencia |   esperado_freq |   esperado_abs |
|------------:|------------:|-------------:|----------------:|---------------:|
|           0 |        1515 |    0.101     |             0.1 |           1500 |
|           1 |        1457 |    0.0971333 |             0.1 |           1500 |
|           2 |        1571 |    0.104733  |             0.1 |           1500 |
|           3 |        1513 |    0.100867  |             0.1 |           1500 |
|           4 |        1519 |    0.101267  |             0.1 |           1500 |
|           5 |        1501 |    0.100067  |             0.1 |           1500 |
|           6 |        1466 |    0.0977333 |             0.1 |           1500 |
|           7 |        1475 |    0.0983333 |             0.1 |           1500 |
|           8 |        1548 |    0.1032    |             0.1 |           1500 |
|           9 |        1435 |    0.0956667 |             0.1 |           1500 |

### Frequência por posição (heatmap em reports/freq_posicao.png)
Ver heatmap reports/freq_posicao.png (esperado 0.10 por célula)

### Frequência por terminação (1 dígito)
|   terminacao |   observado |     freq |
|-------------:|------------:|---------:|
|            4 |         322 | 0.107333 |
|            2 |         318 | 0.106    |
|            0 |         317 | 0.105667 |
|            8 |         313 | 0.104333 |
|            9 |         311 | 0.103667 |

### Distribuição por faixa
| faixa              |   observado |     freq |   esperado |
|:-------------------|------------:|---------:|-----------:|
| (-84.88, 19991.0]  |         597 | 0.199    |        600 |
| (19991.0, 39967.0] |         591 | 0.197    |        600 |
| (39967.0, 59943.0] |         614 | 0.204667 |        600 |
| (59943.0, 79919.0] |         574 | 0.191333 |        600 |
| (79919.0, 99895.0] |         624 | 0.208    |        600 |

### Paridade (binomial n=5 p=0.5)
|   qtd_pares |   observado |   esperado |   freq_obs |   freq_esp |
|------------:|------------:|-----------:|-----------:|-----------:|
|           0 |          88 |      93.75 |  0.0293333 |    0.03125 |
|           1 |         447 |     468.75 |  0.149     |    0.15625 |
|           2 |         898 |     937.5  |  0.299333  |    0.3125  |
|           3 |         981 |     937.5  |  0.327     |    0.3125  |
|           4 |         497 |     468.75 |  0.165667  |    0.15625 |
|           5 |          89 |      93.75 |  0.0296667 |    0.03125 |

### Soma dígitos
- Média 22.38, mediana 22.00, desvio 6.41

Gráficos: `freq_algarismos.png`, `freq_posicao.png`, `finais_1d.png`, `finais_2d.png`, `dist_soma.png`, `dist_numeros.png`

## 4. Testes de Aleatoriedade (§7)
- Chi2 uniformidade dígitos: chi2=10.64, p=0.3014 — Não rejeita uniformidade (compatível com aleatório)
  - H0: distribuição uniforme (p=0.10 por dígito); H1: não uniforme. Limitação: sensível a n grande.
- Runs test (números inteiros): p=0.5109 — Aleatório
- Autocorrelação lag1: r=-0.0009, p=0.9622 — Sem autocorrelação
- Correlação concurso×soma: r=0.0469, p=0.0101

## 5. Probabilidade — Teoria vs Empírico (§8)
- IC 95% Wilson calculado para cada proporção (ex `ic_proporcao.png`).
- Exemplo: terminação 0 — p_hat=0.1057, p_teorica=0.1000, p_binom=0.3008 — Não rejeita H0 (compatível)
- Tabela completa qtd_pares vs teórica disponível em `ProbabilityComparison.tabela_completa`.

## 6. Atraso — Gap Analysis (§6)
> Nunca transformar automaticamente "atraso" em aumento de probabilidade.
- H0: intervalo entre ocorrências compatível com processo aleatório (Geométrica); H1: comportamento diferente.
- Ocorrências do dígito "7" (exemplo): n_gaps=1222, p_hat_gap=2.0401
- Teste KS geométrico: p=nan — Desvio de geométrico
- Conclusão: Sinal fraco — exige out-of-sample.
- Gráfico: `gaps_hist.png`

## 7. Simulações Monte Carlo (§9)
- Iterações solicitadas: 1000
- Estratégias avaliadas: random, frequency, recency, distribution, combined
- Resultados por estratégia em `monte_carlo.png` (quando aplicável). Seed=42.

## 8. Estratégias — Backtest Temporal (§10)
> Nunca usar informações futuras para selecionar apostas em N; dados < N apenas.
| estrategia   |   n_testes |   media_roi |   mediana_roi |   desvio_roi |   roi_total |   taxa_acerto |   media_acertos |   ci_low_roi |   ci_high_roi |
|:-------------|-----------:|------------:|--------------:|-------------:|------------:|--------------:|----------------:|-------------:|--------------:|
| random       |        580 |     2.44828 |            -1 |      83.0455 |     2.44828 |    0.00172414 |      0.00172414 |     -4.32438 |       9.22093 |
| frequency    |        580 |     2.44828 |            -1 |      83.0455 |     2.44828 |    0.00172414 |      0.00172414 |     -4.32438 |       9.22093 |
| recency      |        580 |    -1       |            -1 |       0      |    -1       |    0          |      0          |     -1       |      -1       |
| distribution |        580 |    -1       |            -1 |       0      |    -1       |    0          |      0          |     -1       |      -1       |
| combined     |        580 |    -1       |            -1 |       0      |    -1       |    0          |      0          |     -1       |      -1       |

### Significância vs Baseline (aleatório) — §13
- Sem diferença significativa (todas ROI idênticos ou p>=0.05).
- Teste: Mann-Whitney + t (Welch), α=0.05. Só interessante se superar baseline fora da amostra.

### Métricas adicionais por estratégia
| estrategia   |   n_testes |   media_roi |   roi_total |   taxa_acerto |
|:-------------|-----------:|------------:|------------:|--------------:|
| random       |        580 |     2.44828 |     2.44828 |    0.00172414 |
| frequency    |        580 |     2.44828 |     2.44828 |    0.00172414 |
| recency      |        580 |    -1       |    -1       |    0          |
| distribution |        580 |    -1       |    -1       |    0          |
| combined     |        580 |    -1       |    -1       |    0          |

Gráficos: `roi_benchmark.png`, `roi_acumulado.png`

## 9. Múltiplos Testes (§14)
- Correção Bonferroni e BH (FDR) via `SignificanceTester.corrigir_multiplos`.
- Exemplo (p-values dos testes acima): originais ['0.3014', '0.5109', '0.9622', '0.0101'] → Bonferroni ['1.0000', '1.0000', '1.0000', '0.0405'] → BH ['0.6028', '0.6813', '0.9622', '0.0405']
- Documentado método: BH é menos conservador, adequado quando muitos testes exploratórios.

## 10. Overfitting & Walk-Forward (§11)
- Walk-forward: `simulation.backtest.Backtester.walk_forward` (janela deslizante).
- Split temporal treino/val/teste (60/20/20): {'train': {'roi_total': np.float64(4.882352941176471), 'n': 340}, 'val': {'roi_total': np.float64(-1.0), 'n': 100}, 'test': {'roi_total': np.float64(-1.0), 'n': 100}}
- Diagnóstico overfitting: overfit_suspeito=True — Overfitting suspeito: bom in-sample, ruim out-of-sample. Não considerar promissora.
- Walk-forward estabilidade: media ROI por janela -1.0000, desvio 0.0000, % janelas positivas 0.0% — Instável ou não consistentemente positivo — provável overfit ou flutuação.

## 11. Machine Learning (§15)
- Status: executado
- Detalhe: {'acc_model': 0.8946666666666667, 'acc_dummy': 0.8937777777777778, 'scores_model': [0.88, 0.896, 0.908], 'scores_dummy': [0.8786666666666667, 0.896, 0.9066666666666666], 'leakage_ok': True, 'supera_baseline': False, 'complexidade': 'RandomForestClassifier (n_estimators=50)', 'conclusao': 'ML NÃO supera baseline fora da amostra — registrar como resultado (esperado se sorteio é aleatório). Não promover.'}
- Conclusão ML: ML NÃO supera baseline fora da amostra — registrar como resultado (esperado se sorteio é aleatório). Não promover.

## 12. Sistema de Score (§12)
- Score experimental = Σ peso*componente - penalidade_complexidade. Pesos: {'frequencia': 0.25, 'distribuicao': 0.25, 'recencia': 0.25, 'caracteristicas': 0.25, 'penalidade_complexidade': 0.1}. Tratado como ranking experimental, NÃO probabilidade real.

## 13. Conclusão (§22 — Regra de Ouro)
> **Pergunta:** Existe evidência estatística suficiente para afirmar que alguma estratégia apresenta vantagem sobre a seleção aleatória?
>
> **Resposta baseada nos dados:** NÃO foi encontrada evidência estatística suficiente para vantagem sobre aleatório (fora da amostra, com correção múltipla).

> Se não houver evidência: “Não foi encontrada evidência estatística suficiente.” — resultado válido.

---
*Relatório gerado automaticamente. Todos os cálculos reproduzíveis com seed configurável. Overfitting e viés de múltiplos testes foram considerados. Ver `METHODOLOGY.md`, `STATISTICS.md`, `LIMITATIONS.md`.*
