from pathlib import Path
from federal_lab.data.parser import Parser
from federal_lab.statistics.frequency import FrequencyAnalyzer

def get_df():
    p = Path(__file__).parents[1] / "data" / "raw" / "federal_exemplo.csv"
    concursos = Parser.parse_csv(p)
    return Parser.to_dataframe(concursos)

def test_freq():
    df=get_df()
    fa=FrequencyAnalyzer(df)
    tbl=fa.freq_algarismos()
    assert len(tbl)==10
    assert abs(tbl["frequencia"].sum() -1) < 1e-6
    assert tbl["observado"].sum()== len(df)*5

def test_terminacoes():
    df=get_df()
    fa=FrequencyAnalyzer(df)
    t1=fa.freq_terminacoes(1)
    assert abs(t1["freq"].sum()-1) < 1e-6
    t2=fa.freq_terminacoes(2)
    assert len(t2) <= 100
