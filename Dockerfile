FROM python:3.9-slim

COPY ./requirements.txt /app/requirements.txt

RUN python3 -m pip install --quiet -r /app/requirements.txt --no-cache-dir

COPY ./scripts/start-reload.sh /start-reload.sh
RUN chmod +x /start-reload.sh

COPY ./app /app
WORKDIR /app/

ENV PYTHONPATH=/app
ENV SQLALCHEMY_WARN_20=1

EXPOSE 80

CMD ["/start-reload.sh"]
