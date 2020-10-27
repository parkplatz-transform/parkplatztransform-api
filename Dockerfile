FROM tiangolo/uvicorn-gunicorn-fastapi:python3.8-alpine3.10

COPY ./requirements.txt /app/requirements.txt
RUN \
 apk add --no-cache postgresql-libs && \
 apk add --no-cache --virtual .build-deps gcc musl-dev postgresql-dev && \
 python3 -m pip install --quiet -r requirements.txt --no-cache-dir && \
 apk --purge del .build-deps

COPY ./app /app

CMD /start-reload.sh
