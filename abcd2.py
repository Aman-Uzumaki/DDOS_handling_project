from http.server import BaseHTTPRequestHandler, HTTPServer
import urllib.parse

# Global variables
active = dict()
suspected = set()
bot = set()
total_requests = 0
maximum_allowed_requests = 10
threshold = 5

class RequestHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        global active, suspected, bot, total_requests, maximum_allowed_requests, threshold
        
        # Get IP of device making request to the server
        IP = self.client_address[0]
        
        if IP in bot:
            # Deny access to the server
            self.send_response(403)
            self.end_headers()
            self.wfile.write(b"Access Denied")
        elif IP in suspected:
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            self.wfile.write(b"""
                <html>
                <body>
                <form method="post">
                Enter the passcode: <input type="text" name="passcode"><br>
                <input type="submit" value="Submit">
                </form>
                </body>
                </html>
            """)
        else:
            if total_requests <= maximum_allowed_requests:
                if IP in active:
                    if active[IP] < threshold:
                        active[IP] += 1
                        total_requests += 1
                        self.send_response(200)
                        self.end_headers()
                        self.wfile.write(b"Request Accepted")
                    else:
                        del active[IP]
                        suspected.add(IP)
                        self.send_response(403)
                        self.end_headers()
                        self.wfile.write(b"Access Denied")
                else:
                    active[IP] = 1
                    total_requests += 1
                    self.send_response(200)
                    self.end_headers()
                    self.wfile.write(b"Request Accepted")
            else:
                print("Server is busy. Try after some time.")
                total_requests = 0
                for ip in active:
                    suspected.add(ip)
                active = dict()
                print('Possibility of DDoS attack')
                self.send_response(503)
                self.end_headers()
                self.wfile.write(b"Server Busy")
                
    def do_POST(self):
        global active, suspected, bot
        
        # Get IP of device making request to the server
        IP = self.client_address[0]

        if IP in suspected:
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            parsed_data = urllib.parse.parse_qs(post_data.decode('utf-8'))
            passcode = parsed_data.get('passcode', [None])[0]

            if passcode == 'human':
                suspected.remove(IP)
                active[IP] = 0
                # Accept the request to the server
                self.send_response(200)
                self.end_headers()
                self.wfile.write(b"Request Accepted")
            else:
                self.send_response(401)
                self.end_headers()
                self.wfile.write(b"Incorrect passcode. Try Again")
        else:
            self.send_response(400)
            self.end_headers()
            self.wfile.write(b"Bad Request")

def run(server_class=HTTPServer, handler_class=RequestHandler, port=8080):
    server_address = ('', port)
    httpd = server_class(server_address, handler_class)
    print(f'Starting httpd server on port {port}')
    httpd.serve_forever()

if __name__ == "__main__":
    run()
