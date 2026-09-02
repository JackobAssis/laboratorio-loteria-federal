from pathlib import Path
from federal_lab.data.parser import Parser

def test_parse_csv():
    p = Path(__file__).parents[1] / "data" / "raw" / "federal_exemplo.csv"
    concursos = Parser.parse_csv(p)
    assert len(concursos) == 100
    assert concursos[0]["premios"][0]["numero"].isdigit()
    assert len(concursos[0]["premios"][0]["numero"]) == 5

def test_parse_json():
    p = Path(__file__).parents[1] / "data" / "raw" / "federal_exemplo.json"
    concursos = Parser.parse_json(p)
    assert len(concursos) == 100

def test_hash():
    p = Path(__file__).parents[1] / "data" / "raw" / "federal_exemplo.csv"
    c = Parser.parse_csv(p)
    h1 = Parser.hash_dados(c)
    h2 = Parser.hash_dados(c)
    assert h1 == h2
    assert len(h1) == 64
