"""Features de algarismos."""

import pandas as pd

class DigitFeatures:
    @staticmethod
    def extrair(numero: str) -> dict:
        s = str(numero).zfill(5)
        return {
            "numero": s,
            "d1": s[0], "d2": s[1], "d3": s[2], "d4": s[3], "d5": s[4],
            "primeiro": s[0], "ultimo": s[4],
            "pares": [s[i:i+2] for i in range(4)],
            "trincas": [s[i:i+3] for i in range(3)],
            "digitos_unicos": len(set(s)),
        }

    @staticmethod
    def batch(df: pd.DataFrame) -> pd.DataFrame:
        out = df.copy()
        out["digitos_unicos"] = out["numero"].apply(lambda x: len(set(str(x))))
        return out
