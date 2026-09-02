"""CLI — federal fetch/validate/analyze/probability/simulate/backtest/compare/report"""

import click
from pathlib import Path
import pandas as pd
import numpy as np
from federal_lab.config import get_settings
from federal_lab.data import Repository, LocalFileSource, OfficialSource, Validator
from federal_lab.data.parser import Parser

@click.group()
def cli():
    """Laboratório Estatístico da Loteria Federal"""
    pass

@cli.command()
@click.option("--source", default="local", help="official | local")
@click.option("--file", "filepath", default=None, help="caminho CSV/JSON local")
@click.option("--db", default=None, help="caminho DB SQLite")
def fetch(source, filepath, db):
    cfg = get_settings()
    db_path = db if db else cfg.get_db_path_or_url()
    repo = Repository(db_path)
    if source == "official":
        ds = OfficialSource(cache_path=filepath)
    else:
        if not filepath:
            for p in [Path(cfg.raw_dir)/"federal.csv", Path(cfg.raw_dir)/"federal.json", Path("data/raw/federal.csv")]:
                if p.exists():
                    filepath = str(p)
                    break
            if not filepath:
                click.echo("Forneça --file para fonte local ou coloque arquivo em data/raw/federal.csv")
                raise SystemExit(1)
        ds = LocalFileSource(filepath)
    concursos = ds.fetch()
    meta = ds.metadata(concursos, source)
    val = Validator.validar_lote(concursos)
    if not val["valido"]:
        click.echo(f"Validação falhou: {val['erros']}")
        raise SystemExit(1)
    repo.insert_lote(concursos)
    repo.insert_metadata(meta["data_coleta"], meta["fonte"], meta["quantidade_registros"], meta["hash_dados"], meta["periodo_inicio"], meta["periodo_fim"])
    click.echo(f"✓ {len(concursos)} concursos inseridos em {db_path} (hash {meta['hash_dados'][:12]}...)")

@cli.command()
@click.option("--db", default=None)
def validate(db):
    cfg = get_settings()
    db_path = db if db else cfg.get_db_path_or_url()
    repo = Repository(db_path)
    concursos = repo.get_concursos()
    rep = Validator.validar_lote(concursos)
    click.echo(f"Total: {len(concursos)} concursos")
    click.echo(f"Válido: {rep['valido']}")
    for e in rep["erros"]:
        click.echo(f"  - {e}")
    if rep["valido"]:
        click.echo("✓ validação OK")

@cli.command()
@click.option("--db", default=None)
@click.option("--from", "date_from", default=None)
@click.option("--to", "date_to", default=None)
def analyze(db, date_from, date_to):
    from federal_lab.statistics import FrequencyAnalyzer, DistributionAnalyzer
    cfg = get_settings()
    db_path = db if db else cfg.get_db_path_or_url()
    repo = Repository(db_path)
    df = repo.get_dataframe()
    if df.empty:
        click.echo("Sem dados. Rode 'federal fetch' primeiro.")
        raise SystemExit(1)
    fa = FrequencyAnalyzer(df)
    da = DistributionAnalyzer(df)
    click.echo(f"Concursos: {df['concurso'].nunique()}  Linhas: {len(df)}")
    click.echo("\n-- Frequência algarismos --")
    click.echo(fa.freq_algarismos().to_string(index=False))
    click.echo("\n-- Terminações 1 dígito --")
    click.echo(fa.freq_terminacoes(1).head(10).to_string(index=False))
    click.echo("\n-- Paridade --")
    click.echo(da.paridade().to_string(index=False))
    click.echo("\n-- Soma dígitos --")
    s = da.soma_digitos_stats()
    click.echo(f"media {s['media']:.2f} mediana {s['mediana']:.2f} desvio {s['desvio']:.2f}")

@cli.command(name="probability")
@click.option("--db", default=None)
def probability_cmd(db):
    from federal_lab.probability import TheoreticalProbability, ProbabilityComparison
    cfg = get_settings()
    db_path = db if db else cfg.get_db_path_or_url()
    repo = Repository(db_path)
    df = repo.get_dataframe()
    if df.empty:
        click.echo("Sem dados.")
        raise SystemExit(1)
    k = (df["numero"].str[-1] == "0").sum()
    comp = ProbabilityComparison.comparar_proporcao(int(k), len(df), TheoreticalProbability.prob_terminacao(1))
    click.echo(f"Terminacao 0: k={k}/{len(df)} p_hat={comp['p_hat']:.4f} p_teorica={comp['p_teorica']:.4f} p_value={comp['p_value']:.4f} -> {comp['conclusao']}")

