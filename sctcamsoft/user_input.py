"""Input client for slow control.
Terminal to type in commands, the output of which are displayed
in the output client to prevent blocking.
"""

import argparse
import socket
import shlex

import yaml

from sctcamsoft.slow_control_client import SlowControlClient

# Load configuration
parser = argparse.ArgumentParser()
parser.add_argument('config_file', help='Path to slow control config file')
parser.add_argument('commands_file', help='Path to slow control commands file')
args = parser.parse_args()

with open(args.config_file, 'r') as config_file:
    config = yaml.load(config_file)
server_host = config['user_interface']['host']
server_port = config['user_interface']['input_port']
header_length = config['user_interface']['header_length']

with open(args.commands_file, 'r') as commands_file:
    commands = yaml.load(commands_file)

sc_client = SlowControlClient(server_host, server_port,
                              None, header_length, commands)

# Start a terminal for user input
print("SCT Slow Control - Input")
print("Type 'startup' to prepare camera for operation (Operations Manual sec. "
        "5.1 and 5.2). When everything is connected and on, type 'start_HV' "
        "to turn on HV, and 'stop_HV' to turn it off. When done taking data, "
        "type 'shutdown' to prepare camera for shutdown (Manual sec. 6.1).")
# Identify self to server
while True:
    raw_user_input = input('> ')
    if raw_user_input in ['exit', 'q']:
        sc_client.close()
        break
    try:
        sc_client.send_command(raw_user_input)
    except (ValueError, IndexError) as e:
        print(e)
        continue
