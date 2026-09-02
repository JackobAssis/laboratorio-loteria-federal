"""Interface Web — Laboratório Estatístico da Loteria Federal
FastAPI + Jinja2 + Chart.js. Roda com `federal web` ou `uvicorn federal_lab.web.app:app`.
Princípio: nunca apresentar padrão como vantagem sem significância out-of-sample.
"""

from fastapi import FastAPI, UploadFile, File, Request, Form
from fastapi.responses import HTMLResponse, JSONResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pathlib import Path
import pandas as pd
import numpy as np
import tempfile
import shutil

from federal_lab.config import get_settings
from federal_lab.data import Repository, LocalFileSource, Validator
from federal_lab.data.parser import Parser
from federal_lab.statistics import FrequencyAnalyzer, DistributionAnalyzer, SignificanceTester
from federal_lab.statistics.correlations import CorrelationAnalyzer
from federal_lab.probability import TheoreticalProbability, ProbabilityComparison
from federal_lab.simulation import Backtester, Benchmark, MonteCarloSimulator
from federal_lab.simulation.overfitting import OverfittingDetector
from federal_lab.strategies import get_strategy

BASE = Path(__file__).resolve().parents[3]  # project root
TEMPLATES_DIR = Path(__file__).parent / "templates"
STATIC_DIR = Path(__file__).parent / "static"
STATIC_DIR.mkdir(parents=True, exist_ok=True)
REPORTS_DIR = BASE / "reports"
REPORTS_DIR.mkdir(exist_ok=True)

app = FastAPI(title="Federal Lab", version="0.1.0", description="Laboratório Estatístico da Loteria Federal — interface experimental")

# mount static
app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")
# serve reports PNGs gerados por federal report
app.mount("/reports", StaticFiles(directory=str(REPORTS_DIR)), name="reports")
templates = Jinja2Templates(directory=str(TEMPLATES_DIR))

def get_repo():
    cfg = get_settings()
    return Repository(cfg.db_absolute())

def sanitize(obj):
    """Converte NaN/Inf e numpy scalars para JSON compliant recursivamente."""
    if isinstance(obj, dict):
        return {k: sanitize(v) for k,v in obj.items()}
    if isinstance(obj, (list, tuple)):
        return [sanitize(v) for v in obj]
    if isinstance(obj, np.generic):
        # converte numpy scalar (int64, float64, bool_) para python nativo
        try:
            v = obj.item()
        except Exception:
            v = float(obj) if isinstance(obj, (np.floating, np.integer)) else bool(obj)
        return sanitize(v)
    if isinstance(obj, float):
        if np.isnan(obj) or np.isinf(obj):
            return None
        return obj
    if isinstance(obj, bool):
        return bool(obj)
    return obj

def get_df():
    repo = get_repo()
    return repo.get_dataframe()

@app.get("/", response_class=HTMLResponse)
def dashboard(request: Request):
    return templates.TemplateResponse(request, "dashboard.html")

@app.get("/api/status")
def api_status():
    repo = get_repo()
    df = repo.get_dataframe()
    meta = repo.get_metadata() or {}
    if df.empty:
        return {"concursos": 0, "linhas": 0, "periodo": "—", "fonte": "—", "hash": "—"}
    return {
        "concursos": int(df["concurso"].nunique()),
        "linhas": int(len(df)),
        "periodo": f"{df['data'].min().date()} a {df['data'].max().date()}",
        "fonte": meta.get("fonte", "local"),
        "hash": (meta.get("hash_dados") or "—")[:16],
    }

@app.get("/api/frequency")
def api_frequency():
    df = get_df()
    if df.empty:
        return {"error": "sem dados"}
    fa = FrequencyAnalyzer(df)
    freq = fa.freq_algarismos()
    term1 = fa.freq_terminacoes(1)
    por_pos = fa.freq_por_posicao()
    return {
        "algarismos": freq.to_dict(orient="records"),
        "terminacoes_1d": term1.to_dict(orient="records"),
        "por_posicao": por_pos.to_dict(orient="records"),
    }

