class RangeFeatures:
    FAIXAS = [(0,19999),(20000,39999),(40000,59999),(60000,79999),(80000,99999)]
    @staticmethod
    def faixa(numero: str | int) -> int:
        n = int(numero)
        for idx,(a,b) in enumerate(RangeFeatures.FAIXAS):
            if a <= n <= b:
                return idx
        return -1
    @staticmethod
    def label(numero: str | int) -> str:
        idx = RangeFeatures.faixa(numero)
        a,b = RangeFeatures.FAIXAS[idx]
        return f"{a:05d}-{b:05d}"
