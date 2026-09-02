"""Camada de coleta desacoplada — DataSource interface."""

from abc import ABC, abstractmethod
from pathlib import Path
from datetime import datetime, date
import hashlib
import json
from .parser import Parser

class DataSource(ABC):
    @abstractmethod
    def fetch(self) -> list[dict]:
        ...

    def metadata(self, concursos: list[dict], fonte: str) -> dict:
        payload = json.dumps(concursos, sort_keys=True, default=str)
        h = hashlib.sha256(payload.encode()).hexdigest()
        datas = [c["data_sorteio"] for c in concursos] if concursos else []
        return {
            "data_coleta": datetime.now(),
            "fonte": fonte,
            "quantidade_registros": len(concursos),
            "hash_dados": h,
            "periodo_inicio": min(datas) if datas else None,
            "periodo_fim": max(datas) if datas else None,
        }

class LocalFileSource(DataSource):
    """Lê CSV ou JSON local."""

    def __init__(self, path: str | Path):
        self.path = Path(path)

    def fetch(self) -> list[dict]:
        if not self.path.exists():
            raise FileNotFoundError(f"Arquivo não encontrado: {self.path}")
        suffix = self.path.suffix.lower()
        if suffix == ".csv":
            return Parser.parse_csv(self.path)
        elif suffix == ".json":
            return Parser.parse_json(self.path)
        else:
            raise ValueError(f"Formato não suportado: {suffix} (use .csv ou .json)")

class OfficialSource(DataSource):
    """
    Fonte oficial — placeholder desacoplado.
    Prioriza fonte oficial da CAIXA; implementação real deve fazer download
    do endpoint oficial e cachear em data/raw.
    Atualmente delega para LocalFileSource se arquivo cache existir,
    caso contrário levanta erro informativo (evita scraping frágil hard-coded).
    """

    def __init__(self, cache_path: str | Path | None = None, url: str | None = None):
        self.cache_path = Path(cache_path) if cache_path else None
        self.url = url or "https://servicebus.caixa.gov.br/portaldeloterias/api/federal"

    def fetch(self) -> list[dict]:
        # Se há cache local, usa — evita dependência de rede nos testes
        if self.cache_path and Path(self.cache_path).exists():
            return LocalFileSource(self.cache_path).fetch()
        # Tentativa de fetch real (opcional, sem quebrar se offline)
        try:
            import urllib.request
            with urllib.request.urlopen(self.url, timeout=15) as resp:
                data = json.loads(resp.read().decode())
                # Formato da API da Caixa varia; tenta normalizar
                concursos = self._normalize_api(data)
                if concursos:
                    return concursos
        except Exception as e:
            raise RuntimeError(
                f"Fonte oficial indisponível ({e}). "
                f"Forneça dados locais em data/raw/ ou configure cache_path. "
                f"URL tentada: {self.url}"
            ) from e
        raise RuntimeError("Fonte oficial retornou vazio. Use LocalFileSource.")

    @staticmethod
    def _normalize_api(data) -> list[dict]:
        # Tentativa genérica — se API retornar lista de concursos
        if isinstance(data, dict) and "concursos" in data:
            data = data["concursos"]
        if not isinstance(data, list):
            return []
        out = []
        for item in data:
            try:
                cid = int(item.get("numero") or item.get("concurso") or item.get("id"))
                data_str = item.get("dataApuracao") or item.get("data") or item.get("data_sorteio")
                from .parser import Parser
                ds = Parser._parse_date(str(data_str))
                premios = []
                lista = item.get("listaDezenas") or item.get("dezenas") or item.get("numeros") or []
                for idx, num in enumerate(lista):
                    premios.append({"posicao": idx+1, "numero": str(num).zfill(5), "valor": None})
                out.append({"concurso_id": cid, "data_sorteio": ds, "tipo_extracao": "regular", "premios": premios})
            except Exception:
                continue
        return out
