import socket
import json
import os
import signal
import sys

db_file = 'dns_records.json'


def load_dns_records():
    if not os.path.isfile(db_file):
        return {}
    with open(db_file, 'r') as file:
        return json.load(file)


def save_dns_record(record):
    dns_records = load_dns_records()
    dns_records[record['NAME']] = record
    with open(db_file, 'w') as file:
        json.dump(dns_records, file, indent=4)


def handle_dns_request(data, client_address, server_socket):
    try:
        fields = data.split('\n')
        query_type = fields[0].split('=')[1]
        name = fields[1].split('=')[1]
        if query_type == 'A':
            dns_records = load_dns_records()
            record = dns_records.get(name)
            if record:
                response = f"TYPE=A\nNAME={name}\nVALUE={record['VALUE']}\nTTL={record['TTL']}"
                server_socket.sendto(response.encode(), client_address)
            else:
                print(f"No record found for {name}")
        else:
            print("Unhandled query type")
    except Exception as e:
        print(f"Error handling DNS request: {e}")


def graceful_shutdown(sig, frame):
    print('Shutting down server...')
    sock.close()
    sys.exit(0)


signal.signal(signal.SIGINT, graceful_shutdown)
signal.signal(signal.SIGTERM, graceful_shutdown)

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.bind(('localhost', 53533))

print("Authoritative Server running...")

while True:
    try:
        data, addr = sock.recvfrom(512)
        data = data.decode().strip()
        if data.startswith('TYPE=A'):
            handle_dns_request(data, addr, sock)
        else:
            print("Invalid DNS request")
    except KeyboardInterrupt:
        graceful_shutdown(None, None)
