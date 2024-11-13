FROM ubuntu/bind9:latest

# Set environment variables to non-interactive for apt
ENV DEBIAN_FRONTEND=noninteractive

# Install BIND9, Python, and necessary utilities
RUN apt-get update && \
    apt-get install -y bind9 bind9utils bind9-doc python3 python3-pip netcat-openbsd && \
    rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

COPY . /app/

RUN chmod +x /app/wait-for-it.sh

# Install Python dependencies
RUN pip3 install --no-cache-dir psycopg2-binary requests

# Copy the entrypoint script
COPY entrypoint.sh /app/entrypoint.sh
RUN chmod +x /app/entrypoint.sh

# Expose DNS ports
EXPOSE 53/tcp
EXPOSE 53/udp

# Mount zones directory
VOLUME ["/etc/bind/zones"]

# Use the custom entrypoint
ENTRYPOINT ["/app/entrypoint.sh"]
