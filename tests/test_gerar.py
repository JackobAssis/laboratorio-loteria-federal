def test_gerar_sem_aceite_falha():
    from federal_lab.web.app import api_gerar
    r = api_gerar({"estrategia":"random","n":5,"seed":42,"aceite":False})
    # deve retornar JSONResponse com erro 400
    assert hasattr(r, "status_code")
    assert r.status_code == 400

def test_gerar_com_aceite():
    from federal_lab.web.app import api_gerar
    r = api_gerar({"estrategia":"frequency","n":5,"seed":42,"aceite":True})
    assert "jogos" in r
    assert len(r["jogos"]) == 5
    assert r["prob_teorica"] == 1/100000
    assert "0,001%" in r["prob_teorica_fmt"]
    assert "EXPERIMENTAL" in r["aviso"]
    assert r["n"] == 5
    # vs_random deve existir se houver dados
    assert "vs_random" in r

def test_gerar_limite():
    from federal_lab.web.app import api_gerar
    r = api_gerar({"estrategia":"random","n":15,"seed":42,"aceite":True})
    assert r.status_code == 400

def test_p_hat_cap():
    from federal_lab.statistics.significance import SignificanceTester
    # gaps com média <1 deve cap p_hat em 1.0
    res = SignificanceTester.atraso_geometrico_test([0,0,0,1,0,0,1,0,1,0])
    assert res["p_hat"] <= 1.0
    assert res["p_hat"] == 1.0  # raw seria 2.4
