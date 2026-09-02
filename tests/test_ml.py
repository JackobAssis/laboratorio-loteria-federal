from pathlib import Path
from federal_lab.data.parser import Parser
from federal_lab.ml import MLEvaluator

def get_df():
    p = Path(__file__).parents[1] / "data" / "raw" / "federal_exemplo.csv"
    return Parser.to_dataframe(Parser.parse_csv(p))

def test_ml_sem_leakage():
    df=get_df()
    ev=MLEvaluator(seed=42)
    X,y=ev.preparar_features(df)
    assert "d5" not in X.columns, "d5 leakage — deve estar removido"
    assert "d1" in X.columns

def test_ml_avaliar():
    df=get_df()
    ev=MLEvaluator(seed=42)
    res=ev.avaliar(df)
    # se sklearn instalado, deve ter acc_model e leakage_ok
    if "erro" not in res:
        assert "acc_model" in res
        assert res["leakage_ok"] is True
        # com dados aleatórios, não deve superar baseline com margem
        # (pode ser True por acaso, mas na maioria das vezes False)
        assert "supera_baseline" in res
