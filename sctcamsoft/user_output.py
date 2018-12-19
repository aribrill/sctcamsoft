"""Output client for slow control.
Terminal to display the output of commands corresponding to inputs
given in the input client to prevent blocking.
"""

import argparse
import socket

import yaml

from sctcamsoft.slow_control_client import SlowControlClient

# Load configuration
parser = argparse.ArgumentParser()
parser.add_argument('config_file', help='Path to slow control config file')
args = parser.parse_args()

with open(args.config_file, 'r') as config_file:
    config = yaml.load(config_file)
server_host = config['user_interface']['host']
server_port = config['user_interface']['output_port']
header_length = config['user_interface']['header_length']

sc_client = SlowControlClient(server_host, None, server_port, 
                              header_length, None)

# Start a terminal for user input
print("SCT Slow Control - Output")
while True:
    updates = sc_client.recv_updates()
    if updates is not None:
        for device, variable, value in updates:
            print("{}: {}: {}".format(device, variable, value))
