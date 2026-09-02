"""Modelos de dados — espelho das tabelas SQLite."""

from dataclasses import dataclass
from datetime import date, datetime

@dataclass
class Concurso:
    id: int                      # número do concurso
    data_sorteio: date
    tipo_extracao: str = "regular"  # regular, especial, etc.
    observacao: str | None = None

@dataclass
class Premio:
    concurso_id: int
    posicao: int                 # 1..5 (1º prêmio .. 5º prêmio)
    numero: str                  # 5 dígitos, ex "05327" (preserva zeros)
    valor: float | None = None

@dataclass
class ColetaMetadata:
    id: int | None
    data_coleta: datetime
    fonte: str
    quantidade_registros: int
    hash_dados: str
    periodo_inicio: date | None = None
    periodo_fim: date | None = None
