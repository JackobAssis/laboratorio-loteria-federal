"""Benchmark — compara todas estratégias contra baseline aleatório."""

import pandas as pd
import numpy as np
from scipy import stats
from ..statistics.confidence import ConfidenceInterval
from .backtest import Backtester

class Benchmark:
    def __init__(self, custo: float = 5.0):
        self.custo = custo

    def compare_backtests(self, resultados: dict[str, pd.DataFrame]) -> pd.DataFrame:
        """
        resultados: dict estrategia -> DataFrame do Backtester.run
        Retorna tabela comparativa com média, mediana, desvio, IC, ROI etc.
        """
        rows = []
        for nome, df in resultados.items():
            if df.empty:
                continue
            roi = df["roi"]
            acertos = df["acertos"]
            rows.append({
                "estrategia": nome,
                "n_testes": len(df),
                "media_roi": roi.mean(),
                "mediana_roi": roi.median(),
                "desvio_roi": roi.std(ddof=1) if len(roi)>1 else 0,
                "roi_total": (df["retorno"].sum() - df["custo"].sum()) / df["custo"].sum() if df["custo"].sum() else 0,
                "taxa_acerto": (acertos > 0).mean(),
                "media_acertos": acertos.mean(),
                "ci_low_roi": ConfidenceInterval.media_t(roi)["ci_low"],
                "ci_high_roi": ConfidenceInterval.media_t(roi)["ci_high"],
            })
        out = pd.DataFrame(rows).sort_values("roi_total", ascending=False) if rows else pd.DataFrame()
        return out

    def significancia_vs_baseline(self, df_strategy: pd.DataFrame, df_baseline: pd.DataFrame) -> dict:
        """
        Testa se estratégia supera baseline (aleatório).
        H0: mesma distribuição de ROI
        H1: estratégia diferente
        """
        a = df_strategy["roi"].values
        b = df_baseline["roi"].values
        if len(a) < 5 or len(b) < 5:
            return {"p_value": None, "interpretacao": "amostra pequena"}
        # Mann-Whitney (não paramétrico) + t-test
        try:
            _, p_mw = stats.mannwhitneyu(a, b, alternative="two-sided")
        except Exception:
            p_mw = None
        # tratativa variância zero -> p=1 se médias iguais, senão nan->trata
        if np.all(a == a[0]) and np.all(b == b[0]):
            if a[0] == b[0]:
                p_t, t = 1.0, 0.0
            else:
                p_t, t = 0.0, np.inf if a.mean() > b.mean() else -np.inf
        else:
            try:
                t, p_t = stats.ttest_ind(a, b, equal_var=False, nan_policy="omit")
                if np.isnan(p_t):
                    p_t = 1.0
                    t = 0.0
            except Exception:
                p_t, t = 1.0, 0.0
        return {
            "teste_mannwhitney_p": float(p_mw) if p_mw is not None and not np.isnan(p_mw) else None,
            "teste_t_p": float(p_t) if not np.isnan(p_t) else 1.0,
            "t_stat": float(t) if not np.isnan(t) and np.isfinite(t) else 0.0,
            "media_strategy": float(a.mean()),
            "media_baseline": float(b.mean()),
            "H0": "Mesma distribuição de ROI",
            "conclusao": "Sem evidência de superioridade" if float(p_t) >= 0.05 else "Diferença significativa (verificar fora da amostra e correção múltipla)",
            "aviso": "Uma estratégia só é interessante se superar baseline de forma consistente e fora da amostra."
        }
