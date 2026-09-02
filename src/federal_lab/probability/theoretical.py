"""Probabilidade teórica — assumindo sorteio uniforme 00000-99999 por prêmio."""

import math
from scipy.stats import binom

class TheoreticalProbability:
    TOTAL = 100_000  # 00000..99999

    @staticmethod
    def prob_numero_especifico() -> float:
        return 1 / TheoreticalProbability.TOTAL

    @staticmethod
    def prob_faixa(tamanho: int) -> float:
        return tamanho / TheoreticalProbability.TOTAL

    @staticmethod
    def prob_terminacao(n_digitos: int) -> float:
        """Prob de terminar com sufixo de n dígitos (ex 2 dígitos = 1/100)."""
        return 1 / (10 ** n_digitos)

    @staticmethod
    def prob_qtd_pares(k: int) -> float:
        """Prob de exatamente k dígitos pares entre 5 (cada dígito par 5/10=0.5)."""
        return binom.pmf(k, 5, 0.5)

    @staticmethod
    def prob_soma(soma: int) -> float:
        """Prob teórica da soma dos 5 dígitos = soma (0..45). Via enumeração."""
        # conta combinações: número de 5-tuplas 0-9 com soma = s
        # usa DP
        dp = {0: 1}
        for _ in range(5):
            ndp = {}
            for acc, cnt in dp.items():
                for d in range(10):
                    ndp[acc+d] = ndp.get(acc+d, 0) + cnt
            dp = ndp
        total = 10**5
        return dp.get(soma, 0) / total

    @staticmethod
    def prob_repeticao_minima(r: int) -> float:
        """Prob de ter >= r repeticoes (5 - distintos >= r). Aproximado via enumeração."""
        cnt = 0
        for n in range(100000):
            s = f"{n:05d}"
            rep = 5 - len(set(s))
            if rep >= r:
                cnt += 1
        return cnt / 100000

    @staticmethod
    def prob_todos_iguais() -> float:
        return 10 / 100000  # 00000,11111,...,99999

    @staticmethod
    def prob_sequencia(tamanho: int = 3) -> float:
        cnt = 0
        for n in range(100000):
            s = f"{n:05d}"
            found = False
            for i in range(5 - tamanho + 1):
                janela = [int(c) for c in s[i:i+tamanho]]
                if janela == list(range(janela[0], janela[0]+tamanho)) or janela == list(range(janela[0], janela[0]-tamanho, -1)):
                    found = True
                    break
            if found:
                cnt += 1
        return cnt / 100000
