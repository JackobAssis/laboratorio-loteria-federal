"""Probabilidade empírica com intervalos de confiança."""

import pandas as pd
from ..statistics.confidence import ConfidenceInterval

class EmpiricalProbability:
    def __init__(self, df: pd.DataFrame):
        self.df = df

    def proporcao(self, filtro) -> dict:
        """
        filtro: callable que recebe row e retorna bool, ou máscara booleana
        """
        if callable(filtro):
            mask = self.df.apply(filtro, axis=1)
        else:
            mask = filtro
        k = int(mask.sum())
        n = len(self.df)
        ci = ConfidenceInterval.proporcao_wilson(k, n)
        return {"k": k, "n": n, "p_hat": ci["p_hat"], "ci_low": ci["ci_low"], "ci_high": ci["ci_high"]}

    def por_terminacao(self, n: int = 1) -> pd.DataFrame:
        col = self.df["numero"].str[-n:].value_counts()
        total = len(self.df)
        rows = []
        for term, k in col.items():
            ci = ConfidenceInterval.proporcao_wilson(int(k), total)
            rows.append({"terminacao": term, **ci})
        return pd.DataFrame(rows).sort_values("p_hat", ascending=False)

    def por_faixa(self, bins: int = 10) -> pd.DataFrame:
        import pandas as pd
        df = self.df.copy()
        df["numero_int"] = df["numero"].astype(int)
        df["faixa"] = pd.cut(df["numero_int"], bins=bins)
        total = len(df)
        rows = []
        for faixa, grp in df.groupby("faixa", observed=True):
            k = len(grp)
            ci = ConfidenceInterval.proporcao_wilson(k, total)
            rows.append({"faixa": str(faixa), **ci})
        return pd.DataFrame(rows)
