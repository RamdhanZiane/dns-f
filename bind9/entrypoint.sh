#!/bin/bash
set -e

# Start BIND9 in the background
echo "Starting BIND9..."
/usr/sbin/named -f -c /etc/bind/named.conf -u bind &

# Wait for PostgreSQL to be ready
echo "Waiting for PostgreSQL to be ready..."
# ./wait-for-it.sh postgres:5432 --timeout=30 --strict -- echo "PostgreSQL is up"

# Start the DNS manager Python script
echo "Starting DNS Manager..."
python3 /app/manage_dns.py 

# # Wait indefinitely to keep the container running
# wait -n

# # Exit with the status of the first process that exited
# exit $?