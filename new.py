from flask import FLask, request, jsonify, redirect, url_for, render_template_string
import threading 
import logging
import time

app = Flask(__name__)

# Configuration
INACTIVITY_THRESHOLD = 60
REQUEST_THRESHOLD = 10
REQUEST_INTERVAL = 60

# Data Structures
ip_request_count = {}
ip_last_access_time = {}
suspected_ips = set()
confirm_ips = set()
lock = threading.Lock()
total_request_count = 0

# Passcode for verification
PASSCODE = 'human'

def reset_request_count():

