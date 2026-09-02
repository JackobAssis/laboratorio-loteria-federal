class ParityFeatures:
    @staticmethod
    def qtd_pares(numero: str) -> int:
        return sum(1 for c in str(numero).zfill(5) if int(c) % 2 == 0)
    @staticmethod
    def qtd_impares(numero: str) -> int:
        return 5 - ParityFeatures.qtd_pares(numero)
    @staticmethod
    def padrao(numero: str) -> str:
        return "".join("P" if int(c)%2==0 else "I" for c in str(numero).zfill(5))
