FROM python:3

RUN apt-get update && apt-get -y install netcat && apt-get clean

WORKDIR /app

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY config.yaml ./
COPY run.sh ./
COPY match/ ./match/

RUN chmod +x ./run.sh

CMD ["./run.sh"]
