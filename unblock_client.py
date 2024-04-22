#!/usr/bin/env python3

import getpass
import os
import requests
import subprocess

from consts import PORT

from lib import parse_time_format, setup_logging

def is_server_running():
    try:
        response = requests.get(f'http://localhost:{PORT}/')
        return bool(response.status_code)
    except requests.exceptions.ConnectionError:
        return False

def start_server():
    # Get the directory of the current script
    script_dir = os.path.dirname(os.path.realpath(__file__))
    # Construct the path to the server script
    server_script_path = os.path.join(script_dir, 'unblock_server.py')

    # Start the server using sudo
    password = getpass.getpass("Enter sudo password: ").replace("'", "\\'").replace(";", "\\;")

    # # Escape single quotes in the password
    # escaped_password = password.replace("'", "'\\''")

    command = f'echo {password} | sudo -S python3 {server_script_path}'
    print(f'Starting server on port {PORT}')
    try:
        # Start the server as a background process
        process = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

        # Give the server a little time to start up and encounter any immediate errors
        time.sleep(5)  # Sleep time could be adjusted based on how quickly the server should start

        # Check if the process is still running
        if process.poll() is not None:  # If poll() returns a value, the process has terminated
            stdout, stderr = process.communicate()
            print(f"Error: Server failed to start. Exit code: {process.returncode}")
            print(f"Standard Error Output: {stderr.decode()}")
        else:
            print("Server started successfully and is running in the background.")

    except Exception as e:
        print(f"An exception occurred when trying to start the server: {e}")




def unblock_domain(domain, duration_string):
    url = f'http://localhost:{PORT}/unblock'
    data = {'domain': domain, 'duration_string': duration_string}
    response = requests.post(url, json=data)
    print(response.text)

def get_enabled_domains():
    # Run the 'hosts enabled' command and capture the output
    result = subprocess.run(['hosts', 'enabled'], capture_output=True, text=True)
    blacklist = set(['broadcasthost', 'localhost'])
    domains = [line.split('\t')[1].strip() for line in result.stdout.splitlines()]
    return [d for d in domains if d and d not in blacklist]

def fuzzy_select_domain(domains):
    # Run 'fzf' with the list of domains as input
    process = subprocess.Popen(['fzf', '-m', '--height=20', '--bind=ctrl-t:toggle-all'], stdin=subprocess.PIPE, stdout=subprocess.PIPE, text=True)
    stdout, _ = process.communicate('\n'.join(domains))
    return stdout.strip()


# Example usage
def execute():
    enabled_domains = get_enabled_domains()
    selected_domains = fuzzy_select_domain(enabled_domains).split('\n')
    print(selected_domains)
    parsed_duration = None
    while parsed_duration is None:
        parsed_duration = parse_time_format(input('How many minutes? [3m] (for seconds, append s e.g. 50s)'))

    for domain in selected_domains:
        unblock_domain(domain, str(parsed_duration[0]) + parsed_duration[1])

def log(msg):
    app.logger.info(msg)

if __name__ == "__main__":
    logger = setup_logging('client.log')
    if not is_server_running():
        log('Server is not running. Exiting')
    execute()