@app.get("/api/distribution")
def api_distribution():
    df = get_df()
    if df.empty:
        return {"error": "sem dados"}
    da = DistributionAnalyzer(df)
    return sanitize({
        "faixa": da.por_faixa(bins=5).to_dict(orient="records"),
        "paridade": da.paridade().to_dict(orient="records"),
        "soma": da.soma_digitos_stats()["media"] if hasattr(da.soma_digitos_stats(),"__getitem__") else str(da.soma_digitos_stats()),
        "soma_stats": {k: float(v) if isinstance(v, (int,float,np.floating, np.generic)) else str(v) for k,v in da.soma_digitos_stats().items() if k != "dist"},
    })

@app.get("/api/tests")
def api_tests():
    df = get_df()
    if df.empty:
        return {"error": "sem dados"}
    fa = FrequencyAnalyzer(df)
    freq = fa.freq_algarismos()
    chi = SignificanceTester.chi_square_uniform(freq["observado"].tolist())
    runs = SignificanceTester.runs_test(df["numero"].astype(int).tolist())
    auto = SignificanceTester.autocorrelacao_lag1(df["numero"].astype(int).tolist())
    ca = CorrelationAnalyzer(df)
    correl = ca.correlacao_soma_concurso()
    sorted_df = df.sort_values("concurso")
    ocorrencias = sorted_df[sorted_df["numero"].str.contains("7")]["concurso"].tolist()
    gaps = [ocorrencias[i]-ocorrencias[i-1] for i in range(1,len(ocorrencias))] if len(ocorrencias)>1 else []
    gap_test = SignificanceTester.atraso_geometrico_test(gaps) if gaps else {"p_value": None}
    p_vals = [chi["p_value"], runs.get("p_value") or 1, auto.get("p_value") or 1, correl["p_value"]]
    p_bonf = SignificanceTester.corrigir_multiplos(p_vals, "bonferroni")
    p_bh = SignificanceTester.corrigir_multiplos(p_vals, "bh")
    return sanitize({
        "chi2": chi,
        "runs": runs,
        "autocorr": auto,
        "correl": correl,
        "gap": {"n_gaps": len(gaps), "test": gap_test},
        "correcao": {"originais": p_vals, "bonferroni": p_bonf, "bh": p_bh},
    })

@app.get("/api/probability")
def api_probability():
    df = get_df()
    if df.empty:
        return {"error": "sem dados"}
    k = int((df["numero"].str[-1]=="0").sum())
    comp = ProbabilityComparison.comparar_proporcao(k, len(df), TheoreticalProbability.prob_terminacao(1))
    return sanitize({"k": k, "n": len(df), "comparacao": comp, "tabela_qtd_pares": ProbabilityComparison.tabela_completa(df).to_dict(orient="records")})

@app.post("/api/simulate")
def api_simulate(payload: dict):
    strategy = payload.get("strategy", "random")
    iterations = int(payload.get("iterations", 1000))
    seed = int(payload.get("seed", 42))
    repo = get_repo()
    df = repo.get_dataframe()
    sim = MonteCarloSimulator(seed=seed)
    strat = get_strategy(strategy, seed=seed)
    res = sim.simular_estrategia(strat, n_concursos=iterations, df_history=df if not df.empty else None, seed=seed)
    return sanitize(res)

