"""Configuração centralizada — nunca espalhar valores críticos pelo código."""

from pathlib import Path
from pydantic_settings import BaseSettings
from pydantic import Field


class Settings(BaseSettings):
    # Banco
    db_path: str = Field(default="data/database/federal.db", description="Caminho SQLite")
    # Dados
    data_source: str = Field(default="local", description="official | local | sqlite")
    raw_dir: str = Field(default="data/raw")
    processed_dir: str = Field(default="data/processed")

    # Estatística
    significance_level: float = Field(default=0.05, ge=0.0, le=1.0)
    random_seed: int = Field(default=42)
    monte_carlo_iterations: int = Field(default=100_000, ge=1)
    bankroll: float = Field(default=10_000.0)
    cost_per_bet: float = Field(default=5.0)

    # Período
    date_from: str | None = Field(default=None)
    date_to: str | None = Field(default=None)

    # Estratégias
    strategies: list[str] = Field(default=["random", "frequency", "recency", "distribution", "combined"])
    scoring_weights: dict = Field(default={
        "frequencia": 0.25,
        "distribuicao": 0.25,
        "recencia": 0.25,
        "caracteristicas": 0.25,
        "penalidade_complexidade": 0.1,
    })

    model_config = {
        "env_prefix": "FEDERAL_",
        "env_file": ".env",
        "extra": "ignore",
    }

    @property
    def project_root(self) -> Path:
        # src/federal_lab/config/settings.py -> project root (3 levels up from src)
        return Path(__file__).resolve().parents[3]

    def db_absolute(self) -> Path:
        p = Path(self.db_path)
        return p if p.is_absolute() else self.project_root / p


_settings: Settings | None = None

def get_settings() -> Settings:
    global _settings
    if _settings is None:
        _settings = Settings()
    return _settings
