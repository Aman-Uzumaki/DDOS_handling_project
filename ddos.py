from http.server import BaseHTTPRequestHandler, HTTPServer
import logging

# Set to store unique IP addresses
unique_ips = set()

class RequestHandler(BaseHTTPRequestHandler):
    def log_message(self, format, *args):
        ip_address = self.client_address[0]
        if ip_address not in unique_ips:
            unique_ips.add(ip_address)
            logging.info("New unique IP detected: %s" % ip_address)
        
        logging.info("%s - - [%s] %s\n" %
                     (ip_address,
                      self.log_date_time_string(),
                      format % args))

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
