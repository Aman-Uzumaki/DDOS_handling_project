# DDoS Detection and Prevention System

## Overview

This project is designed to detect and prevent Distributed Denial of Service (DDoS) attacks by monitoring and managing incoming requests to a server. The system keeps track of request patterns from different IP addresses and takes appropriate actions when suspicious activity is detected.

## Features

- **IP Tracking**: Monitors the number of requests from each IP address.
- **Rate Limiting**: Limits the number of requests an IP can make within a specified timeframe.
- **Suspicious IP Detection**: Identifies IPs that exceed the allowed threshold of requests and marks them as suspicious.
- **Bot Detection**: Marks IPs as bots if they fail to pass a verification check.
- **Automatic Cleanup**: Removes inactive IPs from the active list after a specified timeout.
- **Logging**: Logs the status of active, suspected, and bot IPs to the console.
- **Manual IP Testing**: Allows manual testing with fake IP addresses to simulate different request patterns.

## Approach

1. **Request Handling**:
   - Uses `BaseHTTPRequestHandler` from Python's `http.server` module to handle incoming HTTP requests.
   - Differentiates between GET and POST requests.

2. **IP Monitoring**:
   - Tracks requests from each IP in the `active` dictionary, logging the number of requests and the last request time.
   - Uses a `suspected` dictionary for IPs that exceed the request threshold but have not yet been marked as bots.
   - Maintains a `bot` set for IPs that are confirmed as bots.

3. **Rate Limiting**:
   - Defines a maximum allowed number of requests (`maximum_allowed_requests`) within a certain period (60 seconds).
   - Checks the number of requests in the last 60 seconds to enforce rate limiting.

4. **Suspicious IP Detection**:
   - Moves IPs that exceed the request threshold to the `suspected` list.
   - Provides a passcode verification form for suspected IPs to prove they are not bots.

5. **Bot Detection**:
   - Marks IPs as bots if they fail the passcode verification multiple times.
   - Appends bot IPs to a `bot.txt` file for logging.

6. **Automatic Cleanup**:
   - Uses a background thread to periodically remove inactive IPs from the `active` list if they have been inactive for a specified timeout (60 seconds).

7. **Manual IP Testing**:
   - Allows setting fake IP addresses via query parameters and form inputs for testing purposes.

## Usage

### Starting the Server

Run the following command to start the server:

```bash
python ddos_attack_manager.py
```

### Making Requests

- **GET Requests**: Use a web browser or HTTP client to make GET requests to the server. You can include a `fake_ip` query parameter to simulate requests from different IP addresses:
  ```bash
  http://localhost:8080?fake_ip=192.168.1.1
  ```

- **POST Requests**: Submit the passcode verification form provided by the server for suspected IPs. Include a `fake_ip` input to simulate different IP addresses.

### Viewing Logs

Check the console output to view the status of active, suspected, and bot IPs, as well as other relevant logs.

## File Structure

- `ddos_attack_manager.py`: The main script containing the DDoS detection and prevention logic.
- `bot.txt`: A log file where bot IPs are recorded.

## Contributing

Feel free to fork this repository and contribute by submitting pull requests. For major changes, please open an issue first to discuss what you would like to change.
