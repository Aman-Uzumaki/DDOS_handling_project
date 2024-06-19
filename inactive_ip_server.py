from http.server import BaseHTTPRequestHandler, HTTPServer
import logging
from threading import Thread, Lock
import time

# Dictionary to store unique IP addresses, their request counts, and the last access time
ip_request_count = {}
ip_last_access_time = {}
lock = Lock()
INACTIVITY_THRESHOLD = 60  # Time in seconds after which an IP is considered inactive

class RequestHandler(BaseHTTPRequestHandler):
    def log_message(self, format, *args):
        ip_address = self.headers.get('X-Fake-IP', self.client_address[0])

        with lock:
            if ip_address not in ip_request_count:
                ip_request_count[ip_address] = 0
                ip_last_access_time[ip_address] = time.time()
                logging.info("New unique IP detected: %s" % ip_address)

            ip_request_count[ip_address] += 1
            ip_last_access_time[ip_address] = time.time()

            logging.info("%s - - [%s] %s (Request count: %d)\n" %
                         (ip_address,
                          self.log_date_time_string(),
                          format % args,
                          ip_request_count[ip_address]))

    def do_GET(self):
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()
        self.wfile.write(b"Hello, you have reached the server!")
        return

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

    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        pass
    httpd.server_close()
    logging.info('Stopping server...\n')

if __name__ == '__main__':
    run()
