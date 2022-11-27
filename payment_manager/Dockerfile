FROM python:3.10

RUN mkdir /payment_manager
WORKDIR /payment_manager

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1
COPY ./requirements.txt requirements.txt

RUN  pip install --upgrade pip && pip install --no-cache-dir -r requirements.txt

COPY . .
COPY ./wait-for-it.sh /usr/bin/wait-for-it.sh
RUN chmod 777 /usr/bin/wait-for-it.sh

# для запуска на винде
RUN sed -i 's/\r//' /usr/bin/wait-for-it.sh

CMD ["wait-for-it.sh"]