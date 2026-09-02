"""Seleciona com base em frequência histórica (quentes). Experimental — não implica vantagem real."""

import numpy as np
import pandas as pd
from collections import Counter
from .base import BaseStrategy

class FrequencyStrategy(BaseStrategy):
    name = "frequency"
    def select(self, df_history: pd.DataFrame, n: int = 5) -> list[str]:
        if df_history.empty:
            return RandomStrategy(seed=self.seed).select(df_history, n) if (RandomStrategy:=__import__("federal_lab.strategies.random_strategy", fromlist=["RandomStrategy"])).RandomStrategy else []
        # calcula frequência de dígitos por posição
        freq_pos = {}
        for pos in ["d1","d2","d3","d4","d5"]:
            cnt = Counter(df_history[pos].astype(str))
            # ordena por frequência desc
            freq_pos[pos] = [d for d,_ in cnt.most_common()]
            # completa dígitos faltantes
            for dig in map(str, range(10)):
                if dig not in freq_pos[pos]:
                    freq_pos[pos].append(dig)
        rng = np.random.default_rng(self.seed)
        result = []
        for _ in range(n):
            # amostra ponderada: top 3 dígitos têm peso maior
            numero = ""
            for pos in ["d1","d2","d3","d4","d5"]:
                candidatos = freq_pos[pos]
                # pesos exponenciais: 0.4,0.3,0.2, ...
                pesos = np.array([0.4,0.3,0.15,0.07,0.03,0.02,0.01,0.01,0.005,0.005][:len(candidatos)])
                pesos = pesos / pesos.sum()
                # usa apenas top 5 para não ser determinístico
                top = candidatos[:5]
                p_top = pesos[:5] / pesos[:5].sum()
                numero += str(rng.choice(top, p=p_top))
            result.append(numero)
        return result
