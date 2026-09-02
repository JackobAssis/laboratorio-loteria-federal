import numpy as np
import pandas as pd
from .base import BaseStrategy

class RandomStrategy(BaseStrategy):
    name = "random"
    def select(self, df_history: pd.DataFrame, n: int = 5) -> list[str]:
        rng = np.random.default_rng(self.seed)
        # seleção uniforme 00000-99999
        nums = rng.integers(0, 100_000, size=n)
        return [f"{x:05d}" for x in nums]
