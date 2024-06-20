# DDoS Detection and Prevention System

## Overview

This project is designed to detect and prevent Distributed Denial of Service (DDoS) attacks by monitoring and managing incoming requests to a server. Request patterns from different IP addresses are tracked, and appropriate actions are taken when suspicious activity is detected.

## Features

- **IP Tracking**: The number of requests from each IP address is monitored.
- **Rate Limiting**: The number of requests an IP can make within a specified timeframe is limited.
- **Suspicious IP Detection**: IPs that exceed the allowed threshold of requests are identified and marked as suspicious.
- **Bot Detection**: IPs that fail to pass a verification check are marked as bots.
- **Automatic Cleanup**: Inactive IPs are removed from the active list after a specified timeout.
- **Logging**: The status of active, suspected, and bot IPs is logged to the console.

## Approach

1. **Request Handling**:
   - `BaseHTTPRequestHandler` from Python's `http.server` module is used to handle incoming HTTP requests.
   - GET and POST requests are differentiated.

2. **IP Monitoring**:
   - Requests from each IP are tracked in the `active` dictionary, logging the number of requests and the last request time.
   - A `suspected` dictionary is used for IPs that exceed the request threshold but have not yet been marked as bots.
   - A `bot` set is maintained for IPs that are confirmed as bots.

3. **Rate Limiting**:
   - A maximum allowed number of requests (`maximum_allowed_requests`) within a certain period (60 seconds) is defined.
   - The number of requests in the last 60 seconds is checked to enforce rate limiting.

4. **Suspicious IP Detection**:
   - IPs that exceed the request threshold are moved to the `suspected` list.
   - A passcode verification form is provided for suspected IPs to prove they are not bots.

5. **Bot Detection**:
   - IPs are marked as bots if they fail the passcode verification multiple times.
   - Bot IPs are appended to a `bot.txt` file for logging.

6. **Automatic Cleanup**:
   - A background thread periodically removes inactive IPs from the `active` list if they have been inactive for a specified timeout (60 seconds).

## Usage

### Starting the Server

The server can be started by running the following command:

```bash
python your_script_name.py
```

### Making Requests

- **GET Requests**: Web browsers or HTTP clients can be used to make GET requests to the server:
  ```bash
  http://localhost:8080
  ```

- **POST Requests**: The passcode verification form provided by the server for suspected IPs can be submitted.

### Viewing Logs

The console output can be checked to view the status of active, suspected, and bot IPs, as well as other relevant logs.

## File Structure

- `your_script_name.py`: The main script containing the DDoS detection and prevention logic.
- `bot.txt`: A log file where bot IPs are recorded.

## Contributing

Feel free to fork this repository and contribute by submitting pull requests. For major changes, an issue should be opened first to discuss what changes are proposed.
