from abc import ABC, abstractmethod
import pandas as pd

class BaseStrategy(ABC):
    name: str = "base"

    def __init__(self, seed: int | None = 42):
        self.seed = seed

    @abstractmethod
    def select(self, df_history: pd.DataFrame, n: int = 5) -> list[str]:
        """
        Seleciona n números (5 dígitos) com base apenas em df_history (passado).
        NUNCA acessar dados futuros.
        Retorna lista de strings 5 dígitos.
        """
        ...

    def describe(self) -> str:
        return f"Estratégia {self.name} (seed={self.seed})"
