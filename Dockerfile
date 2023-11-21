FROM python:3.11-slim-buster

RUN USER=root pip install poetry
RUN apt-get update
RUN apt-get install
RUN apt-get install

COPY ./pyproject.toml ./pyproject.toml
COPY ./src ./src
COPY ./config.ini ./config.ini

RUN poetry config virtualenvs.create false
RUN poetry install

CMD ["poetry", "run", "python", "-m", "src"]