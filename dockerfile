FROM python:3.10-slim

WORKDIR /app

COPY . .
RUN pip install --no-cache-dir -r requirements.txt

ENV DEPLOYMENT_TOKEN='' \
    DEV_SERVER_TOKEN=''

CMD ["python", "src/main.py"]
