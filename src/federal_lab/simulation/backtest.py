"""Backtesting temporal — nunca usar informação futura."""

import pandas as pd

class Backtester:
    def __init__(self, custo_por_aposta: float = 5.0, premio_por_acerto: float = 50000):
        self.custo = custo_por_aposta
        self.premio = premio_por_acerto

    def run(self, df: pd.DataFrame, estrategia, min_history: int = 20) -> pd.DataFrame:
        """
        df: DataFrame com colunas concurso, data, numero, posicao (ordenado por concurso)
        Para cada concurso N >= min_history, treina em concursos < N e testa em N.
        Retorna DataFrame com resultado por concurso testado.
        """
        if df.empty:
            raise ValueError("DataFrame vazio")
        df = df.sort_values("concurso").copy()
        concursos_unicos = sorted(df["concurso"].unique())
        resultados = []

        for idx, conc_teste in enumerate(concursos_unicos):
            if idx < min_history:
                continue
            historico = df[df["concurso"] < conc_teste]
            teste = df[df["concurso"] == conc_teste]
            sorteados = teste["numero"].tolist()

            try:
                selecao = estrategia.select(historico, n=5)
            except Exception as e:
                selecao = []
            acertos = sum(1 for s in selecao if s in sorteados)
            custo = len(selecao) * self.custo
            retorno = acertos * self.premio
            roi = (retorno - custo) / custo if custo else 0

            # REGRA DE OURO: registrar estratégia, seleção, resultado, nunca usar futuro
            resultados.append({
                "concurso_teste": conc_teste,
                "estrategia": getattr(estrategia, "name", str(estrategia)),
                "selecao": ",".join(selecao),
                "sorteados": ",".join(sorteados),
                "acertos": acertos,
                "custo": custo,
                "retorno": retorno,
                "roi": roi,
                "qtd_apostas": len(selecao),
            })
        out = pd.DataFrame(resultados)
        if not out.empty:
            out["roi_acumulado"] = (out["retorno"].cumsum() - out["custo"].cumsum()) / out["custo"].cumsum()
            out["drawdown"] = out["roi_acumulado"].cummax() - out["roi_acumulado"]
        return out

    def walk_forward(self, df: pd.DataFrame, estrategia, train_size: int = 50, test_size: int = 10) -> pd.DataFrame:
        """Validação walk-forward: treina em janela móvel, testa próximos test_size concursos."""
        df = df.sort_values("concurso")
        concursos = sorted(df["concurso"].unique())
        resultados = []
        start = 0
        while start + train_size + test_size <= len(concursos):
            train_conc = concursos[start : start+train_size]
            test_conc = concursos[start+train_size : start+train_size+test_size]
            historico = df[df["concurso"].isin(train_conc)]
            for ct in test_conc:
                teste = df[df["concurso"] == ct]
                sorteados = teste["numero"].tolist()
                selecao = estrategia.select(historico, n=5)
                acertos = sum(1 for s in selecao if s in sorteados)
                resultados.append({
                    "janela": start,
                    "concurso_teste": ct,
                    "acertos": acertos,
                    "roi": (acertos*self.premio - len(selecao)*self.custo) / (len(selecao)*self.custo) if selecao else 0,
                })
            start += test_size
        return pd.DataFrame(resultados)
