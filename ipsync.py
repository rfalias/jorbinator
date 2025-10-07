import CloudFlare
import requests

# Configuration
CLOUDFLARE_API_TOKEN = 'YOURTOKEN'  # Replace with your Cloudflare API tokena

# List of DNS records to check and update
DNS_RECORDS = [
    {'name': 'vpn.yourdomain.com', 'type': 'A'},
    {'name': 'tvpub.yourdomain.com', 'type': 'A'},
    {'name': 'navipub.yourdomain.com', 'type': 'A'},
    {'name': 'music.yourdomain.com', 'type': 'A'},
    {'name': 'access.yourdomain.com', 'type': 'A'},
    {'name': 'access-api.yourdomain.com', 'type': 'A'},
    {'name': 'stream.yourdomain.com', 'type': 'A'},
    {'name': 'ombi.yourdomain.com', 'type': 'A'},
    {'name': 'pitboss.yourdomain.com', 'type': 'A'},
    {'name': 'factory.yourdomain.com', 'type': 'A'}
]


def get_public_ip():
    """Fetch the current public IP address."""
    try:
        response = requests.get('https://api.ipify.org?format=json')
        response.raise_for_status()
        return response.json()['ip']
    except requests.RequestException as e:
        print(f"Error fetching public IP: {e}")
        return None

def get_zone_id(cf, domain_name):
    """Get the Zone ID for a given domain name."""
    try:
        zones = cf.zones.get(params={'name': domain_name})
        if len(zones) == 0:
            print(f"No zone found for domain: {domain_name}")
            return None
        return zones[0]['id']
    except CloudFlare.exceptions.CloudFlareAPIError as e:
        print(f"Error fetching zone ID for {domain_name}: {e}")
        return None

def update_dns_records(cf, zone_id, records, new_ip):
    """Update DNS records if IP has changed."""
    for record in records:
        try:
            dns_records = cf.zones.dns_records.get(zone_id, params={'name': record['name'], 'type': record['type']})
            if len(dns_records) == 0:
                print(f"No DNS record found for {record['name']}.")
                continue

            dns_record = dns_records[0]  # Assume the first record is the correct one
            if dns_record['content'] != new_ip:
                print(f"IP has changed for {record['name']} from {dns_record['content']} to {new_ip}. Updating DNS record...")
                dns_record_id = dns_record['id']
                dns_record['content'] = new_ip  # Update with new IP
                cf.zones.dns_records.put(zone_id, dns_record_id, data=dns_record)
                print(f"DNS record for {record['name']} updated successfully.")
            else:
                print(f"IP address for {record['name']} has not changed. No update needed.")

        except CloudFlare.exceptions.CloudFlareAPIError as e:
            print(f"Error updating DNS record for {record['name']}: {e}")

def main():
    # Initialize Cloudflare client
    cf = CloudFlare.CloudFlare(token=CLOUDFLARE_API_TOKEN)

    # Step 1: Get the current public IP
    current_ip = get_public_ip()
    if not current_ip:
        return

    # Step 2: Get the Zone ID for the domain
    # Assuming all records are under the same domain
    domain_name = DNS_RECORDS[0]['name'].split('.', 1)[-1]  # Extract the domain (yourdomain.com from subdomain.yourdomain.com)
    print(f"Domain name is {domain_name}")
    zone_id = get_zone_id(cf, domain_name)
    print(f"Zone id is {zone_id}")
    if not zone_id:
        return

    # Step 3: Update DNS records if necessary
    update_dns_records(cf, zone_id, DNS_RECORDS, current_ip)

if __name__ == "__main__":
    main()

