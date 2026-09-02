"""Distribuição: faixas, soma dígitos, paridade, repetição, sequências."""

import pandas as pd
import numpy as np
from collections import Counter

class DistributionAnalyzer:
    def __init__(self, df: pd.DataFrame):
        self.df = df.copy()
        if self.df.empty:
            raise ValueError("DataFrame vazio")
        # colunas auxiliares
        self.df["numero_int"] = self.df["numero"].astype(int)
        self.df["soma_digitos"] = self.df["numero"].apply(lambda x: sum(int(c) for c in str(x)))
        self.df["qtd_pares"] = self.df["numero"].apply(lambda x: sum(1 for c in str(x) if int(c) % 2 == 0))
        self.df["qtd_impares"] = 5 - self.df["qtd_pares"]
        self.df["repeticao"] = self.df["numero"].apply(lambda x: 5 - len(set(str(x))))
        self.df["digitos_iguais"] = self.df["numero"].apply(lambda x: len(set(str(x))) == 1)
        self.df["sequencia_consecutiva"] = self.df["numero"].apply(self._tem_sequencia)

    @staticmethod
    def _tem_sequencia(s: str, tamanho: int = 3) -> bool:
        # ex 12345, 34567, 321 .. verifica qualquer janela ordenada crescente/decrescente
        s = str(s)
        for i in range(len(s) - tamanho + 1):
            janela = [int(c) for c in s[i:i+tamanho]]
            if janela == list(range(janela[0], janela[0]+tamanho)):
                return True
            if janela == list(range(janela[0], janela[0]-tamanho, -1)):
                return True
        return False

    def por_faixa(self, bins: int = 10) -> pd.DataFrame:
        """Divide 0-99999 em bins."""
        df = self.df.copy()
        df["faixa"] = pd.cut(df["numero_int"], bins=bins)
        cnt = df["faixa"].value_counts().sort_index()
        total = len(df)
        return pd.DataFrame({"faixa": cnt.index.astype(str), "observado": cnt.values, "freq": cnt.values/total, "esperado": total/bins})

    def soma_digitos_stats(self) -> dict:
        s = self.df["soma_digitos"]
        return {"media": s.mean(), "mediana": s.median(), "desvio": s.std(), "min": s.min(), "max": s.max(), "dist": s.value_counts().sort_index()}

    def paridade(self) -> pd.DataFrame:
        cnt = self.df["qtd_pares"].value_counts().sort_index()
        total = len(self.df)
        # teórico: binomial n=5 p=0.5 para cada qtd de pares (0..5)
        from scipy.stats import binom
        rows = []
        for k in range(6):
            obs = cnt.get(k, 0)
            esp = binom.pmf(k, 5, 0.5) * total
            rows.append({"qtd_pares": k, "observado": obs, "esperado": esp, "freq_obs": obs/total, "freq_esp": esp/total})
        return pd.DataFrame(rows)

    def repeticoes(self) -> pd.DataFrame:
        cnt = self.df["repeticao"].value_counts().sort_index()
        total = len(self.df)
        return pd.DataFrame({"repeticoes": cnt.index, "observado": cnt.values, "freq": cnt.values/total})

    def digitos_iguais_freq(self) -> dict:
        return {"qtd": int(self.df["digitos_iguais"].sum()), "freq": float(self.df["digitos_iguais"].mean())}

    def sequencias_freq(self) -> dict:
        return {"qtd": int(self.df["sequencia_consecutiva"].sum()), "freq": float(self.df["sequencia_consecutiva"].mean())}
