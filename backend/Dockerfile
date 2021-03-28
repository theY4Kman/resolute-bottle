FROM python:3.10.0a6-buster
ARG ENV="development"
ENV PORT=80

RUN pip install poetry \
  && poetry config virtualenvs.create false

WORKDIR /backend
COPY poetry.lock pyproject.toml /backend/
RUN poetry install \
      --no-interaction \
      --no-root \
      $(test "$ENV" = 'production' && '--no-dev')

COPY . /backend

CMD ["/backend/run_production_server.sh"]