@cli.command()
@click.option("--strategy", default="random", help="random,frequency,recency,distribution,combined")
@click.option("--iterations", default=10000, type=int)
@click.option("--seed", default=42, type=int)
@click.option("--db", default=None)
def simulate(strategy, iterations, seed, db):
    from federal_lab.simulation import MonteCarloSimulator
    from federal_lab.strategies import get_strategy
    cfg = get_settings()
    db_path = db if db else cfg.get_db_path_or_url()
    repo = Repository(db_path)
    df = repo.get_dataframe()
    sim = MonteCarloSimulator(seed=seed)
    strat = get_strategy(strategy, seed=seed)
    res = sim.simular_estrategia(strat, n_concursos=iterations, df_history=df if not df.empty else None, seed=seed)
    click.echo(f"Estratégia {strategy}: ROI {res['roi']:.4f} taxa acerto {res['taxa_acerto']:.5f} lucro {res['lucro']:.2f}")
    click.echo("AVISO: ROI simulado com prêmio fictício R$50000. Probabilidade por bilhete 1/100000 (0,001%) fixa. Histórico não altera sorteio. Não prometer lucro.")

@cli.command()
@click.option("--strategies", default="random,frequency,recency,distribution,combined")
@click.option("--db", default=None)
def backtest(strategies, db):
    from federal_lab.simulation import Backtester, Benchmark
    from federal_lab.strategies import get_strategy
    cfg = get_settings()
    db_path = db if db else cfg.get_db_path_or_url()
    repo = Repository(db_path)
    df = repo.get_dataframe()
    if df.empty or df["concurso"].nunique() < 25:
        click.echo("Dados insuficientes para backtest (precisa >=25 concursos).")
        raise SystemExit(1)
    bt = Backtester()
    resultados = {}
    for name in strategies.split(","):
        name=name.strip()
        strat = get_strategy(name)
        resultados[name] = bt.run(df, strat)
        click.echo(f"{name}: {len(resultados[name])} testes, ROI total {((resultados[name]['retorno'].sum()-resultados[name]['custo'].sum())/resultados[name]['custo'].sum()):.4f}" if not resultados[name].empty else f"{name}: vazio")
    bench = Benchmark()
    tbl = bench.compare_backtests(resultados)
    if not tbl.empty:
        click.echo("\nBenchmark:\n"+tbl.to_string(index=False))
    click.echo("AVISO: Backtest não garante futuro. Cada bilhete 1/100000. Nenhum padrão sem p<0.05 BH + out-of-sample é vantagem. ROI esperado ≈ -1.")

@cli.command()
@click.option("--strategies", default="random,frequency,recency,distribution,combined")
@click.option("--db", default=None)
def compare(strategies, db):
    from federal_lab.simulation import Backtester, Benchmark
    from federal_lab.strategies import get_strategy
    cfg = get_settings()
    db_path = db if db else cfg.get_db_path_or_url()
    repo = Repository(db_path)
    df = repo.get_dataframe()
    bt = Backtester()
    resultados = {}
    for name in strategies.split(","):
        name=name.strip()
        strat = get_strategy(name)
        resultados[name] = bt.run(df, strat)
    bench = Benchmark()
    tbl = bench.compare_backtests(resultados)
    click.echo(tbl.to_string(index=False) if not tbl.empty else "Sem dados")
    if "random" in resultados and len(resultados)>1:
        for name, res in resultados.items():
            if name=="random":
                continue
            sig = bench.significancia_vs_baseline(res, resultados["random"])
            click.echo(f"\n{name} vs random: p_t={sig['teste_t_p']:.4f} -> {sig['conclusao']}")

