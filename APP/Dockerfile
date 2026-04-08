FROM python:3.12-alpine

ENV HOME=/home/test_task \
    APP_HOME=/home/test_task/APP \
	MIGRATIONS=/home/migration \
    PYTHONPATH="$PYTHONPATH:/home/test_task" \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

RUN mkdir -p $APP_HOME \
  && mkdir -p MIGRATIONS \
  && addgroup -S dimatech \
  && adduser -S dimatech -G dimatech

WORKDIR $HOME
 
COPY APP APP
COPY migration ./migration
COPY requirements.txt alembic.ini .env .

RUN pip install --upgrade pip \
 && pip install -r requirements.txt \
 && chown -R dimatech:dimatech .
 
 USER dimatech