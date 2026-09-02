from federal_lab.simulation.monte_carlo import MonteCarloSimulator
from federal_lab.strategies import get_strategy
from federal_lab.data.parser import Parser
from pathlib import Path

def test_monte_reprodutivel():
    sim1=MonteCarloSimulator(seed=42)
    sim2=MonteCarloSimulator(seed=42)
    df1=sim1.simular_concursos(10, seed=123)
    df2=sim2.simular_concursos(10, seed=123)
    assert df1.equals(df2)

def test_backtest_nao_usa_futuro():
    from federal_lab.simulation.backtest import Backtester
    p = Path(__file__).parents[1] / "data" / "raw" / "federal_exemplo.csv"
    df = Parser.to_dataframe(Parser.parse_csv(p))
    # verifica que estrategia não recebe futuro: criamos estrategia que checa
    class SpyStrategy:
        name="spy"
        def select(self, hist, n=5):
            # hist deve ter apenas concursos < teste
            # guarda max concurso visto
            self.last_hist_max = hist["concurso"].max() if not hist.empty else None
            return ["00000"]*n
    spy=SpyStrategy()
    # wrapper para capturar max_hist por chamada
    original_select = spy.select
    hist_maxes = []
    concursos_teste = []
    def tracking_select(hist, n=5):
        hist_maxes.append(hist["concurso"].max() if not hist.empty else 0)
        # registra próximo concurso teste esperado = max+1 ou próximo existente
        return original_select(hist, n)
    spy.select = tracking_select
    bt=Backtester()
    res=bt.run(df, spy, min_history=5)
    # cada chamada: hist_max < concurso_teste correspondente
    for max_hist, (_, row) in zip(hist_maxes, res.iterrows()):
        assert row["concurso_teste"] > max_hist, f"Backtest vazou futuro: {row['concurso_teste']} <= {max_hist}"
    assert "roi" in res.columns

def test_benchmark():
    from federal_lab.simulation import Backtester, Benchmark
    from pathlib import Path
    from federal_lab.data.parser import Parser
    p = Path(__file__).parents[1] / "data" / "raw" / "federal_exemplo.csv"
    df = Parser.to_dataframe(Parser.parse_csv(p))
    bt=Backtester()
    results={}
    for name in ["random","frequency"]:
        strat=get_strategy(name, seed=42)
        results[name]=bt.run(df, strat, min_history=10)
    bench=Benchmark()
    tbl=bench.compare_backtests(results)
    assert not tbl.empty
    assert "roi_total" in tbl.columns
