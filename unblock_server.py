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

app = Flask(__name__)

# Set up logging
script_dir = os.path.dirname(os.path.realpath(__file__))
log_path = os.path.join(script_dir, 'server.log')

# Redirect stderr to the log file
log_file = open(log_path, 'a')
sys.stderr = log_file

handler = RotatingFileHandler(log_path, maxBytes=1000000, backupCount=1)
handler.setLevel(logging.INFO)
handler.setFormatter(logging.Formatter('[%(asctime)s] %(module)s: %(message)s'))
app.logger.addHandler(handler)
app.logger.setLevel(logging.INFO)

def log(msg):
    cur_ts = datetime.datetime.now().strftime('%H:%m:%S')
    print(cur_ts + ' ' + msg)

def modify_hosts(action, domain):
    log(f'### ### sudo hosts {action} {domain}')
    subprocess.run(["sudo", "hosts", action, domain])

def reblock_domain(domain, requested_duration, orig_ts, unblock_counter):
    log(f'### Reblock {unblock_counter}: {domain} {requested_duration} {orig_ts}')
    modify_hosts("enable", domain)

unblock_counter = 0

@app.route('/unblock', methods=['POST'])
def unblock_domain():
    global unblock_counter
    data = request.json
    domain = data['domain']
    requested_duration = data['duration']
    duration = requested_duration
    orig_ts = datetime.datetime.now().strftime('%H:%m:%S')

    modify_hosts("disable", domain)
    log(f'### Unblock {unblock_counter}: {domain} {requested_duration} {orig_ts}')
    timer = threading.Timer(duration * 3, reblock_domain, args=[domain, requested_duration, orig_ts, unblock_counter])
    timer.start()
    unblock_counter += 1
    return f"Unblocked {domain} for {duration} minutes."

if __name__ == '__main__':
    log(f' ')
    log(f'################################# ')
    log(f'## Server starting on port {PORT}')
    log(f'################################# ')
    app.run(host='0.0.0.0', port=PORT)
