"""Baseada em distribuição estatística (faixa, soma, paridade)."""

import numpy as np
import pandas as pd
from .base import BaseStrategy

class DistributionStrategy(BaseStrategy):
    name = "distribution"
    def select(self, df_history: pd.DataFrame, n: int = 5) -> list[str]:
        if df_history.empty:
            from .random_strategy import RandomStrategy
            return RandomStrategy(seed=self.seed).select(df_history, n)
        # analisa distribuição de soma e tenta amostrar próximo à média observada (evita extremos)
        rng = np.random.default_rng(self.seed)
        somas = df_history["numero"].apply(lambda x: sum(int(c) for c in str(x)))
        media = somas.mean()
        desvio = somas.std() or 5
        result = []
        tentativas = 0
        while len(result) < n and tentativas < n*50:
            tentativas += 1
            cand = f"{rng.integers(0,100000):05d}"
            s = sum(int(c) for c in cand)
            # aceita se soma dentro de 1 desvio da média
            if abs(s - media) <= desvio:
                result.append(cand)
        # completa com aleatórios se não preencheu
        while len(result) < n:
            result.append(f"{rng.integers(0,100000):05d}")
        return result
