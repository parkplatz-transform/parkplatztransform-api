FROM python:3.9

COPY ./requirements.txt /app/requirements.txt

RUN \
 apt-get update && apt-get install -y libgeos-dev && \
 python3 -m pip install --quiet -r /app/requirements.txt --no-cache-dir

COPY ./app /app

EXPOSE 80

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "80"]

