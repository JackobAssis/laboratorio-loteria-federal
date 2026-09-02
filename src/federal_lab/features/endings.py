class EndingFeatures:
    @staticmethod
    def extrair(numero: str) -> dict:
        s = str(numero).zfill(5)
        return {"f1": s[-1:], "f2": s[-2:], "f3": s[-3:], "f4": s[-4:]}

    @staticmethod
    def termina_em(numero: str, sufixo: str) -> bool:
        return str(numero).zfill(5).endswith(sufixo)
