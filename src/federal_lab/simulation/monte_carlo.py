"""Monte Carlo — simula milhões de concursos."""

import numpy as np
import pandas as pd

class MonteCarloSimulator:
    def __init__(self, seed: int = 42):
        self.seed = seed

    def simular_concursos(self, n_concursos: int, premios_por_concurso: int = 5, seed: int | None = None) -> pd.DataFrame:
        rng = np.random.default_rng(seed if seed is not None else self.seed)
        rows = []
        for conc in range(1, n_concursos+1):
            for pos in range(1, premios_por_concurso+1):
                num = f"{rng.integers(0,100000):05d}"
                rows.append({"concurso": conc, "posicao": pos, "numero": num})
        return pd.DataFrame(rows)

    def simular_estrategia(
        self,
        estrategia,
        n_concursos: int,
        df_history: pd.DataFrame | None = None,
        custo_por_aposta: float = 5.0,
        premios_por_concurso: int = 5,
        seed: int | None = None,
    ) -> dict:
        """
        Simula estratégia apostando em cada concurso simulado.
        Compara seleção vs números sorteados (acerto exato 5 dígitos).
        Retorna ROI, taxa acerto, etc.
        """
        rng = np.random.default_rng(seed if seed is not None else self.seed)
        # history vazio inicialmente; vai acumulando
        historico = df_history.copy() if df_history is not None and not df_history.empty else pd.DataFrame(columns=["concurso","numero","d1","d2","d3","d4","d5","posicao"])
        total_custo = 0
        total_retorno = 0
        acertos = 0
        apostas_total = 0

        # premio fictício: 1000 * custo por acerto exato (simplificado)
        premio_por_acerto = 50000  # valor ilustrativo

        for conc in range(1, n_concursos+1):
            # sorteio real
            sorteados = [f"{rng.integers(0,100000):05d}" for _ in range(premios_por_concurso)]
            # estratégia seleciona (usa historico apenas)
            try:
                selecao = estrategia.select(historico, n=5)
            except Exception:
                selecao = [f"{rng.integers(0,100000):05d}" for _ in range(5)]
            total_custo += len(selecao) * custo_por_aposta
            apostas_total += len(selecao)
            # verifica acertos
            for s in selecao:
                if s in sorteados:
                    acertos += 1
                    total_retorno += premio_por_acerto
            # atualiza historico com sorteados desse concurso
            for pos, num in enumerate(sorteados, 1):
                historico = pd.concat([historico, pd.DataFrame([{"concurso": conc, "numero": num, "d1": num[0],"d2":num[1],"d3":num[2],"d4":num[3],"d5":num[4],"posicao":pos}])], ignore_index=True)

        roi = (total_retorno - total_custo) / total_custo if total_custo else 0
        return {
            "estrategia": getattr(estrategia, "name", str(estrategia)),
            "n_concursos": n_concursos,
            "apostas": apostas_total,
            "acertos": acertos,
            "taxa_acerto": acertos / apostas_total if apostas_total else 0,
            "custo": total_custo,
            "retorno": total_retorno,
            "lucro": total_retorno - total_custo,
            "roi": roi,
        }
