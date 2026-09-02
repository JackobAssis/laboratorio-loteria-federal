# PROMPT — LABORATÓRIO ESTATÍSTICO DA LOTERIA FEDERAL

Você é responsável por projetar e implementar um projeto Python de análise estatística da **Loteria Federal brasileira**.

O objetivo NÃO é prometer ou afirmar que determinados números possuem maior chance real de serem sorteados.

O objetivo é construir uma plataforma experimental capaz de:

1. coletar e armazenar resultados históricos;
2. realizar análises estatísticas;
3. calcular probabilidades teóricas;
4. identificar padrões aparentes;
5. testar se esses padrões são estatisticamente significativos;
6. comparar estratégias de seleção contra uma estratégia aleatória;
7. realizar simulações Monte Carlo;
8. criar um sistema de pontuação/ranking experimental;
9. medir o desempenho histórico das estratégias;
10. identificar overfitting e vieses estatísticos;
11. gerar relatórios claros sobre os resultados.

A regra principal do projeto é:

> NENHUM PADRÃO HISTÓRICO DEVE SER CONSIDERADO UMA VANTAGEM REAL SEM TESTE ESTATÍSTICO QUE DEMONSTRE SIGNIFICÂNCIA.

---

# 1. PRINCÍPIOS DO PROJETO

Siga rigorosamente estes princípios:

* Separar probabilidade teórica de frequência observada.
* Nunca tratar frequência histórica como garantia de ocorrência futura.
* Não utilizar a falácia do jogador.
* Não assumir que um número "atrasado" está mais propenso a sair.
* Não assumir que um número "quente" continuará sendo frequente.
* Diferenciar correlação de causalidade.
* Testar hipóteses contra modelos aleatórios.
* Utilizar intervalos de confiança quando apropriado.
* Utilizar testes de significância estatística.
* Corrigir problemas de múltiplos testes quando necessário.
* Evitar overfitting.
* Separar dados de treinamento e teste quando houver modelos preditivos.
* Fazer backtesting temporal.
* Registrar todas as hipóteses testadas.
* Tornar todos os cálculos reproduzíveis.
* Utilizar sementes aleatórias configuráveis nas simulações.
* Nunca apresentar uma estratégia experimental como garantia de lucro.

O sistema deve deixar explícito que:

> Se o processo de sorteio for independente e aleatório, o histórico não altera a probabilidade matemática básica do próximo sorteio.

---

# 2. ARQUITETURA

Crie uma arquitetura modular semelhante a:

federal_lab/
│
├── README.md
├── pyproject.toml
├── .gitignore
├── .env.example
│
├── data/
│   ├── raw/
│   ├── processed/
│   └── database/
│
├── src/
│   └── federal_lab/
│       │
│       ├── config/
│       │
│       ├── data/
│       │   ├── collector.py
│       │   ├── parser.py
│       │   ├── validator.py
│       │   └── repository.py
│       │
│       ├── statistics/
│       │   ├── frequency.py
│       │   ├── distribution.py
│       │   ├── independence.py
│       │   ├── significance.py
│       │   ├── confidence.py
│       │   └── correlations.py
│       │
│       ├── probability/
│       │   ├── theoretical.py
│       │   ├── empirical.py
│       │   └── comparisons.py
│       │
│       ├── features/
│       │   ├── digits.py
│       │   ├── endings.py
│       │   ├── ranges.py
│       │   ├── parity.py
│       │   ├── sums.py
│       │   └── repetitions.py
│       │
│       ├── strategies/
│       │   ├── random_strategy.py
│       │   ├── frequency_strategy.py
│       │   ├── recency_strategy.py
│       │   ├── distribution_strategy.py
│       │   └── combined_strategy.py
│       │
│       ├── simulation/
│       │   ├── monte_carlo.py
│       │   ├── backtest.py
│       │   └── benchmark.py
│       │
│       ├── ranking/
│       │   ├── scoring.py
│       │   └── ranking.py
│       │
│       ├── reports/
│       │   ├── generator.py
│       │   └── charts.py
│       │
│       └── cli/
│           └── main.py
│
├── tests/
│
├── notebooks/
│
└── reports/

