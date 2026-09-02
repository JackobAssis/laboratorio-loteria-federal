from pathlib import Path
import tempfile
from federal_lab.data.repository import Repository
from federal_lab.data.parser import Parser

def test_repo_insert_e_recupera():
    with tempfile.TemporaryDirectory() as tmp:
        db=Path(tmp)/"test.db"
        repo=Repository(db)
        p = Path(__file__).parents[1] / "data" / "raw" / "federal_exemplo.csv"
        concursos=Parser.parse_csv(p)[:5]
        repo.insert_lote(concursos)
        assert repo.count_concursos()==5
        df=repo.get_dataframe()
        assert len(df)==25  # 5 conc *5 premios
        # duplicado não aumenta
        repo.insert_lote(concursos)
        assert repo.count_concursos()==5  # INSERT OR IGNORE
