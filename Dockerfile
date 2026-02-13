FROM python:3.12-slim

WORKDIR /app

RUN apt-get update && apt-get install -y \
    gcc \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir poetry==1.7.1

COPY pyproject.toml poetry.lock* ./

RUN poetry config virtualenvs.create false \
    && poetry install --no-interaction --no-ansi --no-root

COPY . /app/
COPY scripts/ /app/scripts/
COPY src/ /app/src/
COPY data/ /app/data/

RUN chmod +x /app/scripts/*.py
RUN ls -la /app/scripts/ && ls -la /app/src/

CMD ["poetry", "run", "python", "-m", "src.bot.main"]