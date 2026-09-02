# Estratégias

- **random** (`RandomStrategy`): baseline uniforme 00000–99999. Sempre comparar contra ela.
- **frequency**: usa Counter por posição; amostra ponderada nos top frequentes (quentes). Experimental — não implica vantagem.
- **recency**: gap de terminações 2d; escolhe mais atrasadas (demonstra falácia se tratada como probabilidade). Usa gap como feature, não como garantia.
- **distribution**: amostra soma dentro de 1 desvio da média histórica (evita extremos como 00000/99999).
- **combined**: pool de 80 candidatos (20 de cada) + ranking por proximidade da média e penalidade de repetição + ruído.

Todas recebem apenas `df_history` (< concurso teste). `CombinedStrategy` aceita `pesos` configuráveis.

Nenhuma deve ser apresentada como garantia de lucro.
