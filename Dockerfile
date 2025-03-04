FROM python:3.12-slim

WORKDIR /app

COPY requirements.txt requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

COPY app /app
COPY best.pt /best.pt

CMD ["gunicorn", "app.main:app"]
