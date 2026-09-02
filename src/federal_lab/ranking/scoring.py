"""Sistema de score experimental — NÃO é probabilidade real."""

import numpy as np

class Scorer:
    def __init__(self, pesos: dict | None = None):
        # pesos configuráveis, nunca arbitrários sem justificativa
        self.pesos = pesos or {
            "frequencia": 0.25,
            "distribuicao": 0.25,
            "recencia": 0.25,
            "caracteristicas": 0.25,
            "penalidade_complexidade": 0.1,
        }

    def score_numero(self, numero: str, historico_stats: dict) -> float:
        """
        historico_stats deve conter:
          freq_global: Counter de dígitos
          media_soma, desvio_soma
          gaps: dict term->gap
        Retorna score experimental.
        """
        s = str(numero).zfill(5)
        # componente frequência
        freq = historico_stats.get("freq", {})
        comp_freq = np.mean([freq.get(c, 0) for c in s]) if freq else 0
        # distribuição (proximidade da média)
        media = historico_stats.get("media_soma", 22.5)
        desvio = historico_stats.get("desvio_soma", 7) or 7
        soma = sum(int(c) for c in s)
        comp_dist = 1 - min(1, abs(soma - media) / (2*desvio))
        # recência
        gaps = historico_stats.get("gaps", {})
        term = s[-2:]
        gap = gaps.get(term, 0)
        max_gap = max(gaps.values()) if gaps else 1
        comp_rec = gap / max_gap if max_gap else 0
        # características (penaliza repetição extrema e sequências)
        repet = 5 - len(set(s))
        comp_carac = 1 - repet/4
        # penalidade complexidade (nº parâmetros)
        penalidade = self.pesos.get("penalidade_complexidade", 0.1)

        score = (
            self.pesos.get("frequencia", 0.25) * comp_freq
            + self.pesos.get("distribuicao", 0.25) * comp_dist
            + self.pesos.get("recencia", 0.25) * comp_rec
            + self.pesos.get("caracteristicas", 0.25) * comp_carac
            - penalidade
        )
        return float(score)
