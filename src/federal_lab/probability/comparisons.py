"""Comparação teoria vs empírico."""

import pandas as pd
from scipy import stats
from .theoretical import TheoreticalProbability
from ..statistics.confidence import ConfidenceInterval

class ProbabilityComparison:
    @staticmethod
    def comparar_proporcao(k: int, n: int, p_teorica: float, alpha: float = 0.05) -> dict:
        """Teste binomial: H0 p=p_teorica."""
        # binomtest (scipy >=1.10)
        res = stats.binomtest(k, n, p_teorica)
        p_val = res.pvalue
        ci = ConfidenceInterval.proporcao_wilson(k, n, alpha)
        dentro = ci["ci_low"] <= p_teorica <= ci["ci_high"]
        return {
            "k": k, "n": n, "p_teorica": p_teorica,
            "p_hat": k/n if n else None,
            "ci_low": ci["ci_low"], "ci_high": ci["ci_high"],
            "p_value": float(p_val),
            "dentro_IC": dentro,
            "H0": f"p = {p_teorica}",
            "conclusao": "Não rejeita H0 (compatível)" if p_val >= alpha else "Rejeita H0 (diferença significativa)",
            "aviso": "Se sorteio é aleatório, diferença observada é flutuação amostral até prova de significância fora da amostra."
        }

    @staticmethod
    def tabela_completa(df: pd.DataFrame) -> pd.DataFrame:
        """Exemplo: compara cada característica observada vs teórica."""
        total = len(df)
        # exemplo qtd pares
        from collections import Counter
        cnt = Counter(df["numero"].apply(lambda x: sum(1 for c in str(x) if int(c)%2==0)))
        rows = []
        for k in range(6):
            obs = cnt.get(k, 0)
            p_teo = TheoreticalProbability.prob_qtd_pares(k)
            comp = ProbabilityComparison.comparar_proporcao(obs, total, p_teo)
            rows.append({"qtd_pares": k, **comp})
        return pd.DataFrame(rows)
