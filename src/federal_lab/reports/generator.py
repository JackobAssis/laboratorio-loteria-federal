"""Gerador de relatório Markdown — §17: estatísticas, testes, simulações, baseline, conclusão."""

from pathlib import Path

TEMPLATE = """# Relatório — Laboratório Estatístico da Loteria Federal

> {aviso}

Gerado em: {data}

## 1. Resumo
- Concursos analisados: {n_concursos}
- Período: {periodo}
- Fonte: {fonte}
- Hash dados: `{hash_dados}`

## 2. Dados
- Total de prêmios (linhas): {n_linhas}
- Tipo extração predominante: {tipo}

## 3. Estatística Descritiva
### Frequência de algarismos (0-9)
{tbl_freq}

### Frequência por posição (heatmap em reports/freq_posicao.png)
{tbl_freq_pos}

### Frequência por terminação (1 dígito)
{tbl_term1}

### Distribuição por faixa
{tbl_faixa}

### Paridade (binomial n=5 p=0.5)
{tbl_paridade}

### Soma dígitos
- Média {soma_media:.2f}, mediana {soma_mediana:.2f}, desvio {soma_desvio:.2f}

Gráficos: `freq_algarismos.png`, `freq_posicao.png`, `finais_1d.png`, `finais_2d.png`, `dist_soma.png`, `dist_numeros.png`

## 4. Testes de Aleatoriedade (§7)
- Chi2 uniformidade dígitos: chi2={chi2:.2f}, p={p_chi2:.4f} — {interp_chi2}
  - H0: distribuição uniforme (p=0.10 por dígito); H1: não uniforme. Limitação: sensível a n grande.
- Runs test (números inteiros): p={p_runs:.4f} — {interp_runs}
- Autocorrelação lag1: r={r_auto:.4f}, p={p_auto:.4f} — {interp_auto}
- Correlação concurso×soma: r={r_correl:.4f}, p={p_correl:.4f}

## 5. Probabilidade — Teoria vs Empírico (§8)
- IC 95% Wilson calculado para cada proporção (ex `ic_proporcao.png`).
- Exemplo: terminação 0 — p_hat={p_hat_term0:.4f}, p_teorica=0.1000, p_binom={p_binom:.4f} — {interp_term0}
- Tabela completa qtd_pares vs teórica disponível em `ProbabilityComparison.tabela_completa`.

## 6. Atraso — Gap Analysis (§6)
> Nunca transformar automaticamente "atraso" em aumento de probabilidade.
- H0: intervalo entre ocorrências compatível com processo aleatório (Geométrica); H1: comportamento diferente.
- Ocorrências do dígito "7" (exemplo): n_gaps={n_gaps}, p_hat_gap={p_hat_gap:.4f}
- Teste KS geométrico: p={p_gap:.4f} — {interp_gap}
- Conclusão: {conclusao_gap}
- Gráfico: `gaps_hist.png`

## 7. Simulações Monte Carlo (§9)
- Iterações solicitadas: {mc_iter}
- Estratégias avaliadas: {estrategias_mc}
- Resultados por estratégia em `monte_carlo.png` (quando aplicável). Seed={seed}.

## 8. Estratégias — Backtest Temporal (§10)
> Nunca usar informações futuras para selecionar apostas em N; dados < N apenas.
{tbl_bench}

### Significância vs Baseline (aleatório) — §13
{tbl_signif}
- Teste: Mann-Whitney + t (Welch), α=0.05. Só interessante se superar baseline fora da amostra.

### Métricas adicionais por estratégia
{tbl_metricas}

Gráficos: `roi_benchmark.png`, `roi_acumulado.png`

## 9. Múltiplos Testes (§14)
- Correção Bonferroni e BH (FDR) via `SignificanceTester.corrigir_multiplos`.
- Exemplo (p-values dos testes acima): originais {p_vals_orig} → Bonferroni {p_vals_bonf} → BH {p_vals_bh}
- Documentado método: BH é menos conservador, adequado quando muitos testes exploratórios.

## 10. Overfitting & Walk-Forward (§11)
- Walk-forward: `simulation.backtest.Backtester.walk_forward` (janela deslizante).
- Split temporal treino/val/teste (60/20/20): {split_roi}
- Diagnóstico overfitting: overfit_suspeito={overfit} — {interp_overfit}
- Walk-forward estabilidade: media ROI por janela {wf_media:.4f}, desvio {wf_desvio:.4f}, % janelas positivas {wf_pct:.1%} — {interp_wf}

## 11. Machine Learning (§15)
- Status: {ml_status}
- Detalhe: {ml_detalhe}
- Conclusão ML: {ml_conclusao}

## 12. Sistema de Score (§12)
- Score experimental = Σ peso*componente - penalidade_complexidade. Pesos: {pesos}. Tratado como ranking experimental, NÃO probabilidade real.

## 13. Conclusão (§22 — Regra de Ouro)
> **Pergunta:** Existe evidência estatística suficiente para afirmar que alguma estratégia apresenta vantagem sobre a seleção aleatória?
>
> **Resposta baseada nos dados:** {conclusao_final}

> Se não houver evidência: “Não foi encontrada evidência estatística suficiente.” — resultado válido.

---
*Relatório gerado automaticamente. Todos os cálculos reproduzíveis com seed configurável. Overfitting e viés de múltiplos testes foram considerados. Ver `METHODOLOGY.md`, `STATISTICS.md`, `LIMITATIONS.md`.*
"""

class ReportGenerator:
    def __init__(self, out_path: str | Path = "reports/relatorio.md"):
        self.out_path = Path(out_path)
        self.out_path.parent.mkdir(parents=True, exist_ok=True)

    def generate(self, ctx: dict) -> Path:
        # garante chaves faltantes com default
        defaults = {k: "—" for k in ["tbl_freq_pos","soma_media","soma_mediana","soma_desvio","interp_runs","interp_auto","r_correl","p_correl","p_hat_term0","p_binom","interp_term0","n_gaps","p_hat_gap","estrategias_mc","seed","tbl_metricas","p_vals_orig","p_vals_bonf","p_vals_bh","split_roi","overfit","interp_overfit","wf_media","wf_desvio","wf_pct","interp_wf","ml_status","ml_detalhe","ml_conclusao","pesos"]}
        for k, v in defaults.items():
            ctx.setdefault(k, v)
        md = TEMPLATE.format(**ctx)
        self.out_path.write_text(md, encoding="utf-8")
        return self.out_path
