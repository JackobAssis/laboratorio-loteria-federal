import http.client, json, time, subprocess, signal, os, pathlib

def test_web_endpoints():
    # testa funções diretas sem servidor
    from federal_lab.web.app import api_status, api_frequency, api_tests, api_probability, api_overfitting, api_ml
    s = api_status()
    assert "concursos" in s
    f = api_frequency()
    assert "algarismos" in f
    t = api_tests()
    assert "chi2" in t
    p = api_probability()
    assert "k" in p
    o = api_overfitting()
    assert "split" in o
    m = api_ml()
    assert "leakage_ok" in m or "erro" in m

def test_sanitize():
    from federal_lab.web.app import sanitize
    import numpy as np
    assert sanitize({"a": np.True_})["a"] is True
    assert sanitize({"a": np.int64(5)})["a"] == 5.0
    assert sanitize({"a": float("nan")})["a"] is None
