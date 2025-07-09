FROM python:3.11-slim

WORKDIR /app

RUN pip install poetry==2.1.3

COPY pyproject.toml poetry.lock ./
COPY README.md .
COPY urlevaluator ./urlevaluator

RUN poetry config virtualenvs.create false && poetry install --no-interaction --no-ansi

ARG DB_NAME
ARG MODEL_NAME

ENV DB_NAME=${DB_NAME}
ENV MODEL_NAME=${MODEL_NAME}

RUN poetry run poe init-db
RUN poetry run poe download-model

CMD ["/bin/bash"]
