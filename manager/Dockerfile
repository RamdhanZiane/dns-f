FROM python:3.9-slim

WORKDIR /app

COPY . .

RUN apt-get update && apt-get install -y netcat && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir -r requirements.txt

COPY manage_dns.py .

# Ensure the wait-for-it.sh script is executable
RUN chmod +x wait-for-it.sh

# Use wait-for-it.sh to wait for PostgreSQL before starting the application
CMD ["./wait-for-it.sh", "postgres:5432", "--", "python", "manage_dns.py"]
