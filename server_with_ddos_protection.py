from http.server import BaseHTTPRequestHandler, HTTPServer
import logging
from threading import Thread, Lock, Timer
import time

# Dictionary to store unique IP addresses, their request counts, and the last access time
ip_request_count = {}
ip_last_access_time = {}
suspected_ips = set()
lock = Lock()

# Configuration
INACTIVITY_THRESHOLD = 60  # Time in seconds after which an IP is considered inactive
REQUEST_THRESHOLD = 5  # Max number of requests per minute before server is considered busy
REQUEST_INTERVAL = 60  # Time in seconds for request count interval

# Counter for total number of requests in the current interval
total_request_count = 0

def reset_request_count():
    global total_request_count
    with lock:
        total_request_count = 0
    Timer(REQUEST_INTERVAL, reset_request_count).start()

class RequestHandler(BaseHTTPRequestHandler):
    def log_message(self, format, *args):
        ip_address = self.headers.get('X-Fake-IP', self.client_address[0])

        with lock:
            # Check if the IP is suspected and deny access
            if ip_address in suspected_ips:
                self.send_response(403)
                self.send_header('Content-type', 'text/html')
                self.end_headers()
                self.wfile.write(b"You are suspected for DDoS attack. Hence, access denied.")
                return

            # Check if the server is busy
            global total_request_count
            if total_request_count >= REQUEST_THRESHOLD:
                suspected_ips.update(ip_request_count.keys())
                self.send_response(503)
                self.send_header('Content-type', 'text/html')
                self.end_headers()
                self.wfile.write(b"The server is busy, try after some time")
                return

            # Update request count and last access time for the IP
            if ip_address not in ip_request_count:
                ip_request_count[ip_address] = 0
                ip_last_access_time[ip_address] = time.time()
                logging.info("New unique IP detected: %s" % ip_address)

            ip_request_count[ip_address] += 1
            ip_last_access_time[ip_address] = time.time()
            total_request_count += 1

            logging.info("%s - - [%s] %s (Request count: %d, Total requests: %d)\n" %
                         (ip_address,
                          self.log_date_time_string(),
                          format % args,
                          ip_request_count[ip_address],
                          total_request_count))

    def do_GET(self):
        with lock:
            self.log_message("GET %s" % self.path)
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()
        self.wfile.write(b"Hello, you have reached the server!")

def remove_inactive_ips():
    while True:
        current_time = time.time()
        with lock:
            inactive_ips = [ip for ip, last_access in ip_last_access_time.items()
                            if current_time - last_access > INACTIVITY_THRESHOLD]

            for ip in inactive_ips:
                del ip_request_count[ip]
                del ip_last_access_time[ip]
                logging.info("IP removed due to inactivity: %s" % ip)

        time.sleep(10)  # Check every 10 seconds

def run(server_class=HTTPServer, handler_class=RequestHandler, port=8080):
    logging.basicConfig(level=logging.INFO)
    server_address = ('', port)
    httpd = server_class(server_address, handler_class)
    logging.info('Starting server on port %d...\n' % port)

    # Start background thread to remove inactive IPs
    thread = Thread(target=remove_inactive_ips, daemon=True)
    thread.start()

    # Start timer to reset the request count every minute
    reset_request_count()

    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        pass
    httpd.server_close()
    logging.info('Stopping server...\n')

if __name__ == '__main__':
    run()

