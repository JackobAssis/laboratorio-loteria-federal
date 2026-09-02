class SumFeatures:
    @staticmethod
    def soma(numero: str) -> int:
        return sum(int(c) for c in str(numero).zfill(5))
    @staticmethod
    def soma_paridade(numero: str) -> str:
        s = SumFeatures.soma(numero)
        return "par" if s % 2 == 0 else "impar"
    @staticmethod
    def media_digitos(numero: str) -> float:
        s = str(numero).zfill(5)
        return sum(int(c) for c in s)/5