@cli.command()
@click.option("--db", default=None)
@click.option("--iterations", default=10000, type=int)
@click.option("--seed", default=42, type=int)
def report(db, iterations, seed):
    """Gera relatório Markdown + gráficos (§17)."""
    from federal_lab.statistics import FrequencyAnalyzer, DistributionAnalyzer, SignificanceTester
    from federal_lab.statistics.correlations import CorrelationAnalyzer
    from federal_lab.probability import TheoreticalProbability, ProbabilityComparison
    from federal_lab.reports import ReportGenerator, ChartGenerator
    from federal_lab.simulation import Backtester, Benchmark
    from federal_lab.simulation.overfitting import OverfittingDetector
    from federal_lab.strategies import get_strategy
    cfg = get_settings()
    db_path = db if db else cfg.get_db_path_or_url()
    repo = Repository(db_path)
    df = repo.get_dataframe()
    if df.empty:
        click.echo("Sem dados para relatório.")
        raise SystemExit(1)

    fa = FrequencyAnalyzer(df)
    da = DistributionAnalyzer(df)
    ca = CorrelationAnalyzer(df)
    freq = fa.freq_algarismos()

    # testes
    chi = SignificanceTester.chi_square_uniform(freq["observado"].tolist())
    runs = SignificanceTester.runs_test(df["numero"].astype(int).tolist())
    auto = SignificanceTester.autocorrelacao_lag1(df["numero"].astype(int).tolist())
    correl = ca.correlacao_soma_concurso()

    # gaps — dígito 7
    from federal_lab.statistics.significance import SignificanceTester as ST
    sorted_df = df.sort_values("concurso")
    ocorrencias = sorted_df[sorted_df["numero"].str.contains("7")]["concurso"].tolist()
    gaps = [ocorrencias[i]-ocorrencias[i-1] for i in range(1,len(ocorrencias))] if len(ocorrencias)>1 else []
    gap_test = ST.atraso_geometrico_test(gaps) if gaps else {"p_value": None, "p_hat": 0}
    n_gaps = len(gaps)
    p_hat_gap = gap_test.get("p_hat") or (1/np.mean(gaps) if gaps else 0)

    # probabilidade terminação 0
    k_term0 = int((df["numero"].str[-1]=="0").sum())
    comp_term0 = ProbabilityComparison.comparar_proporcao(k_term0, len(df), TheoreticalProbability.prob_terminacao(1))
    soma_stats = da.soma_digitos_stats()

    # correção múltipla exemplo: chi2, runs, auto, correl
    p_vals = [chi["p_value"], runs.get("p_value") or 1, auto.get("p_value") or 1, correl["p_value"]]
    p_bonf = ST.corrigir_multiplos(p_vals, "bonferroni")
    p_bh = ST.corrigir_multiplos(p_vals, "bh")

    # backtest todas estratégias
    bt = Backtester()
    resultados = {}
    for name in ["random","frequency","recency","distribution","combined"]:
        try:
            strat = get_strategy(name, seed=seed)
            resultados[name] = bt.run(df, strat)
        except Exception:
            resultados[name] = pd.DataFrame()
    bench = Benchmark()
    bench_tbl = bench.compare_backtests(resultados)

    if "random" in resultados and not bench_tbl.empty:
        melhor = bench_tbl.iloc[0]["estrategia"]
        if melhor != "random" and not resultados[melhor].empty and not resultados["random"].empty:
            sig = bench.significancia_vs_baseline(resultados[melhor], resultados["random"])
            sig_tbl = f"- Melhor: {melhor} vs random: p={sig['teste_t_p']:.4f} — {sig['conclusao']}"
        else:
            sig_tbl = "- Sem diferença significativa (todas ROI idênticos ou p>=0.05)."
    else:
        sig_tbl = "- Backtest insuficiente."

    # overfitting
    od = OverfittingDetector()
    over = od.avaliar(df, get_strategy("frequency", seed=seed))
    wf = od.walk_forward_diagnostico(df, get_strategy("frequency", seed=seed))

    # ML stub
    try:
        from federal_lab.ml import MLEvaluator
        ml = MLEvaluator(seed=seed).avaliar(df)
        ml_status = "executado" if "acc_model" in ml else "não executado"
        ml_detalhe = str({k:v for k,v in ml.items() if k not in ["aviso"]})
        ml_conclusao = ml.get("conclusao", ml.get("erro","—"))
    except Exception as e:
        ml_status = f"erro: {e}"
        ml_detalhe = "—"
        ml_conclusao = "ML não avaliado (ver §15: só após estatística clássica)."

    # charts completos §16
    cg = ChartGenerator(out_dir=Path("reports"))
    try:
        cg.frequencia_algarismos(freq)
        cg.frequencia_por_posicao(df)
        cg.distribuicao_finais(df, n=1, top=15)
        cg.distribuicao_finais(df, n=2, top=15)
        cg.distribuicao_soma(df)
        cg.distribuicao_numeros(df)
        if gaps:
            cg.intervalos_gaps(gaps)
        if not bench_tbl.empty:
            cg.roi_comparado(bench_tbl)
            # roi acumulado da random
            if not resultados["random"].empty:
                cg.roi_acumulado(resultados["random"])
        cg.ic_proporcao(k_term0, len(df), TheoreticalProbability.prob_terminacao(1))
    except Exception as e:
        click.echo(f"Aviso gráfico: {e}")

    meta = repo.get_metadata() or {}
    # conclusão regra de ouro §22
    if not bench_tbl.empty:
        significativa = False
        for name, res in resultados.items():
            if name=="random" or res.empty or resultados["random"].empty:
                continue
            p = bench.significancia_vs_baseline(res, resultados["random"])["teste_t_p"]
            if p is not None and p < 0.05:
                significativa = True
        conclusao = "NÃO foi encontrada evidência estatística suficiente para vantagem sobre aleatório (fora da amostra, com correção múltipla)." if not significativa else "Há sinal de diferença (p<0.05), mas exige validação out-of-sample, correção múltipla e walk-forward antes de qualquer conclusão — não promover como garantia."
    else:
        conclusao = "Dados insuficientes para conclusão."

    # métricas adicionais
    tbl_metricas = bench_tbl[["estrategia","n_testes","media_roi","roi_total","taxa_acerto"]].to_markdown(index=False) if not bench_tbl.empty and hasattr(bench_tbl,"to_markdown") else "—"

    ctx = {
        "aviso": "Se o processo de sorteio for independente e aleatório, o histórico NÃO altera a probabilidade do próximo sorteio.",
        "data": pd.Timestamp.now().strftime("%Y-%m-%d %H:%M"),
        "n_concursos": int(df["concurso"].nunique()),
        "n_linhas": len(df),
        "periodo": f"{df['data'].min().date()} a {df['data'].max().date()}" if "data" in df else "—",
        "fonte": meta.get("fonte","local"),
        "hash_dados": meta.get("hash_dados","—")[:16],
        "tipo": df["tipo_extracao"].mode().iloc[0] if "tipo_extracao" in df and not df.empty else "—",
        "tbl_freq": freq.to_markdown(index=False),
        "tbl_freq_pos": "Ver heatmap reports/freq_posicao.png (esperado 0.10 por célula)",
        "tbl_term1": fa.freq_terminacoes(1).head(5).to_markdown(index=False),
        "tbl_faixa": da.por_faixa(bins=5).to_markdown(index=False),
        "tbl_paridade": da.paridade().to_markdown(index=False),
        "soma_media": float(soma_stats["media"]),
        "soma_mediana": float(soma_stats["mediana"]),
        "soma_desvio": float(soma_stats["desvio"]),
        "chi2": chi["chi2"],
        "p_chi2": chi["p_value"],
        "interp_chi2": "Não rejeita uniformidade (compatível com aleatório)" if chi["p_value"]>=0.05 else "Rejeita uniformidade (investigar viés ou amostra pequena)",
        "p_runs": runs.get("p_value") or 0,
        "interp_runs": "Aleatório" if (runs.get("p_value") or 1) >=0.05 else "Desvio de aleatoriedade",
        "r_auto": auto.get("r") or 0,
        "p_auto": auto.get("p_value") or 0,
        "interp_auto": "Sem autocorrelação" if (auto.get("p_value") or 1) >=0.05 else "Autocorrelação detectada",
        "r_correl": correl["r"],
        "p_correl": correl["p_value"],
        "p_hat_term0": comp_term0["p_hat"],
        "p_binom": comp_term0["p_value"],
        "interp_term0": comp_term0["conclusao"],
        "n_gaps": n_gaps,
        "p_hat_gap": float(p_hat_gap),
        "p_gap": gap_test.get("p_value") or 0,
        "interp_gap": "Compatível com processo aleatório" if (gap_test.get("p_value") or 1) >=0.05 else "Desvio de geométrico",
        "conclusao_gap": "Gaps compatíveis com aleatoriedade — atraso NÃO implica maior probabilidade futura." if (gap_test.get("p_value") or 1) >=0.05 else "Sinal fraco — exige out-of-sample.",
        "mc_iter": iterations,
        "estrategias_mc": "random, frequency, recency, distribution, combined",
        "seed": seed,
        "tbl_bench": bench_tbl.to_markdown(index=False) if not bench_tbl.empty else "Backtest insuficiente",
        "tbl_signif": sig_tbl,
        "tbl_metricas": tbl_metricas,
        "p_vals_orig": [f"{p:.4f}" for p in p_vals],
        "p_vals_bonf": [f"{p:.4f}" for p in p_bonf],
        "p_vals_bh": [f"{p:.4f}" for p in p_bh],
        "split_roi": str(over["splits"]),
        "overfit": over["overfit_suspeito"],
        "interp_overfit": over["interpretacao"],
        "wf_media": wf.get("media", 0),
        "wf_desvio": wf.get("desvio", 0),
        "wf_pct": wf.get("pct_janelas_positivas", 0),
        "interp_wf": wf.get("interpretacao","—"),
        "ml_status": ml_status,
        "ml_detalhe": ml_detalhe[:600],
        "ml_conclusao": ml_conclusao,
        "pesos": str(get_settings().scoring_weights),
        "conclusao_final": conclusao,
    }
    # compat: scoring_weights pode não existir no Settings antigo → fallback
    if "pesos" not in ctx or ctx["pesos"]=="—":
        ctx["pesos"] = "{'frequencia':0.25,'distribuicao':0.25,'recencia':0.25,'caracteristicas':0.25,'penalidade_complexidade':0.1}"
    gen = ReportGenerator(out_path=Path("reports/relatorio.md"))
    out = gen.generate(ctx)
    click.echo(f"✓ Relatório gerado em {out}")
    click.echo(f"  Gráficos em {cg.out_dir}/ ({len(list(cg.out_dir.glob('*.png')))} PNGs)")

