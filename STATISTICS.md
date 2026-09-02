# Estatística — Testes Disponíveis

Cada teste define H0/H1, premissas e limitações.

- **Chi2 uniformidade** (`significance.chi_square_uniform`): H0 uniforme 0–9. Requer n≥50 e esperados ≥5.
- **Chi2 independência** (`independence.chi2_independencia`): tabela contingência (ex d1×d5).
- **Runs test**: mediana como corte; H0 sequência aleatória; sensível a tendência.
- **Autocorrelação lag1**: Pearson r entre série e lag; t-test.
- **KS geométrico (gaps)**: compara distribuição empírica de gaps vs Geométrica(p=1/média); H0 processo aleatório sem memória.
- **Permutation / Bootstrap**: não-paramétricos para diferença de médias e IC.
- **Wilson / Clopper-Pearson**: IC 95% para proporções (ex terminações).
- **Correção múltipla**: Bonferroni (conservador) e Benjamini-Hochberg FDR.

Interpretação: p<0.05 rejeita H0, mas sem out-of-sample e sem correção pode ser falso positivo (procurar evidência *contra* a estratégia é obrigatório).
