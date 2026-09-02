import pytest
from datetime import date
from federal_lab.data.validator import Validator, ValidationError

def test_numero_valido():
    Validator.validar_numero("00000")
    Validator.validar_numero("99999")

def test_numero_invalido():
    with pytest.raises(ValidationError):
        Validator.validar_numero("1234")
    with pytest.raises(ValidationError):
        Validator.validar_numero("abcde")

def test_duplicados():
    lotes = [{"concurso_id":1,"data_sorteio":date(2023,1,1),"premios":[{"posicao":1,"numero":"00001"}]},{"concurso_id":1,"data_sorteio":date(2023,1,2),"premios":[{"posicao":1,"numero":"00002"}]}]
    dups = Validator.detectar_duplicados(lotes)
    assert dups == [1]

def test_validar_lote_ok():
    lotes=[{"concurso_id":1,"data_sorteio":date(2023,1,1),"premios":[{"posicao":1,"numero":"01234"}]}]
    rep=Validator.validar_lote(lotes)
    assert rep["valido"]

def test_rejeita_datas_futuras():
    from datetime import timedelta
    lotes=[{"concurso_id":1,"data_sorteio":date.today()+timedelta(days=10),"premios":[{"posicao":1,"numero":"01234"}]}]
    rep=Validator.validar_lote(lotes)
    assert not rep["valido"]
