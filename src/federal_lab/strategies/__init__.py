from .random_strategy import RandomStrategy
from .frequency_strategy import FrequencyStrategy
from .recency_strategy import RecencyStrategy
from .distribution_strategy import DistributionStrategy
from .combined_strategy import CombinedStrategy

__all__ = ["RandomStrategy","FrequencyStrategy","RecencyStrategy","DistributionStrategy","CombinedStrategy"]

REGISTRY = {
    "random": RandomStrategy,
    "frequency": FrequencyStrategy,
    "recency": RecencyStrategy,
    "distribution": DistributionStrategy,
    "combined": CombinedStrategy,
}

def get_strategy(name: str, **kwargs):
    cls = REGISTRY.get(name)
    if not cls:
        raise ValueError(f"Estratégia desconhecida: {name}. Opções: {list(REGISTRY)}")
    return cls(**kwargs)
