# Limitações & Avisos

- Se sorteio é i.i.d. uniforme, **nenhuma estratégia histórica altera probabilidade de 1/100k** por prêmio. Laboratório é para *estudar*, não para prometer.
- Amostras pequenas (<200 concursos) têm poder baixo; p<0.05 pode ser flutuação.
- Múltiplos testes sem correção geram falsos padrões — usar Bonferroni/BH.
- Backtest in-sample superestima; exigir out-of-sample e walk-forward.
- Fonte oficial pode mudar layout/API — camada `OfficialSource` isola scraping.
- Não usar ML antes de estatística clássica; se usar, evitar leakage e comparar contra baseline.
- Custo/prêmio no simulador são ilustrativos; calibrar com edital real.
- Conclusão honesta: “Não foi encontrada evidência estatística suficiente” é resultado válido e esperado.
