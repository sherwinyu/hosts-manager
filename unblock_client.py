#!/usr/bin/env python3

import getpass
import os
import requests
import subprocess

from consts import PORT

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
    process = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    print(f'Starting server on port {PORT}')

def unblock_domain(domain, duration):
    url = f'http://localhost:{PORT}/unblock'
    data = {'domain': domain, 'duration': duration}
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
    process = subprocess.Popen(['fzf', '-m', '--height=20'], stdin=subprocess.PIPE, stdout=subprocess.PIPE, text=True)
    stdout, _ = process.communicate('\n'.join(domains))
    return stdout.strip()

# Example usage
def execute():
    enabled_domains = get_enabled_domains()
    selected_domains = fuzzy_select_domain(enabled_domains).split('\n')
    print(selected_domains)
    duration = int(input('How many minutes? [3]') or "3")
    for domain in selected_domains:
        unblock_domain(domain, duration)


if __name__ == "__main__":
    if not is_server_running():
        print('Server is not running.')
        start_server()
    execute()

