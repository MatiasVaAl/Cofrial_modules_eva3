FROM python:3.12-slim

RUN apt-get update \
    && apt-get install -y --no-install-recommends ca-certificates \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app
COPY simulator.py /app/simulator.py

ENV PYTHONUNBUFFERED=1

CMD ["python", "/app/simulator.py"]
