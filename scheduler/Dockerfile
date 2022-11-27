FROM python:3.10
COPY ./requirements.txt requirements.txt
RUN  pip install --upgrade pip && pip install --no-cache-dir -r requirements.txt

COPY . /code

WORKDIR /code

ENTRYPOINT [ "celery", "-A", "main", "worker", "-l", "info", "-B" ]
