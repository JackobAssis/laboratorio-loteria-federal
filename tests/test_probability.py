from federal_lab.probability.theoretical import TheoreticalProbability
from federal_lab.probability.comparisons import ProbabilityComparison

def test_teorica():
    assert TheoreticalProbability.prob_numero_especifico() == 1/100000
    assert abs(TheoreticalProbability.prob_terminacao(1)-0.1) < 1e-9
    assert abs(TheoreticalProbability.prob_terminacao(2)-0.01) < 1e-9
    assert abs(sum(TheoreticalProbability.prob_qtd_pares(k) for k in range(6))-1) < 1e-9
    assert abs(TheoreticalProbability.prob_todos_iguais() - 0.0001) < 1e-9

def test_comparacao():
    comp = ProbabilityComparison.comparar_proporcao(10, 100, 0.1)
    assert "p_value" in comp
    assert comp["p_hat"] == 0.1