Adapte a estrutura se identificar uma arquitetura melhor, mas preserve a separação entre:

DATA → FEATURES → ESTATÍSTICA → PROBABILIDADE → ESTRATÉGIAS → SIMULAÇÃO → BACKTEST → RELATÓRIO.

---

# 3. BANCO DE DADOS

Utilize inicialmente SQLite para facilitar execução local.

Crie tabelas adequadas para:

* concursos;
* datas;
* tipo de extração;
* números sorteados;
* posições dos prêmios;
* metadados;
* resultados processados;
* resultados das análises;
* simulações;
* estratégias;
* backtests.

O banco deve permitir posteriormente migração para PostgreSQL.

Não duplicar dados.

Criar validações para detectar:

* concursos duplicados;
* números inválidos;
* datas inconsistentes;
* resultados incompletos;
* alterações nos dados históricos.

---

# 4. COLETA DE DADOS

Crie uma camada de coleta desacoplada da análise.

A fonte oficial deve ser priorizada.

Não faça scraping frágil diretamente dentro dos módulos estatísticos.

Criar interface semelhante a:

DataSource
├── OfficialSource
└── LocalFileSource

O sistema deve conseguir trabalhar tanto com:

* dados obtidos da fonte oficial;
* CSV/JSON local;
* banco SQLite.

Registrar:

* data da coleta;
* fonte;
* quantidade de registros;
* hash ou mecanismo equivalente para detectar alteração dos dados.

---

# 5. ANÁLISE DESCRITIVA

Implementar análises para:

## Algarismos

Calcular:

* frequência de 0–9;
* frequência por posição;
* frequência do primeiro algarismo;
* frequência do último algarismo;
* frequência de pares;
* frequência de trincas;
* frequência de sequências.

## Terminações

Analisar:

* finais de 1 dígito;
* finais de 2 dígitos;
* finais de 3 dígitos;
* finais de 4 dígitos.

## Distribuição

Analisar:

* números por faixa;
* distribuição dos dígitos;
* soma dos dígitos;
* quantidade de números pares;
* quantidade de números ímpares;
* repetição de algarismos;
* números com dígitos iguais;
* sequências consecutivas.

---

# 6. NÚMERO "ATRASADO"

Criar uma análise específica para demonstrar matematicamente a diferença entre:

* frequência;
* tempo desde a última ocorrência;
* probabilidade futura.

O sistema deve calcular o intervalo desde a última ocorrência.

Porém:

NUNCA transformar automaticamente "atraso" em aumento de probabilidade.

Criar um experimento:

H0:
O intervalo entre ocorrências é compatível com um processo aleatório.

H1:
Existe evidência estatística de comportamento diferente.

Executar testes apropriados e apresentar:

* estatística;
* p-value;
* intervalo de confiança;
* interpretação;
* tamanho da amostra.

---

# 7. TESTE DE ALEATORIEDADE

Criar módulo para verificar se as distribuições observadas são compatíveis com aleatoriedade.

Considerar testes apropriados, como:

* Chi-square;
* teste de independência;
* runs test;
* autocorrelação;
* testes de distribuição;
* permutation tests;
* bootstrap.

Não aplicar testes indiscriminadamente.

Cada teste deve possuir:

* hipótese nula;
* hipótese alternativa;
* justificativa;
* limitações;
* interpretação.

---

# 8. PROBABILIDADE

Separar claramente:

PROBABILIDADE TEÓRICA

versus

PROBABILIDADE EMPÍRICA.

Exemplo:

Se determinada característica ocorreu 12% dos concursos, isso NÃO significa automaticamente que a próxima ocorrência terá probabilidade de 12%.

Calcular intervalos de confiança para proporções observadas.

Quando apropriado, utilizar modelos binomiais.

---

# 9. SIMULAÇÃO MONTE CARLO

Criar um mecanismo capaz de simular milhões de concursos.

Permitir configurar:

* número de simulações;
* quantidade de concursos;
* quantidade de números;
* seed;
* estratégia;
* bankroll;
* custo por aposta.

Criar benchmark:

Estratégia A:
Seleção completamente aleatória.

