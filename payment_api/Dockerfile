FROM python:3.10

COPY ./requirements.txt .

RUN  pip install --upgrade pip && pip install --no-cache-dir -r requirements.txt

COPY /src /src

WORKDIR /src
RUN chmod +x entrypoint.sh

# для запуска на винде
RUN sed -i 's/\r//' entrypoint.sh

EXPOSE 8000

ENTRYPOINT ["./entrypoint.sh"]