from pathlib import Path
from federal_lab.data.parser import Parser
from federal_lab.simulation.overfitting import OverfittingDetector
from federal_lab.strategies import get_strategy

def get_df():
    p = Path(__file__).parents[1] / "data" / "raw" / "federal_exemplo.csv"
    return Parser.to_dataframe(Parser.parse_csv(p))

def test_split_temporal():
    df=get_df()
    od=OverfittingDetector()
    splits=od.split_temporal(df, 0.6,0.2)
    assert "train" in splits and "val" in splits and "test" in splits
    assert len(splits["train"])+len(splits["val"])+len(splits["test"])==len(df)

def test_avaliar():
    df=get_df()
    od=OverfittingDetector()
    res=od.avaliar(df, get_strategy("random", seed=42))
    assert "overfit_suspeito" in res

def test_walk_forward():
    df=get_df()
    od=OverfittingDetector()
    wf=od.walk_forward_diagnostico(df, get_strategy("random", seed=42), train_size=20, test_size=5)
    assert "estavel" in wf
