"""Detecção de overfitting — §11: treino/validação/teste, walk-forward, out-of-sample."""

import pandas as pd
import numpy as np
from .backtest import Backtester

class OverfittingDetector:
    """
    Detecta quando estratégia parece funcionar só porque foi ajustada ao histórico.
    Regra: bom desempenho in-sample sem validação fora da amostra NÃO é promissor.
    """

    def __init__(self, custo: float = 5.0):
        self.custo = custo

    def split_temporal(self, df: pd.DataFrame, train_frac=0.6, val_frac=0.2) -> dict:
        """Divide concursos em treino/validação/teste temporal (sem embaralhar)."""
        concs = sorted(df["concurso"].unique())
        n = len(concs)
        i_train = int(n * train_frac)
        i_val = int(n * (train_frac + val_frac))
        return {
            "train": df[df["concurso"].isin(concs[:i_train])],
            "val": df[df["concurso"].isin(concs[i_train:i_val])],
            "test": df[df["concurso"].isin(concs[i_val:])],
            "cut_train": concs[i_train] if i_train < n else None,
            "cut_val": concs[i_val] if i_val < n else None,
        }

    def avaliar(self, df: pd.DataFrame, estrategia, train_frac=0.6, val_frac=0.2, min_history=20) -> dict:
        """Roda backtest separado em cada split e compara ROI."""
        splits = self.split_temporal(df, train_frac, val_frac)
        bt = Backtester(custo_por_aposta=self.custo)
        resultados = {}
        for nome in ["train", "val", "test"]:
            sub = splits[nome]
            if sub.empty or sub["concurso"].nunique() < min_history + 5:
                resultados[nome] = {"roi_total": None, "n": 0, "df": pd.DataFrame()}
                continue
            # para val/test, histórico = treino+val anteriores, mas teste isolado:
            # simula como se só tivesse acesso a dados até início do split
            # simplificado: backtest dentro do split
            res = bt.run(sub, estrategia, min_history=min_history)
            roi_total = (res["retorno"].sum() - res["custo"].sum()) / res["custo"].sum() if not res.empty and res["custo"].sum() else None
            resultados[nome] = {"roi_total": roi_total, "n": len(res), "df": res}

        # heurística overfitting: train >> val/test
        rt = resultados["train"]["roi_total"]
        rv = resultados["val"]["roi_total"]
        rtt = resultados["test"]["roi_total"]
        overfit = None
        if rt is not None and rv is not None and rtt is not None:
            overfit = (rt > 0 and rv < 0 and rtt < 0) or (rt - rtt > 0.5)  # queda acentuada
        return {
            "splits": {k: {"roi_total": v["roi_total"], "n": v["n"]} for k, v in resultados.items()},
            "overfit_suspeito": bool(overfit) if overfit is not None else None,
            "interpretacao": (
                "Overfitting suspeito: bom in-sample, ruim out-of-sample. Não considerar promissora."
                if overfit else
                "Sem evidência clara de overfitting, mas exigir validação walk-forward."
                if overfit is False else
                "Dados insuficientes para diagnóstico."
            ),
            "detalhe": resultados,
        }

    def walk_forward_diagnostico(self, df: pd.DataFrame, estrategia, train_size=50, test_size=10) -> dict:
        """Walk-forward + estabilidade: ROI por janela deve ser estável, não apenas um pico."""
        bt = Backtester(custo_por_aposta=self.custo)
        wf = bt.walk_forward(df, estrategia, train_size=train_size, test_size=test_size)
        if wf.empty:
            return {"estavel": None, "motivo": "walk-forward vazio"}
        roi_por_janela = wf.groupby("janela")["roi"].mean()
        # estabilidade: desvio / média, e % janelas positivas
        media = roi_por_janela.mean()
        desvio = roi_por_janela.std(ddof=1) if len(roi_por_janela) > 1 else 0
        pct_pos = (roi_por_janela > 0).mean()
        estavel = desvio < abs(media) * 0.5 and pct_pos > 0.6 if media != 0 else False
        return {
            "roi_por_janela": roi_por_janela.to_dict(),
            "media": float(media),
            "desvio": float(desvio),
            "pct_janelas_positivas": float(pct_pos),
            "estavel": bool(estavel),
            "interpretacao": "Estável e consistente" if estavel else "Instável ou não consistentemente positivo — provável overfit ou flutuação."
        }
