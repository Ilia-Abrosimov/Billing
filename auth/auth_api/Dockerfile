FROM python:3.10

COPY ./requirements.txt requirements.txt

RUN  pip install --upgrade pip && pip install --no-cache-dir -r requirements.txt

COPY . /code


WORKDIR /code
RUN chmod +x entrypoint.sh
RUN sed -i 's/\r//' entrypoint.sh

EXPOSE 8000

ENTRYPOINT ["./entrypoint.sh"]