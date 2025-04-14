FROM python:3.12 AS build

WORKDIR /database

# Виртуальное окружение для slim-версий
COPY pyproject.toml poetry.lock ./
RUN pip install poetry 
RUN poetry self update

RUN python -m venv /venv
RUN . /venv/bin/activate && poetry install --no-root --without dev

FROM python:3.12-slim AS production
COPY . .
COPY --from=build /venv /venv
COPY startup.sh ./

# Артефакт с переносами каретки в sh и bash
# RUN sed -i 's/\r$//' startup.sh

EXPOSE 8100

ENTRYPOINT [ "/bin/sh", "./startup.sh" ]
