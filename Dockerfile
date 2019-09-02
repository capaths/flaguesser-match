FROM python:3

LABEL version="0.1"
LABEL description="This image contains the match service for the Flaguesser App"

WORKDIR /app

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY config.yaml ./

COPY match/ match/
COPY images.txt ./

CMD ["nameko", "run", "--config", "config.yaml", "match.service"]
