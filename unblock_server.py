from flask import Flask, request

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
handler.setFormatter(logging.Formatter('[%(asctime)s] %(levelname)s in %(module)s: %(message)s'))
app.logger.addHandler(handler)
app.logger.setLevel(logging.INFO)



HISTORY_FILE = 'unblock_history.json'

def get_history():
    try:
        with open(HISTORY_FILE, 'r') as file:
            return json.load(file)
    except FileNotFoundError:
        return {}

def modify_hosts(action, domain):
    subprocess.run(["sudo", "hosts", action, domain])

def reblock_domain(domain, requested_duration):
    app.logger.info(f'Reblock {domain} {requested_duration}')
    modify_hosts("enable", domain)

@app.route('/unblock', methods=['POST'])
def unblock_domain():
    data = request.json
    domain = data['domain']
    requested_duration = data['duration']
    duration = requested_duration

    modify_hosts("disable", domain)
    timer = threading.Timer(duration * 3, reblock_domain, args=[domain, requested_duration])
    timer.start()
    app.logger.info(f'/unblock {domain} {requested_duration}')
    return f"Unblocked {domain} for {duration} minutes."

if __name__ == '__main__':
    app.logger.info(f'Server starting on port {PORT}')
    app.run(host='0.0.0.0', port=PORT)
