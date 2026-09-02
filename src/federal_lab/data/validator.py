"""Validações — detecta concursos duplicados, números inválidos, datas inconsistentes."""

import re
from datetime import date
from collections import Counter

NUMERO_RE = re.compile(r"^\d{5}$")

class ValidationError(Exception):
    pass

class Validator:
    @staticmethod
    def validar_numero(numero: str) -> None:
        if not isinstance(numero, str):
            raise ValidationError(f"Número deve ser string 5 dígitos, obtido {type(numero)}: {numero}")
        if not NUMERO_RE.match(numero):
            raise ValidationError(f"Número inválido (esperado 5 dígitos 00000-99999): {numero}")
        # valor int 0..99999 já garantido por regex

    @staticmethod
    def validar_concurso(concurso_id: int, data_sorteio: date, premios: list[dict]) -> None:
        if concurso_id <= 0:
            raise ValidationError(f"concurso_id inválido: {concurso_id}")
        if not isinstance(data_sorteio, date):
            raise ValidationError(f"data_sorteio deve ser date: {data_sorteio}")
        if len(premios) == 0:
            raise ValidationError(f"Concurso {concurso_id}: nenhum prêmio informado")
        if len(premios) > 10:
            raise ValidationError(f"Concurso {concurso_id}: muitos prêmios ({len(premios)})")
        posicoes = [p["posicao"] for p in premios]
        if len(posicoes) != len(set(posicoes)):
            raise ValidationError(f"Concurso {concurso_id}: posições duplicadas {posicoes}")
        for p in premios:
            Validator.validar_numero(p["numero"])
            if not 1 <= p["posicao"] <= 10:
                raise ValidationError(f"Posição inválida {p['posicao']}")
        if data_sorteio > date.today():
            raise ValidationError(f"Data futura {data_sorteio} para concurso {concurso_id}")

    @staticmethod
    def detectar_duplicados(concursos: list[dict]) -> list[int]:
        ids = [c["concurso_id"] for c in concursos]
        cnt = Counter(ids)
        return [k for k, v in cnt.items() if v > 1]

    @staticmethod
    def validar_lote(concursos: list[dict]) -> dict:
        """Valida lote inteiro. Retorna relatório."""
        duplicados = Validator.detectar_duplicados(concursos)
        erros: list[str] = []
        if duplicados:
            erros.append(f"Concursos duplicados: {duplicados}")
        for c in concursos:
            try:
                Validator.validar_concurso(c["concurso_id"], c["data_sorteio"], c["premios"])
            except ValidationError as e:
                erros.append(str(e))
        # datas inconsistentes: concurso maior deve ter data >= concurso menor (ordenação)
        ordenados = sorted(concursos, key=lambda x: x["concurso_id"])
        for i in range(1, len(ordenados)):
            if ordenados[i]["data_sorteio"] < ordenados[i-1]["data_sorteio"]:
                erros.append(
                    f"Data inconsistente: concurso {ordenados[i]['concurso_id']} "
                    f"({ordenados[i]['data_sorteio']}) anterior a {ordenados[i-1]['concurso_id']} "
                    f"({ordenados[i-1]['data_sorteio']})"
                )
                break
        return {"valido": len(erros) == 0, "erros": erros, "duplicados": duplicados}