Estratégia B:
Seleção baseada em frequência histórica.

Estratégia C:
Seleção baseada em recência.

Estratégia D:
Seleção baseada em distribuição estatística.

Estratégia E:
Modelo combinado.

Comparar todas contra o baseline aleatório.

---

# 10. BACKTEST

Criar backtesting temporal.

IMPORTANTE:

Nunca utilizar informações futuras para selecionar apostas em um concurso passado.

Exemplo:

Para testar o concurso N:

dados disponíveis = concursos anteriores a N.

A estratégia é calculada.

Depois o resultado real do concurso N é revelado.

Registrar:

* estratégia;
* seleção;
* resultado;
* acertos;
* prêmio;
* custo;
* retorno;
* ROI;
* drawdown;
* quantidade de apostas.

Repetir para todo o período disponível.

---

# 11. DETECÇÃO DE OVERFITTING

Criar mecanismos para detectar quando uma estratégia parece funcionar apenas porque foi ajustada ao histórico.

Implementar:

* treino;
* validação;
* teste;
* walk-forward validation;
* out-of-sample testing.

Uma estratégia não deve ser considerada promissora apenas porque possui bom desempenho no histórico utilizado para construí-la.

---

# 12. SISTEMA DE SCORE

Criar um sistema experimental de score.

Exemplo conceitual:

score =
peso_frequencia
+ peso_distribuicao
+ peso_recencia
+ peso_caracteristicas
- penalidade_complexidade

Porém:

NÃO definir pesos arbitrários sem justificativa.

Criar configuração para pesos.

Permitir comparação entre:

* pesos manuais;
* pesos uniformes;
* pesos derivados do treinamento.

O score deve ser tratado como:

"ranking experimental"

e não:

"probabilidade real de sorteio".

---

# 13. COMPARAÇÃO COM BASELINE

Esta é uma das partes MAIS IMPORTANTES do projeto.

Toda estratégia deve ser comparada com:

1. seleção aleatória;
2. seleção uniforme;
3. estratégia ingênua;
4. estratégia histórica.

Calcular:

* média;
* mediana;
* desvio padrão;
* intervalo de confiança;
* ROI;
* taxa de acerto;
* distribuição de resultados.

Determinar se a diferença entre estratégias possui significância estatística.

Uma estratégia só deve ser considerada interessante se conseguir superar o baseline de maneira consistente e fora da amostra.

---

# 14. CONTROLE DE MÚLTIPLOS TESTES

Como o projeto testará muitas hipóteses, implementar correção para múltiplas comparações quando apropriado.

Considerar métodos como:

* Bonferroni;
* Benjamini-Hochberg / FDR.

Documentar por que determinado método foi utilizado.

Isso é obrigatório para evitar encontrar "padrões" por puro acaso.

---

# 15. MACHINE LEARNING

NÃO começar utilizando machine learning.

Primeiro construir:

1. estatística descritiva;
2. probabilidade;
3. testes de hipótese;
4. simulação;
5. backtesting.

Somente depois avaliar se ML possui justificativa.

Se for implementado:

* evitar leakage;
* separar treino/teste;
* utilizar validação temporal;
* comparar contra baseline;
* medir complexidade;
* testar estabilidade.

Se ML não superar o baseline fora da amostra, registrar isso como resultado.

---

# 16. VISUALIZAÇÕES

Criar gráficos para:

* frequência dos algarismos;
* frequência por posição;
* distribuição dos finais;
* distribuição das somas;
* intervalos entre ocorrências;
* distribuição dos números;
* desempenho das estratégias;
* ROI;
* resultados Monte Carlo;
* comparação com baseline;
* intervalo de confiança.

Os gráficos devem ser gerados automaticamente nos relatórios.

---

# 17. RELATÓRIO AUTOMÁTICO

Criar relatório Markdown contendo:

## Resumo

Quantidade de concursos analisados.

## Dados

Fonte e período.

## Estatística

Principais distribuições.

## Testes

Hipóteses testadas.

## Significância

Resultados estatísticos.

## Simulações

Quantidade de simulações.

## Estratégias

Desempenho de cada estratégia.

## Baseline

Comparação com aleatoriedade.

