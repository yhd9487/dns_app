from flask import Flask, request, jsonify
import dns.resolver
import requests  # Make sure to install this package

app = Flask(__name__)


@app.route('/fibonacci', methods=['GET'])
def get_fibonacci():
    hostname = request.args.get('hostname')
    fs_port = request.args.get('fs_port')
    number = request.args.get('number')
    as_ip = request.args.get('as_ip')
    as_port = request.args.get('as_port')

    # Check if all parameters are provided
    if not all([hostname, fs_port, number, as_ip, as_port]):
        return 'Bad Request', 400

    try:
        # Use DNS resolver to get the IP address of FS
        answers = dns.resolver.resolve(hostname, 'A')
        fs_ip = answers[0].to_text()

        # Send a request to the FS to get the Fibonacci number
        fs_url = f"http://{fs_ip}:{fs_port}/fibonacci/{number}"
        response = requests.get(fs_url)

        if response.status_code == 200:
            # Assume the FS returns a JSON with the Fibonacci number
            fibonacci_number = response.json().get('fibonacci_number')
            return jsonify(fibonacci_number=fibonacci_number), 200
        else:
            # FS did not return a successful response
            return 'Error contacting Fibonacci Server', response.status_code
    except Exception as e:
        return str(e), 500


if __name__ == '__main__':
    app.run(port=8080)
