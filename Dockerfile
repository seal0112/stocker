FROM python:3.9.18-alpine3.18

WORKDIR /app
COPY . /app

RUN apk update && \
    apk add --no-cache --virtual .build-deps gcc musl-dev libffi-dev openssl-dev python3-dev && \
    pip install --upgrade pip && \
    pip install -r requirements.txt

RUN addgroup -S stocker && \
    adduser -S stocker -G stocker && \
    chown -R stocker:stocker /app
USER stocker

CMD ["gunicorn", "wsgi:app"]
