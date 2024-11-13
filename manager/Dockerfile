FROM python:3.9-slim

WORKDIR /app

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY manage_dns.py .

CMD ["python", "manage_dns.py"]
