# //FROM python:3.10 AS builder

# ENV PYTHONUNBUFFERED=1 \
#     PYTHONDONTWRITEBYTECODE=1
# //WORKDIR /app

# ENV PIPENV_VENV_IN_PROJECT=1 \
#     PIPENV_CUSTOM_VENV_NAME=.venv

# RUN pip install pipenv
# COPY Pipfile Pipfile.lock ./

# RUN pipenv install
# FROM python:3.10-slim
# # WORKDIR /app
# COPY --from=builder /app/.venv .venv/
# COPY . .
# CMD ["/app/.venv/bin/fastapi", "run"]



FROM python:3.10 AS builder

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1

WORKDIR /code

ENV PIPENV_VENV_IN_PROJECT=1 \
    PIPENV_CUSTOM_VENV_NAME=.venv

RUN pip install pipenv

COPY COPY Pipfile Pipfile.lock ./

RUN pipenv install

# RUN pip install --no-cache-dir --upgrade -r /code/requirements.txt

COPY ./app /code/app

CMD ["fastapi", "run", "app/main.py", "--port", "8000"]