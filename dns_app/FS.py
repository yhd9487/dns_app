import socket
from flask import Flask, request, jsonify

app = Flask(__name__)


@app.route('/register', methods=['PUT'])
def register():
    content = request.get_json()

    # Validate input content
    required_fields = ['hostname', 'ip', 'as_ip', 'as_port']
    if not all(field in content for field in required_fields):
        return jsonify({"error": "Missing fields"}), 400

    # Build the DNS message
    dns_message = f"----\nTYPE=A\nNAME={content['hostname']}\nVALUE={content['ip']}\nTTL=10\n----"

    # Send DNS message to AS using UDP
    as_address = (content['as_ip'], int(content['as_port']))
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
        sock.sendto(dns_message.encode(), as_address)
        # Optionally set a timeout for a response
        sock.settimeout(2.0)  # 2 seconds timeout

        try:
            # Try to receive a response
            data, _ = sock.recvfrom(1024)
            response_message = data.decode()
            print(f"Received response from AS: {response_message}")
        except socket.timeout:
            # If there's no response (which is normal for UDP), continue
            print("No response from AS, but that's okay for UDP.")

    # If you want to check the response, do it here.
    # If everything is okay, return a success message.
    return jsonify({"message": "Registered successfully"}), 201


@app.route('/fibonacci')
def fibonacci():
    number = request.args.get('number')
    if not number.isdigit():
        return jsonify({"error": "Bad format"}), 400
    fib_number = calculate_fibonacci(int(number))
    return jsonify({"fibonacci_number": fib_number}), 200


def calculate_fibonacci(n):
    a, b = 0, 1
    for _ in range(n):
        a, b = b, a + b
    return a


if __name__ == '__main__':
    app.run(port=9090)
