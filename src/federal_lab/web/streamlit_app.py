"""Streamlit alternativo — `streamlit run src/federal_lab/web/streamlit_app.py`"""

import streamlit as st
import pandas as pd
from pathlib import Path

st.set_page_config(page_title="Federal Lab", layout="wide", page_icon="🎲")

st.title("Laboratório Estatístico da Loteria Federal")
st.caption("Se o processo for aleatório, histórico NÃO altera probabilidade do próximo sorteio. Nenhum padrão sem significância out-of-sample é vantagem real.")

try:
    from federal_lab.data import Repository
    from federal_lab.statistics import FrequencyAnalyzer, DistributionAnalyzer, SignificanceTester
    from federal_lab.simulation import Backtester, Benchmark
    from federal_lab.strategies import get_strategy
    from federal_lab.config import get_settings
    repo = Repository(get_settings().db_absolute())
    df = repo.get_dataframe()
except Exception as e:
    st.error(f"Erro carregando dados: {e}")
    st.stop()

if df.empty:
    st.warning("Sem dados. Rode `federal fetch --file data/raw/federal_exemplo.csv`")
    st.stop()

tab1, tab2, tab3, tab4, tab5 = st.tabs(["📊 Estatística", "🔬 Testes", "🎲 Simulação", "📈 Backtest", "📄 Relatório"])

with tab1:
    fa = FrequencyAnalyzer(df)
    st.subheader(f"Concursos: {df['concurso'].nunique()} | Linhas: {len(df)}")
    c1,c2 = st.columns(2)
    with c1:
        st.dataframe(fa.freq_algarismos(), use_container_width=True)
        st.bar_chart(fa.freq_algarismos().set_index("algarismo")["frequencia"])
    with c2:
        da = DistributionAnalyzer(df)
        st.dataframe(da.paridade(), use_container_width=True)
        st.write(da.soma_digitos_stats())

with tab2:
    chi = SignificanceTester.chi_square_uniform(FrequencyAnalyzer(df).freq_algarismos()["observado"].tolist())
    st.metric("Chi2 uniformidade p", f"{chi['p_value']:.4f}", delta="compatível" if chi["p_value"]>=0.05 else "rejeita", delta_color="off")
    st.json(chi)

with tab3:
    strat = st.selectbox("Estratégia", ["random","frequency","recency","distribution","combined"])
    it = st.slider("Iterações", 100, 5000, 1000)
    if st.button("Simular"):
        from federal_lab.simulation import MonteCarloSimulator
        sim = MonteCarloSimulator(seed=42)
        res = sim.simular_estrategia(get_strategy(strat, seed=42), n_concursos=it, df_history=df, seed=42)
        st.json(res)

with tab4:
    if st.button("Rodar backtest"):
        bt = Backtester()
        res = {name: bt.run(df, get_strategy(name, seed=42)) for name in ["random","frequency","recency","distribution","combined"]}
        bench = Benchmark().compare_backtests(res)
        st.dataframe(bench, use_container_width=True)

with tab5:
    p = Path("reports/relatorio.md")
    if p.exists():
        st.markdown(p.read_text(encoding="utf-8"))
    else:
        st.info("Rode `federal report`")
