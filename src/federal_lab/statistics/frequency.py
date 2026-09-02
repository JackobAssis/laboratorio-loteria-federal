"""Frequência de algarismos, pares, trincas, sequências, terminações."""

from collections import Counter
import pandas as pd
import numpy as np

class FrequencyAnalyzer:
    def __init__(self, df: pd.DataFrame):
        """
        df deve conter colunas: numero (5 dígitos), d1..d5, posicao, concurso.
        Obtido via Repository.get_dataframe() ou Parser.to_dataframe()
        """
        self.df = df.copy()
        if self.df.empty:
            raise ValueError("DataFrame vazio — sem dados para análise")

    def freq_algarismos(self) -> pd.DataFrame:
        """Frequência 0-9 em todos os dígitos (5 * N sorteios)."""
        todos = "".join(self.df["numero"].astype(str))
        cnt = Counter(todos)
        total = len(todos)
        rows = []
        for d in map(str, range(10)):
            obs = cnt.get(d, 0)
            rows.append({"algarismo": d, "observado": obs, "frequencia": obs/total, "esperado_freq": 0.1, "esperado_abs": total*0.1})
        return pd.DataFrame(rows).sort_values("algarismo")

    def freq_por_posicao(self) -> pd.DataFrame:
        """Frequência por posição d1..d5."""
        rows = []
        for pos in ["d1","d2","d3","d4","d5"]:
            cnt = Counter(self.df[pos].astype(str))
            total = len(self.df)
            for d in map(str, range(10)):
                rows.append({"posicao": pos, "algarismo": d, "observado": cnt.get(d,0), "freq": cnt.get(d,0)/total})
        return pd.DataFrame(rows)

    def freq_primeiro_ultimo(self) -> dict:
        return {
            "primeiro": Counter(self.df["d1"].astype(str)),
            "ultimo": Counter(self.df["d5"].astype(str)),
        }

    def freq_terminacoes(self, n: int = 1) -> pd.DataFrame:
        """Terminações de n dígitos (1..4)."""
        if not 1 <= n <= 4:
            raise ValueError("n deve ser 1..4")
        col = self.df["numero"].str[-n:]
        cnt = Counter(col)
        total = len(col)
        df = pd.DataFrame([{"terminacao": k, "observado": v, "freq": v/total} for k,v in cnt.items()])
        # completa com zeros esperados? apenas observados
        return df.sort_values("observado", ascending=False)

    def freq_pares(self) -> pd.DataFrame:
        """Frequência de pares consecutivos (ex '12' em '01234' conta 01,12,23,34)."""
        pares = []
        for num in self.df["numero"]:
            s = str(num)
            for i in range(4):
                pares.append(s[i:i+2])
        cnt = Counter(pares)
        total = len(pares)
        return pd.DataFrame([{"par": k, "obs": v, "freq": v/total} for k,v in cnt.most_common()])

    def freq_trincas(self) -> pd.DataFrame:
        trincas = []
        for num in self.df["numero"]:
            s = str(num)
            for i in range(3):
                trincas.append(s[i:i+3])
        cnt = Counter(trincas)
        total = len(trincas)
        return pd.DataFrame([{"trinca": k, "obs": v, "freq": v/total} for k,v in cnt.most_common()])

    def intervalo_desde_ultima(self, alvo: str | None = None, posicao: str | None = None) -> pd.DataFrame:
        """
        Calcula intervalo desde última ocorrência.
        Se alvo is None, calcula para cada algarismo 0-9 por posição.
        Retorna DataFrame com concurso e gap.
        """
        df = self.df.sort_values("concurso")
        # para cada concurso, verifica ocorrência
        # retorna gap atual (quantos concursos desde última ocorrência)
        result = []
        for dig in map(str, range(10)):
            last = None
            gap_atual = None
            for _, row in df.iterrows():
                ocorreu = False
                if posicao:
                    ocorreu = str(row[posicao]) == dig
                else:
                    ocorreu = dig in str(row["numero"])
                if ocorreu:
                    gap = row["concurso"] - last if last is not None else None
                    result.append({"algarismo": dig, "posicao": posicao or "qualquer", "concurso": row["concurso"], "gap": gap})
                    last = row["concurso"]
            # gap desde última ocorrência até concurso mais recente
            if last is not None:
                ultimo_concurso = df["concurso"].max()
                result.append({"algarismo": dig, "posicao": posicao or "qualquer", "concurso": ultimo_concurso, "gap_atual": ultimo_concurso - last, "ultima_ocorrencia": last})
        return pd.DataFrame(result)