## Conclusão

Responder:

> Existe evidência estatística suficiente para afirmar que alguma estratégia apresenta vantagem sobre a seleção aleatória?

A resposta deve ser baseada nos dados, não em expectativa.

---

# 18. CLI

Criar uma interface CLI simples:

federal fetch

federal validate

federal analyze

federal probability

federal simulate

federal backtest

federal compare

federal report

Exemplo:

federal analyze --from 2010-01-01 --to 2026-12-31

federal simulate --strategy random --iterations 1000000

federal compare --strategies random,frequency,recency,combined

federal report

---

# 19. CONFIGURAÇÃO

Criar arquivo de configuração para:

* fonte de dados;
* banco;
* quantidade de simulações;
* seed;
* nível de significância;
* período analisado;
* estratégias;
* pesos;
* quantidade de apostas;
* bankroll.

Nunca deixar valores críticos espalhados pelo código.

---

# 20. TESTES AUTOMATIZADOS

Criar testes unitários para:

* parser;
* validação;
* cálculo de frequência;
* probabilidade;
* score;
* simulação;
* backtest;
* ROI;
* estatística.

Criar testes para casos extremos.

Garantir que:

* dados inválidos sejam rejeitados;
* resultados sejam reproduzíveis com a mesma seed;
* backtest não utilize dados futuros;
* estratégias não tenham acesso ao resultado que estão tentando prever.

---

# 21. DOCUMENTAÇÃO

Criar:

README.md

ARCHITECTURE.md

METHODOLOGY.md

STATISTICS.md

STRATEGIES.md

BACKTESTING.md

LIMITATIONS.md

EXPERIMENTS.md

Cada metodologia estatística deve ser explicada em linguagem clara.

---

# 22. REGRA DE OURO

O projeto não deve procurar apenas evidências que confirmem que uma estratégia funciona.

Ele deve procurar ativamente evidências de que a estratégia NÃO funciona.

Para cada hipótese:

1. formular H0;
2. formular H1;
3. definir teste;
4. executar;
5. medir efeito;
6. verificar significância;
7. validar fora da amostra;
8. comparar contra baseline;
9. registrar conclusão.

Se não houver evidência suficiente:

> "Não foi encontrada evidência estatística suficiente."

Essa conclusão deve ser considerada um resultado válido.

---

# 23. PRIMEIRA IMPLEMENTAÇÃO

Não tente implementar tudo de uma vez.

Execute em fases:

FASE 1
→ estrutura do projeto
→ configuração
→ banco SQLite
→ modelo de dados
→ coleta/importação
→ validação

FASE 2
→ estatística descritiva
→ frequências
→ distribuição
→ características dos números

FASE 3
→ testes estatísticos
→ probabilidade
→ intervalos de confiança
→ testes de independência

FASE 4
→ estratégias
→ baseline aleatório
→ score experimental

FASE 5
→ Monte Carlo
→ backtesting
→ comparação

FASE 6
→ controle de overfitting
→ walk-forward
→ testes fora da amostra

FASE 7
→ relatórios
→ gráficos
→ CLI
→ documentação

NÃO avance para a próxima fase enquanto a anterior não estiver funcional e testada.

---

# 24. COMPORTAMENTO DO OPENCODE

Trabalhe de forma autônoma dentro do projeto.

Antes de implementar:

1. examine os arquivos existentes;
2. identifique tecnologias já utilizadas;
3. preserve código existente;
4. não sobrescreva arquivos sem necessidade;
5. crie documentação das decisões;
6. execute testes;
7. corrija erros;
8. valide os resultados.

Quando houver uma decisão estatística relevante, documente-a.

Não invente dados.

Não invente resultados.

Não declare que existe vantagem estatística sem evidência.

Ao finalizar cada fase, apresente:

* arquivos criados;
* arquivos modificados;
* funcionalidades implementadas;
* testes executados;
* resultados;
* problemas encontrados;
* próxima etapa.

O objetivo final é construir um **laboratório científico reproduzível para estudar a Loteria Federal**, utilizando matemática, estatística, probabilidade, simulação e backtesting, e não um sistema de promessa de previsão de resultados.
