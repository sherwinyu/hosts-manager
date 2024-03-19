#!/usr/bin/env python3
import os
import requests
import subprocess

from consts import PORT

def is_server_running():
    # Check if the server is running (e.g., by checking if port 5000 is in use)
    result = subprocess.run(['lsof', '-i', f':{PORT}'], capture_output=True, text=True)
    return bool(result.stdout)

def start_server():
    # Get the directory of the current script
    script_dir = os.path.dirname(os.path.realpath(__file__))
    # Construct the path to the server script
    server_script_path = os.path.join(script_dir, 'unblock_server.py')
    # Start the server using sudo
    subprocess.Popen(['sudo', 'python3', server_script_path])
    print('Starting server on port f{PORT}')

def unblock_domain(domain, duration):
    url = f'http://localhost:{PORT}/unblock'
    data = {'domain': domain, 'duration': duration}
    response = requests.post(url, json=data)
    print(response.text)

def get_enabled_domains():
    # Run the 'hosts enabled' command and capture the output
    result = subprocess.run(['hosts', 'enabled'], capture_output=True, text=True)
    return [line.split('\t')[1].strip() for line in result.stdout.splitlines()]

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
    duration = int(input('How many minutes? ') or "3")
    for domain in selected_domains:
        unblock_domain(domain, duration)


if __name__ == "__main__":
    if not is_server_running():
        print('Server is not running.')
        start_server()
    execute()

