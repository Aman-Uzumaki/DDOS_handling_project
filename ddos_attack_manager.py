from http.server import BaseHTTPRequestHandler, HTTPServer
import urllib.parse
import threading
import time
from collections import deque

# Global variables
active = dict()
suspected = dict()
bot = set()
total_requests_log = deque()  # To keep track of request timestamps
maximum_allowed_requests = 10
threshold = 5
timeout = 60  # 1 minute timeout

class RequestHandler(BaseHTTPRequestHandler):
    def log_status(self):
        print(f"Active: {active}")
        print(f"Suspected: {suspected}")
        print(f"Bot: {bot}")
        print(f"Total Requests in last 60 seconds: {len(total_requests_log)}")

    def do_GET(self):
        global active, suspected, bot, total_requests_log, maximum_allowed_requests, threshold
        
        # Get IP of device making request to the server
        IP = self.client_address[0]
        current_time = time.time()
        
        # Clean up old requests
        self.cleanup_old_requests(current_time)

        if IP in bot:
            # Deny access to the server
            self.send_response(403)
            self.end_headers()
            self.wfile.write(b"Access Denied")
        elif IP in suspected:
            if suspected[IP]['attempts'] <= 4:
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
                suspected[IP]['attempts'] += 1
            else:
                del suspected[IP]
                bot.add(IP)
                with open("bot.txt",'a') as f:
                    f.write(f"{IP}\n")
        else:
            if len(total_requests_log) < maximum_allowed_requests:
                if IP in active:
                    if active[IP]['requests'] < threshold:
                        active[IP]['requests'] += 1
                        active[IP]['last_request_time'] = current_time
                        total_requests_log.append(current_time)
                        self.send_response(200)
                        self.end_headers()
                        self.wfile.write(b"Request Accepted")
                    else:
                        del active[IP]
                        suspected[IP] = {'attempts': 0, 'last_request_time': current_time}
                        self.send_response(403)
                        self.end_headers()
                        self.wfile.write(b"Access Denied")
                else:
                    active[IP] = {'requests': 1, 'last_request_time': current_time}
                    total_requests_log.append(current_time)
                    self.send_response(200)
                    self.end_headers()
                    self.wfile.write(b"Request Accepted")
                    print(f"New IP discovered: {IP}")
            else:
                print("Server is busy. Try after some time.")
                total_requests_log.clear()
                for ip in active:
                    suspected[ip] = {'attempts': 0, 'last_request_time': current_time}
                active = dict()
                print('Possibility of DDoS attack')
                self.send_response(503)
                self.end_headers()
                self.wfile.write(b"Server Busy")
        
        self.log_status()  # Log status after handling the request
                
    def do_POST(self):
        global active, suspected, bot
        
        # Get IP of device making request to the server
        IP = self.client_address[0]
        current_time = time.time()

        # Clean up old requests
        self.cleanup_old_requests(current_time)

        if IP in suspected:
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            parsed_data = urllib.parse.parse_qs(post_data.decode('utf-8'))
            passcode = parsed_data.get('passcode', [None])[0]

            if passcode == 'human':
                del suspected[IP]
                active[IP] = {'requests': 0, 'last_request_time': current_time}
                total_requests_log.append(current_time)
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

        self.log_status()  # Log status after handling the request

    def cleanup_old_requests(self, current_time):
        # Remove requests older than 60 seconds
        while total_requests_log and current_time - total_requests_log[0] > 60:
            total_requests_log.popleft()

def cleanup_active_ips():
    global active, timeout
    while True:
        current_time = time.time()
        to_remove = [ip for ip, data in active.items() if current_time - data['last_request_time'] > timeout]
        for ip in to_remove:
            del active[ip]
            print(f"IP removed due to inactivity: {ip}")
        time.sleep(10)  # Check every 10 seconds

def run(server_class=HTTPServer, handler_class=RequestHandler, port=8080):
    server_address = ('', port)
    httpd = server_class(server_address, handler_class)
    print(f'Starting httpd server on port {port}')
    cleanup_thread = threading.Thread(target=cleanup_active_ips, daemon=True)
    cleanup_thread.start()
    httpd.serve_forever()

if __name__ == "__main__":
    run()
