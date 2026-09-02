"""Testes de independência e aleatoriedade."""

import numpy as np
import pandas as pd
from scipy import stats

class IndependenceTester:
    @staticmethod
    def chi2_independencia(tabela: np.ndarray) -> dict:
        """
        Tabela de contingência (ex dígitos por posição).
        H0: variáveis independentes
        """
        chi2, p, dof, expected = stats.chi2_contingency(tabela)
        return {
            "teste": "Chi2 independência",
            "H0": "Variáveis independentes",
            "H1": "Dependência entre variáveis",
            "chi2": float(chi2),
            "p_value": float(p),
            "dof": int(dof),
            "expected": expected.tolist(),
        }

    @staticmethod
    def permutacao_media_diff(a: list[float], b: list[float], n_perm: int = 10000, seed: int = 42) -> dict:
        rng = np.random.default_rng(seed)
        a = np.asarray(a, dtype=float)
        b = np.asarray(b, dtype=float)
        diff_obs = a.mean() - b.mean()
        combined = np.concatenate([a,b])
        n_a = len(a)
        count = 0
        for _ in range(n_perm):
            rng.shuffle(combined)
            diff_perm = combined[:n_a].mean() - combined[n_a:].mean()
            if abs(diff_perm) >= abs(diff_obs):
                count += 1
        p = (count + 1) / (n_perm + 1)
        return {"diff_obs": float(diff_obs), "p_value": float(p), "n_perm": n_perm, "H0": "Mesma distribuição"}

    @staticmethod
    def bootstrap_media(data: list[float], n_bootstrap: int = 10000, seed: int = 42) -> dict:
        rng = np.random.default_rng(seed)
        arr = np.asarray(data, dtype=float)
        means = [rng.choice(arr, size=len(arr), replace=True).mean() for _ in range(n_bootstrap)]
        low, high = np.percentile(means, [2.5, 97.5])
        return {"mean_obs": float(arr.mean()), "ci_low": float(low), "ci_high": float(high), "n_bootstrap": n_bootstrap}
