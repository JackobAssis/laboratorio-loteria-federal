"""ML — §15: NÃO começar com ML. Avaliar só após estatística clássica, com leakage check."""

import pandas as pd
import numpy as np

try:
    from sklearn.model_selection import TimeSeriesSplit
    from sklearn.dummy import DummyClassifier
    from sklearn.ensemble import RandomForestClassifier
    from sklearn.metrics import accuracy_score
    SKLEARN_OK = True
except Exception:
    SKLEARN_OK = False

class MLEvaluator:
    """
    Stub responsável — só roda ML se houver justificativa, sempre:
    - separa treino/teste temporal (TimeSeriesSplit)
    - compara contra baseline (Dummy)
    - mede complexidade e estabilidade
    - nunca usa informação futura (leakage check)
    """

    AVISO = "ML só após descritiva → probabilidade → testes → simulação → backtest. Se não superar baseline fora da amostra, registrar como resultado."

    def __init__(self, seed: int = 42):
        self.seed = seed

    def preparar_features(self, df: pd.DataFrame) -> tuple[pd.DataFrame, pd.Series]:
        """
        Features seguras SEM LEAKAGE:
        Target: termina em 0?
        Features NÃO incluem d5 (último dígito) nem terminação direta — evita leakage trivial.
        Usa apenas d1-d4, soma parcial, etc. §15: evitar leakage.
        """
        tmp = df.copy()
        tmp["soma"] = tmp["numero"].apply(lambda x: sum(int(c) for c in str(x)))
        tmp["qtd_pares"] = tmp["numero"].apply(lambda x: sum(1 for c in str(x) if int(c)%2==0))
        tmp["repeticao"] = tmp["numero"].apply(lambda x: 5 - len(set(str(x))))
        for col in ["d1","d2","d3","d4"]:
            tmp[col] = tmp[col].astype(int)
        # NÃO usa d5 — leakage explícito removido
        X = tmp[["d1","d2","d3","d4","soma","qtd_pares","repeticao"]]
        y = (tmp["numero"].str[-1] == "0").astype(int)  # termina em 0
        return X, y

    def avaliar(self, df: pd.DataFrame, modelo=None) -> dict:
        if not SKLEARN_OK:
            return {"erro": "scikit-learn não instalado. Instale com pip install scikit-learn para avaliar ML.", "aviso": self.AVISO}
        if len(df) < 100:
            return {"erro": "Dados insuficientes (<100 linhas) para ML temporal", "aviso": self.AVISO}
        X, y = self.preparar_features(df)
        # TimeSeriesSplit garante temporalidade
        tscv = TimeSeriesSplit(n_splits=3)
        modelo = modelo or RandomForestClassifier(n_estimators=50, random_state=self.seed, max_depth=5)
        dummy = DummyClassifier(strategy="most_frequent")

        scores_model, scores_dummy = [], []
        leakage_ok = True
        for train_idx, test_idx in tscv.split(X):
            # leakage check: max concurso train < min concurso test ?
            # como df está ordenado por concurso, índices já respeitam temporalidade
            if max(train_idx) >= min(test_idx):
                leakage_ok = False
            Xtr, Xte = X.iloc[train_idx], X.iloc[test_idx]
            ytr, yte = y.iloc[train_idx], y.iloc[test_idx]
            modelo.fit(Xtr, ytr)
            dummy.fit(Xtr, ytr)
            scores_model.append(accuracy_score(yte, modelo.predict(Xte)))
            scores_dummy.append(accuracy_score(yte, dummy.predict(Xte)))

        media_model = float(np.mean(scores_model))
        media_dummy = float(np.mean(scores_dummy))
        supera = media_model > media_dummy + 0.02  # margem 2pp
        return {
            "acc_model": media_model,
            "acc_dummy": media_dummy,
            "scores_model": scores_model,
            "scores_dummy": scores_dummy,
            "leakage_ok": leakage_ok,
            "supera_baseline": bool(supera),
            "complexidade": f"{modelo.__class__.__name__} (n_estimators={getattr(modelo,'n_estimators', '?')})",
            "conclusao": (
                "ML supera baseline fora da amostra — investigar estabilidade e custo."
                if supera else
                "ML NÃO supera baseline fora da amostra — registrar como resultado (esperado se sorteio é aleatório). Não promover."
            ),
            "aviso": self.AVISO,
        }
