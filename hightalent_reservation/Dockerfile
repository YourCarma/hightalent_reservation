FROM python:3.12-slim

USER root

WORKDIR /hightalent_reservation
COPY pyproject.toml poetry.lock ./
RUN python3 -m pip install poetry 
RUN poetry config virtualenvs.create false
RUN poetry install --no-root --without dev

RUN apt install curl -y

COPY . .
RUN sed -i 's/\r$//' startup.sh

ENTRYPOINT [ "/bin/sh", "./startup.sh" ]
EXPOSE 8001
