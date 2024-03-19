from flask import Flask, request
import subprocess
import threading
import time
import json

from consts import PORT

app = Flask(__name__)

HISTORY_FILE = 'unblock_history.json'

def get_history():
    try:
        with open(HISTORY_FILE, 'r') as file:
            return json.load(file)
    except FileNotFoundError:
        return {}

def update_history(history):
    with open(HISTORY_FILE, 'w') as file:
        json.dump(history, file)

def modify_hosts(action, domain):
    subprocess.run(["sudo", "hosts", action, domain])

def reblock_domain(domain, history):
    modify_hosts("enable", domain)
    update_history(history)

@app.route('/unblock', methods=['POST'])
def unblock_domain():
    data = request.json
    domain = data['domain']
    requested_duration = data['duration']
    duration = requested_duration
    history = get_history()

    # # Apply exponential backoff based on history
    # if domain in history:
    #     history[domain]['count'] += 1
    #     duration = requested_duration * (0.5 ** history[domain]['count'])
    # else:
    #     history[domain] = {'count': 1}
    #     duration = requested_duration

    modify_hosts("disable", domain)
    timer = threading.Timer(duration * 60, reblock_domain, args=[domain, history])
    timer.start()
    print(domain, requested_duration)
    return f"Unblocked {domain} for {duration} minutes."

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=PORT)

