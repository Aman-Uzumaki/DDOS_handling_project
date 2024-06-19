from http.server import BaseHTTPRequestHandler, HTTPServer
import logging

# Dictionary to store unique IP addresses and their request counts
ip_request_count = {}

class RequestHandler(BaseHTTPRequestHandler):
    def log_message(self, format, *args):
        # Check for custom header 'X-Fake-IP'
        fake_ip = self.headers.get('X-Fake-IP')
        ip_address = fake_ip if fake_ip else self.client_address[0]

        if ip_address not in ip_request_count:
            ip_request_count[ip_address] = 0
            logging.info("New unique IP detected: %s" % ip_address)
        
        ip_request_count[ip_address] += 1
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

def run(server_class=HTTPServer, handler_class=RequestHandler, port=8080):
    logging.basicConfig(level=logging.INFO)
    server_address = ('', port)
    httpd = server_class(server_address, handler_class)
    logging.info('Starting server on port %d...\n' % port)
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        pass
    httpd.server_close()
    logging.info('Stopping server...\n')

if __name__ == '__main__':
    run()
