FROM python:3.11-slim-bullseye

RUN apt-get update -y && \
    apt-get install -y build-essential && \
    apt-get install -y librdkafka-dev

WORKDIR /bytewax
# Install bytewax and the dependencies you need here

COPY requirements.txt requirements.txt
COPY dataflow.py dataflow.py
RUN mkdir data
COPY data/products.jsonl data/products.jsonl

RUN pip install --upgrade pip
RUN python3 --version && pip install -r requirements.txt

ENV PYTHONUNBUFFERED 1
CMD ["python", "-m", "bytewax.run", "dataflow"]