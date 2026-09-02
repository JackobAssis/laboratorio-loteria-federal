"""Correlações — diferenciar correlação de causalidade."""

import pandas as pd
import numpy as np
from scipy import stats

class CorrelationAnalyzer:
    def __init__(self, df: pd.DataFrame):
        self.df = df

    def correlacao_posicoes(self) -> pd.DataFrame:
        """Correlação entre dígitos nas 5 posições."""
        mat = self.df[["d1","d2","d3","d4","d5"]].astype(int)
        corr = mat.corr(method="pearson")
        return corr

    def correlacao_soma_concurso(self) -> dict:
        """Correlação entre número do concurso e soma dos dígitos (deve ser ~0 se aleatório)."""
        x = self.df["concurso"].astype(int)
        y = self.df["numero"].apply(lambda s: sum(int(c) for c in str(s)))
        r, p = stats.pearsonr(x, y)
        return {"r": float(r), "p_value": float(p), "interpretacao": "r≈0 esperado para sorteio aleatório"}

    def cramer_v(self, col1: str, col2: str) -> dict:
        """Cramér's V para variáveis categóricas (ex d1 vs d5)."""
        ct = pd.crosstab(self.df[col1], self.df[col2])
        chi2 = stats.chi2_contingency(ct)[0]
        n = ct.values.sum()
        k = min(ct.shape)
        v = np.sqrt(chi2 / (n * (k -1))) if k>1 else 0
        return {"cramer_v": float(v), "chi2": float(chi2), "n": int(n)}