@app.post("/api/backtest")
def api_backtest(payload: dict):
    strategies = payload.get("strategies", ["random","frequency","recency","distribution","combined"])
    if isinstance(strategies, str):
        strategies = [s.strip() for s in strategies.split(",")]
    df = get_df()
    if df.empty or df["concurso"].nunique() < 25:
        return {"error": "dados insuficientes (<25 concursos)"}
    bt = Backtester()
    bench = Benchmark()
    resultados = {}
    for name in strategies:
        try:
            strat = get_strategy(name)
            resultados[name] = bt.run(df, strat)
        except Exception as e:
            resultados[name] = pd.DataFrame()
    tbl = bench.compare_backtests(resultados)
    sig = {}
    if "random" in resultados:
        for name, res in resultados.items():
            if name=="random" or res.empty or resultados["random"].empty:
                continue
            sig[name] = bench.significancia_vs_baseline(res, resultados["random"])
    return sanitize({
        "benchmark": tbl.to_dict(orient="records") if not tbl.empty else [],
        "significancia": sig,
    })

@app.get("/api/overfitting")
def api_overfitting():
    df = get_df()
    if df.empty:
        return {"error": "sem dados"}
    od = OverfittingDetector()
    over = od.avaliar(df, get_strategy("frequency"))
    # remove DataFrames brutos (não serializáveis) — mantém só splits resumidos
    over_clean = {k: v for k,v in over.items() if k != "detalhe"}
    wf = od.walk_forward_diagnostico(df, get_strategy("frequency"))
    return sanitize({"split": over_clean, "walk_forward": wf})

@app.get("/api/ml")
def api_ml():
    df = get_df()
    if df.empty:
        return {"error": "sem dados"}
    from federal_lab.ml import MLEvaluator
    res = MLEvaluator().avaliar(df)
    return res

@app.post("/api/gerar")
def api_gerar(payload: dict):
    """
    Gera jogos com atrito e disclaimer obrigatório.
    Payload: {estrategia: str, n: int (1..10), seed: int, aceite: bool}
    Retorna jogos + aviso + prob_teorica fixa + comparação vs random.
    Nunca promete vantagem.
    """
    estrategia = payload.get("estrategia", "random")
    n = int(payload.get("n", 5))
    seed = int(payload.get("seed", 42))
    aceite = bool(payload.get("aceite", False))
    if not aceite:
        return JSONResponse({"error": "Você deve aceitar o aviso: entendo que é experimental, cada bilhete tem 1/100000 (0.001%) e ROI esperado ≈ -1"}, status_code=400)
    if not 1 <= n <= 10:
        return JSONResponse({"error": "n deve ser 1..10"}, status_code=400)
    if estrategia not in ["random","frequency","recency","distribution","combined"]:
        return JSONResponse({"error": f"estrategia inválida {estrategia}"}, status_code=400)
    df = get_df()
    repo = get_repo()
    meta = repo.get_metadata() or {}
    # gera
    strat = get_strategy(estrategia, seed=seed)
    jogos = strat.select(df if not df.empty else pd.DataFrame(), n=n)
    # contexto estatístico
    prob_teorica = TheoreticalProbability.prob_numero_especifico()  # 0.00001
    # compara estratégia vs random no histórico (se houver dados)
    vs_random = None
    if not df.empty and df["concurso"].nunique() >= 25:
        try:
            bt = Backtester()
            bench = Benchmark()
            r_estr = bt.run(df, strat)
            r_rand = bt.run(df, get_strategy("random", seed=seed))
            vs_random = bench.significancia_vs_baseline(r_estr, r_rand)
            vs_random = sanitize(vs_random)
        except Exception as e:
            vs_random = {"erro": str(e)}
    # ranking experimental (não prob)
    try:
        from federal_lab.ranking import Scorer, Ranker
        scorer = Scorer()
        # stats históricos para score
        historico_stats = {}
        if not df.empty:
            from collections import Counter
            freq = Counter("".join(df["numero"].astype(str)))
            total = sum(freq.values())
            historico_stats["freq"] = {k: v/total for k,v in freq.items()}
            historico_stats["media_soma"] = float(df["numero"].apply(lambda x: sum(int(c) for c in str(x))).mean())
            historico_stats["desvio_soma"] = float(df["numero"].apply(lambda x: sum(int(c) for c in str(x))).std() or 7)
            # gaps 2d
            gaps = {}
            sd = df.sort_values("concurso")
            ultimo = sd["concurso"].max()
            term_last = {}
            for _, row in sd.iterrows():
                term_last[str(row["numero"])[-2:]] = row["concurso"]
            for term, last in term_last.items():
                gaps[term] = int(ultimo - last)
            historico_stats["gaps"] = gaps
        ranker = Ranker(scorer)
        ranking = ranker.rank(jogos, historico_stats)
        ranking_records = ranking.to_dict(orient="records")
    except Exception:
        ranking_records = [{"numero": j, "score": None, "aviso": "ranking experimental"} for j in jogos]

    return sanitize({
        "jogos": jogos,
        "ranking": ranking_records,
        "estrategia": estrategia,
        "n": n,
        "seed": seed,
        "prob_teorica": prob_teorica,
        "prob_teorica_pct": prob_teorica * 100,
        "prob_teorica_fmt": "1 em 100.000 (0,001%)",
        "roi_esperado": -1.0,
        "hash_dados": (meta.get("hash_dados") or "—")[:16],
        "periodo": f"{df['data'].min().date()} a {df['data'].max().date()}" if not df.empty and "data" in df else "—",
        "vs_random": vs_random,
        "aviso": "AVISO: Jogos são ranking EXPERIMENTAL, NÃO probabilidade real. Cada bilhete tem 0,001% independente do histórico. Histórico não altera sorteio se processo for aleatório. ROI esperado ≈ -1 (perda). Backtest 600 concursos p=1.0 sem superioridade vs random. Não foi encontrada evidência de vantagem.",
        "regras": [
            "Probabilidade por bilhete: 1/100.000 (fixa)",
            "Ranking ≠ probabilidade",
            "Nenhum padrão sem p<0.05 out-of-sample + BH foi considerado vantagem",
            "Limite 10 jogos por geração para evitar ilusão de cobertura"
        ]
    })

