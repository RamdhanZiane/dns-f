FROM ubuntu/bind9:latest

# Set environment variables to non-interactive for apt
ENV DEBIAN_FRONTEND=noninteractive

# Install BIND9, Python, and necessary utilities
RUN apt-get update && \
    apt-get install -y \
    bind9 \
    bind9utils \
    bind9-doc \
    python3 \
    python3-pip \
    python3-psycopg2 \
    python3-requests \
    netcat-openbsd && \
    rm -rf /var/lib/apt/lists/*

# Generate rndc.key
RUN rndc-confgen -a -c /etc/bind/rndc.key && \
    chown bind:bind /etc/bind/rndc.key && \
    chmod 600 /etc/bind/rndc.key

# Set working directory
WORKDIR /app

# Copy application files into the container
COPY . /app/

# Ensure wait-for-it.sh is executable
RUN chmod +x /app/wait-for-it.sh

# Remove pip install step since packages are installed via apt
# RUN pip3 install --no-cache-dir psycopg2-binary requests

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
