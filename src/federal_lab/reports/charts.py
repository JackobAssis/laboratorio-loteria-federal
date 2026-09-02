"""Gráficos — §16: frequência, posição, finais, soma, intervalos, distribuição, ROI, Monte Carlo, baseline, IC."""

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
import numpy as np
from pathlib import Path

sns.set_theme(style="whitegrid")

class ChartGenerator:
    def __init__(self, out_dir: str | Path = "reports"):
        self.out_dir = Path(out_dir)
        self.out_dir.mkdir(parents=True, exist_ok=True)

    def frequencia_algarismos(self, df_freq: pd.DataFrame, path: str = "freq_algarismos.png") -> Path:
        plt.figure(figsize=(8,4))
        plt.bar(df_freq["algarismo"].astype(str), df_freq["frequencia"])
        plt.axhline(0.1, color="red", linestyle="--", label="esperado 0.10")
        plt.title("Frequência de algarismos 0-9 (todos os dígitos)")
        plt.xlabel("Algarismo"); plt.ylabel("Frequência")
        plt.legend()
        out = self.out_dir / path
        plt.tight_layout(); plt.savefig(out, dpi=150); plt.close()
        return out

    def frequencia_por_posicao(self, df: pd.DataFrame, path: str = "freq_posicao.png") -> Path:
        # heatmap 5 posições x 10 dígitos
        import pandas as pd
        mat = np.zeros((5,10))
        for i, pos in enumerate(["d1","d2","d3","d4","d5"]):
            cnt = df[pos].astype(str).value_counts(normalize=True)
            for d in range(10):
                mat[i, d] = cnt.get(str(d), 0)
        plt.figure(figsize=(10,4))
        sns.heatmap(mat, annot=True, fmt=".2f", cmap="YlGnBu", xticklabels=range(10), yticklabels=["d1","d2","d3","d4","d5"])
        plt.title("Frequência por posição (esperado 0.10)")
        out = self.out_dir / path
        plt.tight_layout(); plt.savefig(out, dpi=150); plt.close()
        return out

    def distribuicao_finais(self, df: pd.DataFrame, n: int = 2, top: int = 20, path: str = None) -> Path:
        path = path or f"finais_{n}d.png"
        col = df["numero"].str[-n:].value_counts().head(top)
        plt.figure(figsize=(10,4))
        plt.bar(col.index.astype(str), col.values)
        plt.axhline(len(df)/ (10**n), color="red", linestyle="--", label=f"esperado {len(df)/(10**n):.1f}")
        plt.title(f"Top {top} terminações {n} dígitos")
        plt.xticks(rotation=45)
        plt.legend()
        out = self.out_dir / path
        plt.tight_layout(); plt.savefig(out, dpi=150); plt.close()
        return out

    def distribuicao_soma(self, df: pd.DataFrame, path: str = "dist_soma.png") -> Path:
        sums = df["numero"].apply(lambda x: sum(int(c) for c in str(x)))
        plt.figure(figsize=(8,4))
        plt.hist(sums, bins=range(0,46), edgecolor="black", alpha=0.7)
        plt.title("Distribuição da soma dos dígitos (0-45)")
        plt.xlabel("Soma"); plt.ylabel("Frequência")
        out = self.out_dir / path
        plt.tight_layout(); plt.savefig(out, dpi=150); plt.close()
        return out

    def distribuicao_numeros(self, df: pd.DataFrame, bins: int = 20, path: str = "dist_numeros.png") -> Path:
        vals = df["numero"].astype(int)
        plt.figure(figsize=(8,4))
        plt.hist(vals, bins=bins, edgecolor="black", alpha=0.7)
        plt.title("Distribuição dos números sorteados (00000-99999)")
        plt.xlabel("Número"); plt.ylabel("Frequência")
        out = self.out_dir / path
        plt.tight_layout(); plt.savefig(out, dpi=150); plt.close()
        return out

    def intervalos_gaps(self, gaps: list[int], path: str = "gaps_hist.png") -> Path:
        if not gaps:
            return None
        plt.figure(figsize=(7,4))
        plt.hist(gaps, bins=20, edgecolor="black", alpha=0.7)
        plt.title("Distribuição de gaps entre ocorrências (atraso)")
        plt.xlabel("Gap (concursos)"); plt.ylabel("Frequência")
        out = self.out_dir / path
        plt.tight_layout(); plt.savefig(out, dpi=150); plt.close()
        return out

    def roi_comparado(self, bench_df: pd.DataFrame, path: str = "roi_benchmark.png") -> Path:
        if bench_df.empty:
            return None
        plt.figure(figsize=(8,4))
        cols = bench_df["estrategia"]
        vals = bench_df["roi_total"]
        colors = ["green" if v>0 else "red" for v in vals]
        plt.bar(cols, vals, color=colors)
        plt.axhline(0, color="black")
        plt.title("ROI total por estratégia (backtest)")
        plt.ylabel("ROI")
        plt.xticks(rotation=15)
        out = self.out_dir / path
        plt.tight_layout(); plt.savefig(out, dpi=150); plt.close()
        return out

    def roi_acumulado(self, backtest_df: pd.DataFrame, path: str = "roi_acumulado.png") -> Path:
        if backtest_df.empty or "roi_acumulado" not in backtest_df:
            return None
        plt.figure(figsize=(9,4))
        plt.plot(backtest_df["concurso_teste"], backtest_df["roi_acumulado"], label="ROI acumulado")
        plt.fill_between(backtest_df["concurso_teste"], backtest_df["roi_acumulado"], alpha=0.2)
        plt.axhline(0, color="black", linestyle="--")
        plt.title("ROI acumulado ao longo dos concursos")
        plt.xlabel("Concurso"); plt.ylabel("ROI")
        plt.legend()
        out = self.out_dir / path
        plt.tight_layout(); plt.savefig(out, dpi=150); plt.close()
        return out

    def monte_carlo_hist(self, resultados: list[dict], path: str = "monte_carlo.png") -> Path:
        rois = [r["roi"] for r in resultados]
        plt.figure(figsize=(7,4))
        plt.hist(rois, bins=20, edgecolor="black", alpha=0.7)
        plt.axvline(np.mean(rois), color="red", linestyle="--", label=f"média {np.mean(rois):.3f}")
        plt.title("Distribuição ROI — Monte Carlo (baseline aleatório)")
        plt.xlabel("ROI"); plt.ylabel("Frequência")
        plt.legend()
        out = self.out_dir / path
        plt.tight_layout(); plt.savefig(out, dpi=150); plt.close()
        return out

    def ic_proporcao(self, k: int, n: int, p_teorica: float, path: str = "ic_proporcao.png") -> Path:
        from federal_lab.statistics.confidence import ConfidenceInterval
        ci = ConfidenceInterval.proporcao_wilson(k, n)
        plt.figure(figsize=(6,3))
        plt.errorbar([0], [ci["p_hat"]], yerr=[[ci["p_hat"]-ci["ci_low"]],[ci["ci_high"]-ci["p_hat"]]], fmt="o", capsize=8, label="p_hat IC95%")
        plt.scatter([0], [p_teorica], color="red", marker="x", s=100, label=f"p teórica {p_teorica:.3f}")
        plt.xlim(-0.5,0.5); plt.xticks([])
        plt.title(f"IC 95% Wilson — k={k}/n={n}")
        plt.legend()
        out = self.out_dir / path
        plt.tight_layout(); plt.savefig(out, dpi=150); plt.close()
        return out
