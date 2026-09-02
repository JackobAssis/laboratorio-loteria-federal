"""Intervalos de confiança para proporções e médias."""

import numpy as np
from scipy import stats

class ConfidenceInterval:
    @staticmethod
    def proporcao_wilson(k: int, n: int, alpha: float = 0.05) -> dict:
        """Wilson score interval para proporção."""
        if n == 0:
            return {"p_hat": None, "ci_low": None, "ci_high": None}
        p = k / n
        z = stats.norm.ppf(1 - alpha/2)
        denom = 1 + z**2 / n
        centre = p + z**2 / (2*n)
        margin = z * np.sqrt(p*(1-p)/n + z**2/(4*n**2))
        low = (centre - margin) / denom
        high = (centre + margin) / denom
        return {"p_hat": p, "ci_low": max(0, low), "ci_high": min(1, high), "z": z, "alpha": alpha}

    @staticmethod
    def media_t(data, alpha: float = 0.05) -> dict:
        arr = np.asarray(data, dtype=float)
        n = len(arr)
        if n < 2:
            return {"mean": float(np.mean(arr)) if n else None, "ci_low": None, "ci_high": None}
        mean = arr.mean()
        if np.all(arr == arr[0]):  # variância zero
            return {"mean": float(mean), "ci_low": float(mean), "ci_high": float(mean), "n": n, "alpha": alpha}
        se = stats.sem(arr)
        if se == 0 or np.isnan(se):
            return {"mean": float(mean), "ci_low": float(mean), "ci_high": float(mean), "n": n, "alpha": alpha}
        ci = stats.t.interval(1-alpha, n-1, loc=mean, scale=se)
        return {"mean": float(mean), "ci_low": float(ci[0]), "ci_high": float(ci[1]), "n": n, "alpha": alpha}

    @staticmethod
    def binomial_exact(k: int, n: int, alpha: float = 0.05) -> dict:
        """Clopper-Pearson exact."""
        low = stats.beta.ppf(alpha/2, k, n-k+1) if k > 0 else 0.0
        high = stats.beta.ppf(1-alpha/2, k+1, n-k) if k < n else 1.0
        return {"p_hat": k/n if n else None, "ci_low": float(low), "ci_high": float(high)}
