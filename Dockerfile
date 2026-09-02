FROM python:3.11-slim
WORKDIR /app
COPY pyproject.toml README.md ./
COPY src ./src
RUN pip install --no-cache-dir -e ".[ml]" && pip install --no-cache-dir matplotlib seaborn tabulate
COPY data ./data
COPY reports ./reports
EXPOSE 8000
CMD ["federal", "--help"]
