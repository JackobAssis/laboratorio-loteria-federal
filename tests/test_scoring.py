from federal_lab.ranking.scoring import Scorer

def test_score():
    sc=Scorer()
    stats={"freq": {"1":0.5}, "media_soma":22, "desvio_soma":7, "gaps": {"00":10,"12":5}, "freq_global": {}}
    s=sc.score_numero("01234", {"freq": {"0":0.2,"1":0.2,"2":0.2,"3":0.2,"4":0.2}, "media_soma":10,"desvio_soma":5,"gaps":{"34":5}})
    assert isinstance(s,float)