@cli.command()
@click.option("--estrategia", default="random", help="random,frequency,recency,distribution,combined")
@click.option("--n", default=5, type=int, help="Qtd jogos 1..10")
@click.option("--seed", default=42, type=int)
@click.option("--aceite", is_flag=True, help="Aceite: entendo que é experimental, 0,001% fixo, ROI -1")
@click.option("--db", default=None)
def gerar(estrategia, n, seed, aceite, db):
    """Gera jogos com atrito e disclaimer obrigatório (18+)."""
    if not aceite:
        click.echo("ERRO: Use --aceite para confirmar que entende: cada bilhete 1/100000 (0,001%) fixo, ranking experimental NÃO é probabilidade, ROI esperado -1, sem promessa de lucro. Ex: federal gerar --estrategia random --n 5 --aceite")
        raise SystemExit(1)
    if not 1 <= n <= 10:
        click.echo("n deve ser 1..10")
        raise SystemExit(1)
    from federal_lab.strategies import get_strategy
    from federal_lab.probability.theoretical import TheoreticalProbability
    cfg = get_settings()
    repo = Repository(db if db else cfg.get_db_path_or_url())
    df = repo.get_dataframe()
    meta = repo.get_metadata() or {}
    strat = get_strategy(estrategia, seed=seed)
    jogos = strat.select(df if not df.empty else __import__("pandas").DataFrame(), n=n)
    prob = TheoreticalProbability.prob_numero_especifico()
    custo = n * cfg.cost_per_bet
    click.echo(f"Jogos ({estrategia}, seed {seed}): {', '.join(jogos)}")
    click.echo(f"Prob teórica por bilhete: 1/100000 (0,001%) | Custo estimado: R$ {custo:.2f} | Perda esperada ≈ R$ {custo:.2f}")
    click.echo(f"Hash dados: {(meta.get('hash_dados') or '—')[:12]} | Período: {df['data'].min().date() if not df.empty and 'data' in df else '—'}")
    click.echo("AVISO: Ranking EXPERIMENTAL, não probabilidade real. Histórico não altera sorteio se aleatório. 18+ Jogue com responsabilidade. CVV 188.")
    # vs random se houver dados
    if not df.empty and df["concurso"].nunique() >= 25:
        from federal_lab.simulation import Backtester, Benchmark
        bt = Backtester(); bench = Benchmark()
        r1 = bt.run(df, strat); r2 = bt.run(df, get_strategy("random", seed=seed))
        vs = bench.significancia_vs_baseline(r1, r2)
        click.echo(f"vs random: p={vs['teste_t_p']:.4f} → {vs['conclusao']}")

@cli.command()
@click.option("--host", default="127.0.0.1", help="Host")
@click.option("--port", default=8000, type=int, help="Porta")
@click.option("--reload", is_flag=True, help="Reload para dev")
def web(host, port, reload):
    """Inicia interface web (FastAPI). Acesse http://127.0.0.1:8000"""
    try:
        from federal_lab.web.app import run
    except ImportError as e:
        click.echo(f"Dependências web faltando: {e}. Instale com pip install fastapi uvicorn jinja2 python-multipart")
        raise SystemExit(1)
    click.echo(f"→ Iniciando Federal Lab web em http://{host}:{port} (docs em http://{host}:{port}/docs)")
    run(host=host, port=port, reload=reload)

if __name__ == "__main__":
    cli()
