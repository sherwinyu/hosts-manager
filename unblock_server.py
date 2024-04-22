from flask import Flask, request
import datetime

import sys
import os
import subprocess
import threading
import logging
from logging.handlers import RotatingFileHandler
import time
import json

from consts import PORT
from lib import parse_time_format, setup_logging, restart_application


app = Flask(__name__)
script_dir = os.path.dirname(os.path.realpath(__file__))
log_path = os.path.join(script_dir, 'server.log')
app.logger = setup_logging(log_path)

def log(msg):
    app.logger.info(msg)

def modify_hosts(action, domain):
    log(f'### ### sudo hosts {action} {domain}')
    subprocess.run(["sudo", "hosts", action, domain])

def reblock_domain(domain, duration_string, orig_ts, unblock_counter):
    log(f'### Reblock {unblock_counter}: {domain} {duration_string} {orig_ts}')
    modify_hosts("enable", domain)
    restart_application('Arc')

unblock_counter = 0

@app.route('/unblock', methods=['POST'])
def unblock_domain():
    global unblock_counter
    data = request.json
    domain = data['domain']
    duration_string = data['duration_string']
    parsed = parse_time_format(duration_string)
    if not parsed:
        abort(400, description="Invalid duration format")  # Raise a 400 Bad Request error with a custom message

    duration = convert_to_seconds(parsed)

    orig_ts = datetime.datetime.now().strftime('%H:%M:%S')  # Corrected format '%H:%m:%S' to '%H:%M:%S'

    modify_hosts("disable", domain)
    log(f'### Unblock {unblock_counter}: {domain} {duration_string} {orig_ts}')
    timer = threading.Timer(duration, reblock_domain, args=[domain, duration_string, orig_ts, unblock_counter])
    timer.start()
    unblock_counter += 1
    return f"Unblocked {domain} for {duration_string}"

def convert_to_seconds(time_tuple):
    number, unit = time_tuple
    if unit == 'm':
        return number * 60  # Convert minutes to seconds
    elif unit == 's':
        return number      # Already in seconds
    else:
        raise ValueError("Invalid unit: must be 'm' or 's'")

def check_root():
    if os.geteuid() != 0:
        log("Server must be run as root")
        sys.exit(1)

if __name__ == '__main__':
    check_root()


    log(f' ')
    log(f'################################# ')
    log(f'## Server starting on port {PORT}')
    log(f'################################# ')
    app.run(debug=True, host='0.0.0.0', port=PORT)
