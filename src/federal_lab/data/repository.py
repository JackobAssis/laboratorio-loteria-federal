"""Repository — SQLite com migração para PostgreSQL via DATABASE_URL."""

import sqlite3
import os
from pathlib import Path
from datetime import datetime, date
from contextlib import contextmanager

SCHEMA = """
PRAGMA foreign_keys = ON;

CREATE TABLE IF NOT EXISTS concursos (
    id INTEGER PRIMARY KEY,
    data_sorteio TEXT NOT NULL,
    tipo_extracao TEXT NOT NULL DEFAULT 'regular',
    observacao TEXT,
    created_at TEXT NOT NULL DEFAULT (datetime('now')),
    UNIQUE(id)
);

CREATE TABLE IF NOT EXISTS premios (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    concurso_id INTEGER NOT NULL REFERENCES concursos(id) ON DELETE CASCADE,
    posicao INTEGER NOT NULL,
    numero TEXT NOT NULL CHECK(length(numero)=5),
    valor REAL,
    UNIQUE(concurso_id, posicao)
);

CREATE TABLE IF NOT EXISTS coleta_metadata (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    data_coleta TEXT NOT NULL,
    fonte TEXT NOT NULL,
    quantidade_registros INTEGER NOT NULL,
    hash_dados TEXT NOT NULL,
    periodo_inicio TEXT,
    periodo_fim TEXT
);

CREATE TABLE IF NOT EXISTS analises (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    tipo TEXT NOT NULL,
    parametros TEXT,
    resultado TEXT,
    created_at TEXT NOT NULL DEFAULT (datetime('now'))
);

CREATE TABLE IF NOT EXISTS simulacoes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    estrategia TEXT NOT NULL,
    iteracoes INTEGER NOT NULL,
    seed INTEGER,
    resultado TEXT,
    created_at TEXT NOT NULL DEFAULT (datetime('now'))
);

CREATE TABLE IF NOT EXISTS backtests (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    estrategia TEXT NOT NULL,
    concurso_teste INTEGER NOT NULL,
    selecao TEXT,
    acertos INTEGER,
    custo REAL,
    retorno REAL,
    roi REAL
);
"""

SCHEMA_PG = """
CREATE TABLE IF NOT EXISTS concursos (
    id INTEGER PRIMARY KEY,
    data_sorteio TEXT NOT NULL,
    tipo_extracao TEXT NOT NULL DEFAULT 'regular',
    observacao TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    UNIQUE(id)
);
CREATE TABLE IF NOT EXISTS premios (
    id SERIAL PRIMARY KEY,
    concurso_id INTEGER NOT NULL REFERENCES concursos(id) ON DELETE CASCADE,
    posicao INTEGER NOT NULL,
    numero TEXT NOT NULL CHECK(length(numero)=5),
    valor DOUBLE PRECISION,
    UNIQUE(concurso_id, posicao)
);
CREATE TABLE IF NOT EXISTS coleta_metadata (
    id SERIAL PRIMARY KEY,
    data_coleta TIMESTAMPTZ NOT NULL,
    fonte TEXT NOT NULL,
    quantidade_registros INTEGER NOT NULL,
    hash_dados TEXT NOT NULL,
    periodo_inicio TEXT,
    periodo_fim TEXT
);
CREATE TABLE IF NOT EXISTS analises (
    id SERIAL PRIMARY KEY,
    tipo TEXT NOT NULL,
    parametros TEXT,
    resultado TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
CREATE TABLE IF NOT EXISTS simulacoes (
    id SERIAL PRIMARY KEY,
    estrategia TEXT NOT NULL,
    iteracoes INTEGER NOT NULL,
    seed INTEGER,
    resultado TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
CREATE TABLE IF NOT EXISTS backtests (
    id SERIAL PRIMARY KEY,
    estrategia TEXT NOT NULL,
    concurso_teste INTEGER NOT NULL,
    selecao TEXT,
    acertos INTEGER,
    custo DOUBLE PRECISION,
    retorno DOUBLE PRECISION,
    roi DOUBLE PRECISION
);
"""

