"""Recência / atraso — seleciona números 'atrasados'. Demonstra falácia do jogador se mal usado."""

import pandas as pd
import numpy as np
from collections import Counter
from .base import BaseStrategy

class RecencyStrategy(BaseStrategy):
    name = "recency"
    def select(self, df_history: pd.DataFrame, n: int = 5) -> list[str]:
        if df_history.empty or len(df_history) < 5:
            from .random_strategy import RandomStrategy
            return RandomStrategy(seed=self.seed).select(df_history, n)
        # calcula último concurso onde cada número (terminação 2 dígitos) apareceu
        # escolhe terminações menos recentes (= maior gap)
        df_sorted = df_history.sort_values("concurso")
        ultimo = df_sorted["concurso"].max()
        # mapa terminação 2d -> último concurso
        term_last = {}
        for _, row in df_sorted.iterrows():
            term = str(row["numero"])[-2:]
            term_last[term] = row["concurso"]
        # gap
        gaps = {term: ultimo - last for term, last in term_last.items()}
        # inclui terminações nunca vistas (gap = ultimo - 0 = grande)
        for i in range(100):
            t = f"{i:02d}"
            if t not in gaps:
                gaps[t] = ultimo  # máximo
        # ordena por gap desc (mais atrasado primeiro)
        ordenados = sorted(gaps, key=lambda k: gaps[k], reverse=True)
        rng = np.random.default_rng(self.seed)
        result = []
        for _ in range(n):
            term = rng.choice(ordenados[:20])  # top 20 atrasados
            prefix = f"{rng.integers(0,1000):03d}"  # 3 dígitos aleatórios
            result.append(prefix + term)
        return result
