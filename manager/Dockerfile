FROM python:3.9-slim

WORKDIR /app

COPY . .

# Install bind9utils for rndc and netcat-openbsd for testing connections
RUN apt-get update && \
    apt-get install -y bind9utils netcat-openbsd && \
    rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir -r requirements.txt

COPY manage_dns.py .

# (Optional) If you decide to use wait-for-it.sh later
# RUN chmod +x wait-for-it.sh

# Use wait-for-it.sh to wait for PostgreSQL before starting the application (if using)
CMD ["./wait-for-it.sh", "postgres:5432", "--", "python", "manage_dns.py"]

# Mount zones directory
VOLUME ["/etc/bind/zones"]