@app.get("/api/report")
def api_report():
    # gera relatório e retorna markdown
    import subprocess, sys
    cfg = get_settings()
    # chama CLI report via subprocess seria mais lento; faz direto
    from federal_lab.cli.main import report as cli_report
    # não dá para chamar click diretamente; gera via função auxiliar
    # simplifica: lê reports/relatorio.md se existir, senão gera
    report_path = BASE / "reports" / "relatorio.md"
    if not report_path.exists():
        return {"error": "relatório não gerado. Rode federal report."}
    return {"markdown": report_path.read_text(encoding="utf-8")}

@app.post("/api/upload")
async def api_upload(file: UploadFile = File(...)):
    suffix = Path(file.filename).suffix.lower()
    if suffix not in [".csv", ".json"]:
        return JSONResponse({"error": "formato deve ser .csv ou .json"}, status_code=400)
    with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
        shutil.copyfileobj(file.file, tmp)
        tmp_path = Path(tmp.name)
    try:
        ds = LocalFileSource(tmp_path)
        concursos = ds.fetch()
        val = Validator.validar_lote(concursos)
        if not val["valido"]:
            return JSONResponse({"error": val["erros"]}, status_code=400)
        repo = get_repo()
        repo.insert_lote(concursos)
        meta = ds.metadata(concursos, "upload")
        repo.insert_metadata(meta["data_coleta"], meta["fonte"], meta["quantidade_registros"], meta["hash_dados"], meta["periodo_inicio"], meta["periodo_fim"])
        return {"ok": True, "concursos": len(concursos), "hash": meta["hash_dados"][:12]}
    finally:
        tmp_path.unlink(missing_ok=True)

# compat CLI `federal web` usa esta função
def run(host: str = "127.0.0.1", port: int = 8000, reload: bool = False):
    import uvicorn
    uvicorn.run("federal_lab.web.app:app", host=host, port=port, reload=reload)
