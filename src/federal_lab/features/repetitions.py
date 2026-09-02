from collections import Counter
class RepetitionFeatures:
    @staticmethod
    def repeticoes(numero: str) -> int:
        return 5 - len(set(str(numero).zfill(5)))
    @staticmethod
    def tem_repeticao(numero: str) -> bool:
        return RepetitionFeatures.repeticoes(numero) > 0
    @staticmethod
    def todos_iguais(numero: str) -> bool:
        return len(set(str(numero).zfill(5))) == 1
    @staticmethod
    def sequencia(numero: str, tamanho: int = 3) -> bool:
        s = str(numero).zfill(5)
        for i in range(len(s)-tamanho+1):
            janela = [int(c) for c in s[i:i+tamanho]]
            if janela == list(range(janela[0], janela[0]+tamanho)):
                return True
            if janela == list(range(janela[0], janela[0]-tamanho, -1)):
                return True
        return False
    @staticmethod
    def padrao_repeticao(numero: str) -> str:
        cnt = Counter(str(numero).zfill(5))
        # ex 11234 -> 2-1-1-1
        return "-".join(map(str, sorted(cnt.values(), reverse=True)))
