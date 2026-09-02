def _mock_request(ip="127.0.0.1"):
    from unittest.mock import Mock
    m = Mock()
    m.client.host = ip
    return m

def test_gerar_sem_aceite_falha():
    from federal_lab.web.app import api_gerar
    r = api_gerar({"estrategia":"random","n":5,"seed":42,"aceite":False}, _mock_request("1.1.1.1"))
    assert hasattr(r, "status_code")
    assert r.status_code == 400

def test_gerar_com_aceite():
    from federal_lab.web.app import api_gerar
    r = api_gerar({"estrategia":"frequency","n":5,"seed":42,"aceite":True,"aceite_18":True,"aceite_responsavel":True}, _mock_request("1.1.1.2"))
    assert "jogos" in r
    assert len(r["jogos"]) == 5
    assert r["prob_teorica"] == 1/100000
    assert "0,001%" in r["prob_teorica_fmt"]
    assert "EXPERIMENTAL" in r["aviso"]
    assert r["n"] == 5
    assert r["custo_total"] == 5 * 5.0
    assert "vs_random" in r

def test_gerar_limite():
    from federal_lab.web.app import api_gerar
    r = api_gerar({"estrategia":"random","n":15,"seed":42,"aceite":True,"aceite_18":True,"aceite_responsavel":True}, _mock_request("1.1.1.3"))
    assert r.status_code == 400

def test_gerar_18_falha():
    from federal_lab.web.app import api_gerar
    r = api_gerar({"estrategia":"random","n":5,"seed":42,"aceite":True,"aceite_18":False,"aceite_responsavel":True}, _mock_request("1.1.1.4"))
    assert r.status_code == 400

def test_p_hat_cap():
    from federal_lab.statistics.significance import SignificanceTester
    # gaps com média <1 deve cap p_hat em 1.0
    res = SignificanceTester.atraso_geometrico_test([0,0,0,1,0,0,1,0,1,0])
    assert res["p_hat"] <= 1.0
    assert res["p_hat"] == 1.0  # raw seria 2.4
