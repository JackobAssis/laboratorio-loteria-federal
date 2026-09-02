"""Parser — converte CSV/JSON bruto em estrutura normalizada."""

import csv
import json
import hashlib
from datetime import datetime, date
from pathlib import Path
from typing import Any

class Parser:
    @staticmethod
    def parse_csv(path: Path | str, encoding: str = "utf-8") -> list[dict]:
        path = Path(path)
        concursos: dict[int, dict] = {}
        with open(path, newline="", encoding=encoding) as f:
            reader = csv.DictReader(f)
            # Esperado colunas: concurso, data, posicao, numero, valor, tipo_extracao
            # Suporta variações de nome
            for row in reader:
                cid = int(str(row.get("concurso") or row.get("concurso_id") or row.get("id")).strip())
                data_raw = str(row.get("data") or row.get("data_sorteio") or "").strip()
                data_sorteio = Parser._parse_date(data_raw)
                posicao = int(str(row.get("posicao") or row.get("pos") or 1).strip())
                numero = str(row.get("numero") or row.get("numero_sorteado") or "").strip().zfill(5)
                valor_raw = row.get("valor") or row.get("valor_premio")
                valor = float(str(valor_raw).replace(",", ".").replace("R$", "").strip()) if valor_raw not in (None, "") else None
                tipo = str(row.get("tipo_extracao") or row.get("tipo") or "regular").strip() or "regular"

                if cid not in concursos:
                    concursos[cid] = {
                        "concurso_id": cid,
                        "data_sorteio": data_sorteio,
                        "tipo_extracao": tipo,
                        "premios": [],
                    }
                concursos[cid]["premios"].append({"posicao": posicao, "numero": numero, "valor": valor})
        return list(concursos.values())

    @staticmethod
    def parse_json(path: Path | str, encoding: str = "utf-8") -> list[dict]:
        path = Path(path)
        with open(path, encoding=encoding) as f:
            data = json.load(f)
        # aceita lista ou dict com chave concursos
        if isinstance(data, dict) and "concursos" in data:
            data = data["concursos"]
        concursos = []
        for item in data:
            cid = int(item["concurso_id"] if "concurso_id" in item else item["concurso"])
            data_sorteio = Parser._parse_date(str(item["data_sorteio"] if "data_sorteio" in item else item["data"]))
            premios = []
            for p in item.get("premios", item.get("numeros", [])):
                if isinstance(p, str):
                    premios.append({"posicao": len(premios)+1, "numero": p.zfill(5), "valor": None})
                elif isinstance(p, dict):
                    premios.append({
                        "posicao": int(p.get("posicao", len(premios)+1)),
                        "numero": str(p.get("numero", p.get("bilhete", ""))).zfill(5),
                        "valor": p.get("valor"),
                    })
            concursos.append({
                "concurso_id": cid,
                "data_sorteio": data_sorteio,
                "tipo_extracao": item.get("tipo_extracao", "regular"),
                "premios": premios,
            })
        return concursos

    @staticmethod
    def _parse_date(s: str) -> date:
        s = s.strip()
        for fmt in ("%Y-%m-%d", "%d/%m/%Y", "%d-%m-%Y", "%Y/%m/%d"):
            try:
                return datetime.strptime(s, fmt).date()
            except ValueError:
                continue
        raise ValueError(f"Formato de data não reconhecido: {s}")

    @staticmethod
    def hash_dados(concursos: list[dict]) -> str:
        payload = json.dumps(concursos, sort_keys=True, default=str)
        return hashlib.sha256(payload.encode()).hexdigest()

    @staticmethod
    def to_dataframe(concursos: list[dict]):
        import pandas as pd
        rows = []
        for c in concursos:
            for p in c["premios"]:
                rows.append({
                    "concurso": c["concurso_id"],
                    "data": c["data_sorteio"],
                    "tipo_extracao": c.get("tipo_extracao", "regular"),
                    "posicao": p["posicao"],
                    "numero": p["numero"],
                    "valor": p.get("valor"),
                    "d1": p["numero"][0],
                    "d2": p["numero"][1],
                    "d3": p["numero"][2],
                    "d4": p["numero"][3],
                    "d5": p["numero"][4],
                })
        df = pd.DataFrame(rows)
        if not df.empty:
            df["data"] = pd.to_datetime(df["data"])
        return df
