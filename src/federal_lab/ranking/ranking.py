"""Ranking experimental."""

import pandas as pd
from .scoring import Scorer

class Ranker:
    def __init__(self, scorer: Scorer | None = None):
        self.scorer = scorer or Scorer()

    def rank(self, numeros: list[str], historico_stats: dict) -> pd.DataFrame:
        rows = []
        for num in numeros:
            score = self.scorer.score_numero(num, historico_stats)
            rows.append({"numero": num, "score": score})
        df = pd.DataFrame(rows).sort_values("score", ascending=False).reset_index(drop=True)
        df["rank"] = df.index + 1
        # aviso explícito
        df["aviso"] = "ranking experimental — não é probabilidade real"
        return df