class Repository:
    def __init__(self, db_path: str | Path):
        # suporta postgres URL ou sqlite path
        db_str = str(db_path)
        self.is_postgres = db_str.startswith(("postgres://", "postgresql://"))
        self.db_url = db_str if self.is_postgres else None
        if self.is_postgres:
            # tenta psycopg, senão fallback sqlite com aviso
            try:
                import psycopg  # noqa: F401
                self.db_path = None
            except ImportError:
                print("AVISO: DATABASE_URL postgres detectado mas psycopg não instalado. Usando SQLite fallback. Instale: pip install psycopg[binary]")
                self.is_postgres = False
                self.db_url = None
                self.db_path = Path("data/database/federal.db")
                self.db_path.parent.mkdir(parents=True, exist_ok=True)
        else:
            self.db_path = Path(db_path)
            self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._init_db()

    def _connect(self):
        if self.is_postgres:
            import psycopg
            conn = psycopg.connect(self.db_url)
            return conn
        conn = sqlite3.connect(str(self.db_path), detect_types=sqlite3.PARSE_DECLTYPES)
        conn.row_factory = sqlite3.Row
        return conn

    def _ph(self):
        return "%s" if self.is_postgres else "?"

    @contextmanager
    def _cursor(self):
        conn = self._connect()
        try:
            if self.is_postgres:
                import psycopg.rows
                cur = conn.cursor(row_factory=psycopg.rows.dict_row)
            else:
                cur = conn.cursor()
            yield cur
            conn.commit()
        finally:
            conn.close()

    def _init_db(self):
        if self.is_postgres:
            with self._cursor() as cur:
                cur.execute(SCHEMA_PG)
            return
        with self._cursor() as cur:
            cur.executescript(SCHEMA)

    # — concursos / prêmios —
    def insert_concurso(self, concurso_id: int, data_sorteio: date, tipo_extracao: str = "regular", observacao: str | None = None):
        with self._cursor() as cur:
            ph = self._ph()
            if self.is_postgres:
                cur.execute(
                    f"INSERT INTO concursos (id, data_sorteio, tipo_extracao, observacao) VALUES ({ph},{ph},{ph},{ph}) ON CONFLICT (id) DO NOTHING",
                    (concurso_id, data_sorteio.isoformat(), tipo_extracao, observacao),
                )
            else:
                cur.execute(
                    "INSERT OR IGNORE INTO concursos (id, data_sorteio, tipo_extracao, observacao) VALUES (?,?,?,?)",
                    (concurso_id, data_sorteio.isoformat(), tipo_extracao, observacao),
                )

    def insert_premio(self, concurso_id: int, posicao: int, numero: str, valor: float | None = None):
        with self._cursor() as cur:
            ph = self._ph()
            if self.is_postgres:
                cur.execute(
                    f"INSERT INTO premios (concurso_id, posicao, numero, valor) VALUES ({ph},{ph},{ph},{ph}) ON CONFLICT (concurso_id, posicao) DO UPDATE SET numero=EXCLUDED.numero, valor=EXCLUDED.valor",
                    (concurso_id, posicao, numero, valor),
                )
            else:
                cur.execute(
                    "INSERT OR REPLACE INTO premios (concurso_id, posicao, numero, valor) VALUES (?,?,?,?)",
                    (concurso_id, posicao, numero, valor),
                )

    def insert_lote(self, concursos: list[dict]):
        for c in concursos:
            self.insert_concurso(c["concurso_id"], c["data_sorteio"], c.get("tipo_extracao", "regular"))
            for p in c["premios"]:
                self.insert_premio(c["concurso_id"], p["posicao"], p["numero"], p.get("valor"))

    def get_concursos(self) -> list[dict]:
        with self._cursor() as cur:
            cur.execute("SELECT * FROM concursos ORDER BY id")
            concursos = {row["id"]: {"concurso_id": row["id"], "data_sorteio": date.fromisoformat(row["data_sorteio"]), "tipo_extracao": row["tipo_extracao"], "premios": []} for row in cur.fetchall()}
            cur.execute("SELECT * FROM premios ORDER BY concurso_id, posicao")
            for row in cur.fetchall():
                cid = row["concurso_id"]
                if cid in concursos:
                    concursos[cid]["premios"].append({"posicao": row["posicao"], "numero": row["numero"], "valor": row["valor"]})
            return list(concursos.values())

    def count_concursos(self) -> int:
        with self._cursor() as cur:
            cur.execute("SELECT COUNT(*) as cnt FROM concursos")
            return cur.fetchone()["cnt"]

    def get_dataframe(self):
        import pandas as pd
        concursos = self.get_concursos()
        from .parser import Parser
        return Parser.to_dataframe(concursos)

    # — metadata —
    def insert_metadata(self, data_coleta: datetime, fonte: str, quantidade: int, hash_dados: str, periodo_inicio=None, periodo_fim=None):
        with self._cursor() as cur:
            ph = self._ph()
            cur.execute(
                f"INSERT INTO coleta_metadata (data_coleta, fonte, quantidade_registros, hash_dados, periodo_inicio, periodo_fim) VALUES ({ph},{ph},{ph},{ph},{ph},{ph})",
                (data_coleta.isoformat(), fonte, quantidade, hash_dados,
                 periodo_inicio.isoformat() if periodo_inicio else None,
                 periodo_fim.isoformat() if periodo_fim else None),
            )

    def get_metadata(self):
        with self._cursor() as cur:
            cur.execute("SELECT * FROM coleta_metadata ORDER BY id DESC LIMIT 1")
            row = cur.fetchone()
            return dict(row) if row else None

    # — util —
    def clear_all(self):
        with self._cursor() as cur:
            cur.execute("DELETE FROM premios")
            cur.execute("DELETE FROM concursos")
            cur.execute("DELETE FROM coleta_metadata")

    def hash_atual(self) -> str | None:
        meta = self.get_metadata()
        return meta["hash_dados"] if meta else None
