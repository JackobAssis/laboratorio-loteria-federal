# # Notebook 01 — Análise Exploratória
# Execute como script ou importe no Jupyter.

from pathlib import Path
from federal_lab.data import Repository
from federal_lab.statistics import FrequencyAnalyzer, DistributionAnalyzer, SignificanceTester
from federal_lab.probability import TheoreticalProbability, ProbabilityComparison

db = Path("data/database/federal.db")
repo = Repository(db)
df = repo.get_dataframe()
print(f"Concursos: {df['concurso'].nunique()}, linhas: {len(df)}")

fa = FrequencyAnalyzer(df)
print(fa.freq_algarismos().to_string(index=False))
print(SignificanceTester.chi_square_uniform(fa.freq_algarismos()["observado"].tolist()))

da = DistributionAnalyzer(df)
print(da.paridade())
print(da.soma_digitos_stats())
