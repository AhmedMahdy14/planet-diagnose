FROM python:3.10-slim

WORKDIR /app

COPY . /app

RUN pip install -r requirements.txt

EXPOSE 5000

ENV FLASK_APP=app

CMD exec gunicorn --bind 0.0.0.0:$PORT app:app
