.PHONY: install test analyze report simulate backtest compare ml web clean

install:
	pip install -e ".[dev,ml]"

test:
	pytest -q --tb=short

analyze:
	federal analyze

report:
	federal report --iterations 1000 --seed 42

simulate:
	federal simulate --strategy random --iterations 10000 --seed 42

backtest:
	federal backtest --strategies random,frequency,recency,distribution,combined

compare:
	federal compare --strategies random,frequency,recency,distribution,combined

ml:
	python -c "from federal_lab.ml import MLEvaluator; from federal_lab.data import Repository; print(MLEvaluator().avaliar(Repository('data/database/federal.db').get_dataframe()))"

fetch-exemplo:
	federal fetch --file data/raw/federal_exemplo.csv

fetch-escala:
	federal fetch --file data/raw/federal_escala.csv

web:
	federal web --port 8000

web-streamlit:
	streamlit run src/federal_lab/web/streamlit_app.py

clean:
	find . -type d -name "__pycache__" -exec rm -rf {} +; find . -type d -name ".pytest_cache" -exec rm -rf {} +; rm -rf src/*.egg-info .coverage
