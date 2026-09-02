"""Combina pesos de frequência, distribuição, recência."""

import numpy as np
import pandas as pd
from .base import BaseStrategy
from .random_strategy import RandomStrategy
from .frequency_strategy import FrequencyStrategy
from .recency_strategy import RecencyStrategy
from .distribution_strategy import DistributionStrategy

class CombinedStrategy(BaseStrategy):
    name = "combined"
    def __init__(self, seed: int | None = 42, pesos: dict | None = None):
        super().__init__(seed)
        self.pesos = pesos or {"frequencia": 0.25, "distribuicao": 0.25, "recencia": 0.25, "aleatorio": 0.25}

    def select(self, df_history: pd.DataFrame, n: int = 5) -> list[str]:
        rng = np.random.default_rng(self.seed)
        # coleta 20 candidatos de cada estratégia e escolhe com score combinado simples
        freq = FrequencyStrategy(seed=self.seed).select(df_history, 20)
        rec = RecencyStrategy(seed=self.seed).select(df_history, 20)
        dist = DistributionStrategy(seed=self.seed).select(df_history, 20)
        rand = RandomStrategy(seed=self.seed).select(df_history, 20)
        pool = freq + rec + dist + rand
        # score: quanto mais próximo da média de soma, maior score; penaliza repetição excessiva
        somas = [sum(int(c) for c in x) for x in pool]
        media_pool = np.mean(somas)
        scores = []
        for num in pool:
            s = sum(int(c) for c in num)
            repet = 5 - len(set(num))
            score = -abs(s - media_pool) - repet*0.5 + rng.normal(0, 0.5)
            scores.append(score)
        idx = np.argsort(scores)[::-1][:n]
        return [pool[i] for i in idx]
