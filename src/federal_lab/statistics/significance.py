"""Testes de significância com correção para múltiplos testes."""

import numpy as np
import pandas as pd
from scipy import stats

class SignificanceTester:
    @staticmethod
    def chi_square_uniform(observados: list[int] | np.ndarray) -> dict:
        """
        H0: distribuição uniforme (ex dígitos 0-9 com p=0.1)
        H1: distribuição diferente de uniforme
        """
        obs = np.asarray(observados, dtype=float)
        n = obs.sum()
        k = len(obs)
        esperados = np.full(k, n/k)
        chi2, p = stats.chisquare(obs, f_exp=esperados)
        return {
            "teste": "Chi-square uniformidade",
            "H0": "Distribuição uniforme",
            "H1": "Distribuição não uniforme",
            "chi2": float(chi2),
            "p_value": float(p),
            "graus_liberdade": k-1,
            "observados": obs.tolist(),
            "esperados": esperados.tolist(),
            "n": int(n),
        }

    @staticmethod
    def chi_square_aderencia(observados, esperados) -> dict:
        obs = np.asarray(observados, dtype=float)
        esp = np.asarray(esperados, dtype=float)
        chi2, p = stats.chisquare(obs, f_exp=esp)
        return {"chi2": float(chi2), "p_value": float(p), "H0": "Observado = Esperado"}

    @staticmethod
    def runs_test(sequence: list[int]) -> dict:
        """Wald-Wolfowitz runs test para aleatoriedade."""
        # converte para binário pela mediana
        arr = np.asarray(sequence)
        median = np.median(arr)
        binary = (arr > median).astype(int)
        n1 = (binary == 0).sum()
        n0 = (binary == 1).sum()
        if n1 == 0 or n0 == 0:
            return {"p_value": 1.0, "runs": int(len(arr)), "interpretacao": "sequência constante"}
        runs = 1 + np.sum(binary[1:] != binary[:-1])
        # aproximação normal
        mu = 2*n1*n0 / (n1+n0) + 1
        var = 2*n1*n0*(2*n1*n0 - n1 - n0) / ((n1+n0)**2 * (n1+n0-1))
        z = (runs - mu) / np.sqrt(var) if var > 0 else 0
        p = 2 * (1 - stats.norm.cdf(abs(z)))
        return {"teste": "Runs test", "H0": "Sequência aleatória", "runs": int(runs), "z": float(z), "p_value": float(p), "n1": int(n1), "n0": int(n0)}

    @staticmethod
    def autocorrelacao_lag1(series: list[float]) -> dict:
        arr = np.asarray(series, dtype=float)
        if len(arr) < 3:
            return {"r": None, "p_value": None}
        r = np.corrcoef(arr[:-1], arr[1:])[0,1]
        # teste t para correlação
        n = len(arr)-1
        if np.isnan(r) or abs(r) == 1:
            return {"r": float(r) if not np.isnan(r) else None, "p_value": 0.0 if abs(r)==1 else None}
        t = r * np.sqrt((n-2)/(1-r**2)) if abs(r) < 1 else np.inf
        p = 2 * (1 - stats.t.cdf(abs(t), n-2))
        return {"r": float(r), "t": float(t), "p_value": float(p), "H0": "r=0 (sem autocorrelação)"}

    @staticmethod
    def atraso_geometrico_test(gaps: list[int]) -> dict:
        """
        Testa se gaps entre ocorrências seguem Geométrica(p).
        H0: gaps compatíveis com processo aleatório (geométrico)
        Usa KS test comparando gaps observados vs simulação geométrica.
        """
        if len(gaps) < 10:
            return {"p_value": None, "interpretacao": "amostra pequena (<10 gaps)"}
        arr = np.asarray(gaps, dtype=float)
        # estima p = 1 / media gaps, cap em [0.001,1] (p>1 impossível)
        mean_gap = arr.mean() if arr.mean() != 0 else 1
        p_hat_raw = 1 / mean_gap if mean_gap != 0 else 0.1
        p_hat = float(np.clip(p_hat_raw, 0.001, 1.0))
        # usa kstest contra geom com p_hat
        # scipy geom: pmf(k) = (1-p)^(k-1) * p  k>=1
        try:
            stat, p = stats.kstest(arr, lambda x: stats.geom.cdf(x, p_hat))
        except Exception:
            p = None
            stat = None
        return {"teste": "KS geométrico (atraso)", "H0": "Gaps ~ Geométrica(p)", "p_hat": float(p_hat), "p_hat_raw": float(p_hat_raw), "ks_stat": float(stat) if stat else None, "p_value": float(p) if p else None}

    @staticmethod
    def corrigir_multiplos(p_values: list[float], method: str = "bonferroni") -> list[float]:
        """Bonferroni ou Benjamini-Hochberg."""
        p = np.asarray(p_values, dtype=float)
        if method == "bonferroni":
            return np.minimum(p * len(p), 1.0).tolist()
        elif method in ("fdr", "benjamini-hochberg", "bh"):
            # BH procedure
            n = len(p)
            order = np.argsort(p)
            ranked = p[order]
            adj = ranked * n / (np.arange(n)+1)
            # cumulative min from end
            adj = np.minimum.accumulate(adj[::-1])[::-1]
            adj = np.minimum(adj, 1.0)
            # reorder
            out = np.empty_like(adj)
            out[order] = adj
            return out.tolist()
        else:
            raise ValueError(f"Método desconhecido: {method}")
