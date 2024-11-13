import time
import psycopg2
import os
import requests
import logging
import subprocess  # Added for executing rndc commands

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s %(levelname)s:%(message)s')

# Database configuration
DB_HOST = os.getenv('POSTGRES_HOST', 'postgres')
DB_PORT = os.getenv('POSTGRES_PORT', '5432')
DB_NAME = os.getenv('POSTGRES_DB', 'dnsdb')
DB_USER = os.getenv('POSTGRES_USER', 'user')
DB_PASSWORD = os.getenv('POSTGRES_PASSWORD', 'password')

# Nginx Proxy Manager API configuration
NPM_API_URL = os.getenv('NPM_API_URL', 'http://nginx-proxy-manager:81/api')
NPM_API_KEY = os.getenv('NPM_API_KEY', 'your_api_key_here')

def get_db_connection():
    try:
        conn = psycopg2.connect(
            host=DB_HOST,
            port=DB_PORT,
            dbname=DB_NAME,
            user=DB_USER,
            password=DB_PASSWORD
        )
        return conn
    except Exception as e:
        logging.error(f"Database connection failed: {e}")
        return None

def get_new_domains():
    conn = get_db_connection()
    if not conn:
        return []
    try:
        with conn.cursor() as cur:
            cur.execute("SELECT domain, ip_address FROM domains WHERE is_processed = FALSE;")
            domains = [{'domain': row[0], 'ip_address': row[1]} for row in cur.fetchall()]
            return domains
    except Exception as e:
        logging.error(f"Error fetching new domains: {e}")
        return []
    finally:
        conn.close()

def mark_domain_as_processed(domain):
    conn = get_db_connection()
    if not conn:
        return
    try:
        with conn.cursor() as cur:
            cur.execute("UPDATE domains SET is_processed = TRUE WHERE domain = %s;", (domain,))
            conn.commit()
    except Exception as e:
        logging.error(f"Error marking domain as processed: {e}")
    finally:
        conn.close()

def add_zone_with_rndc(domain_info):
    domain = domain_info['domain']
    ip_address = domain_info['ip_address']
    zone_name = domain
    zone_file = f"/etc/bind/zones/db.{domain}"

    # Create zone file content
    zone_content = f"""$TTL    604800
@       IN      SOA     ns1.{domain}. admin.{domain}. (
                              2         ; Serial
                         604800         ; Refresh
                          86400         ; Retry
                        2419200         ; Expire
                         604800 )       ; Negative Cache TTL
;
@       IN      NS      ns1.{domain}.
@       IN      A       {ip_address}
www     IN      CNAME   {domain}.
"""

    try:
        # Write zone file
        with open(zone_file, 'w') as zf:
            zf.write(zone_content)
        logging.info(f"Zone file created for {domain}")

        # Add zone using rndc
        add_zone_cmd = [
            'rndc', 'addzone',
            zone_name,
            f'type master; file "{zone_file}";'
        ]
        subprocess.run(add_zone_cmd, check=True)
        logging.info(f"Zone {domain} added via rndc")

        # Reload BIND9 to apply changes
        reload_bind_cmd = ['rndc', 'reload']
        subprocess.run(reload_bind_cmd, check=True)
        logging.info("BIND9 reloaded successfully via rndc")

    except subprocess.CalledProcessError as e:
        logging.error(f"rndc command failed: {e}")
    except Exception as e:
        logging.error(f"Error adding zone with rndc for {domain}: {e}")

def request_ssl_certificate(domain):
    headers = {
        'Authorization': f'Bearer {NPM_API_KEY}',
        'Content-Type': 'application/json'
    }
    data = {
        "domain": {
            "name": domain,
            "type": "domain",
            "wildcard": False
        },
        "ssl": {
            "type": "letsencrypt",
            "email": "admin@example.com",
            "agree_to_terms": True
        }
    }
    try:
        response = requests.post(f"{NPM_API_URL}/certificates", json=data, headers=headers)
        if response.status_code == 201:
            logging.info(f"SSL certificate requested for {domain}")
        else:
            logging.error(f"Failed to request SSL for {domain}: {response.text}")
    except Exception as e:
        logging.error(f"Error requesting SSL for {domain}: {e}")

def update_bind(domains):
    for domain_info in domains:
        add_zone_with_rndc(domain_info)
        request_ssl_certificate(domain_info['domain'])
        mark_domain_as_processed(domain_info['domain'])

def main():
    while True:
        domains = get_new_domains()
        if domains:
            update_bind(domains)
        time.sleep(600)  # Wait for 10 minutes

if __name__ == "__main__":
    main()
