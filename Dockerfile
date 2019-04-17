FROM python:3.7-alpine

ARG EXT_API_KEY
ENV EXTERNAL_API_KEY=$EXT_API_KEY
COPY . /app
WORKDIR /app
RUN pip install -r requirements.txt

CMD gunicorn -w 4 -b 0.0.0.0:$PORT app.api:app
