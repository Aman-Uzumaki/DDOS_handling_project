from flask import Flask, request, jsonify, redirect, url_for, render_template_string
import threading
import logging
import time

app = Flask(__name__)

# Configuration
INACTIVITY_THRESHOLD = 60  # Time in seconds after which an IP is considered inactive
REQUEST_THRESHOLD = 10  # Max number of requests per minute before server is considered busy
REQUEST_INTERVAL = 60  # Time in seconds for request count interval

# Data structures
ip_request_count = {}
ip_last_access_time = {}
suspected_ips = set()
confirm_ips = set()
lock = threading.Lock()
total_request_count = 0

# Passcode for verification
PASSCODE = "human"

def reset_request_count():
    global total_request_count
    with lock:
        total_request_count = 0
    threading.Timer(REQUEST_INTERVAL, reset_request_count).start()

def remove_inactive_ips():
    while True:
        current_time = time.time()
        with lock:
            inactive_ips = [ip for ip, last_access in ip_last_access_time.items()
                            if current_time - last_access > INACTIVITY_THRESHOLD]
            for ip in inactive_ips:
                if ip in ip_request_count:
                    del ip_request_count[ip]
                if ip in ip_last_access_time:
                    del ip_last_access_time[ip]
                logging.info("IP removed due to inactivity: %s" % ip)
        time.sleep(10)  # Check every 10 seconds

reset_request_count()
threading.Thread(target=remove_inactive_ips, daemon=True).start()

@app.before_request
def before_request():
    global total_request_count
    ip_address = request.remote_addr

    with lock:
        # Check if the IP is in the suspected set
        if ip_address in suspected_ips:
            return render_template_string('''
                <form action="{{ url_for('verify') }}" method="post">
                    <label for="passcode">Enter passcode to verify you're human:</label>
                    <input type="text" id="passcode" name="passcode">
                    <input type="submit" value="Submit">
                </form>
            '''), 403

        # Check if the IP is in the confirm set
        if ip_address in confirm_ips:
            return "You are not allowed to access the server.", 403

        # Check if the server is busy
        if total_request_count >= REQUEST_THRESHOLD:
            suspected_ips.update(ip_request_count.keys())
            return "The server is busy, try after 5 minutes", 503

        # Update request count and last access time for the IP
        if ip_address not in ip_request_count:
            ip_request_count[ip_address] = 0
            ip_last_access_time[ip_address] = time.time()
            logging.info("New unique IP detected: %s" % ip_address)

        ip_request_count[ip_address] += 1
        ip_last_access_time[ip_address] = time.time()
        total_request_count += 1

        logging.info("%s - Request count: %d, Total requests: %d" %
                     (ip_address, ip_request_count[ip_address], total_request_count))

        # Move IP to suspected set if it reaches the request limit
        if ip_request_count[ip_address] >= 5:
            del ip_request_count[ip_address]
            suspected_ips.add(ip_address)

@app.route('/verify', methods=['POST'])
def verify():
    ip_address = request.remote_addr
    passcode = request.form.get('passcode')

    # Log the form data
    app.logger.info("Form submitted: IP=%s, Passcode=%s" % (ip_address, passcode))

    with lock:
        if ip_address in suspected_ips:
            if passcode == PASSCODE:
                suspected_ips.remove(ip_address)
                ip_request_count[ip_address] = 1  # Reset the request count
                ip_last_access_time[ip_address] = time.time()
                return redirect(url_for('home'))
            else:
                confirm_ips.add(ip_address)
                suspected_ips.remove(ip_address)
                return "Access denied, incorrect passcode.", 403
    return "No verification needed."

@app.route('/')
def home():
    return "Hello, you have reached the server!"

if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    app.run(port=8080)

