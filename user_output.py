"""Output client for slow control.
Terminal to display the output of commands corresponding to inputs
given in the input client to prevent blocking.
"""

import argparse
import socket

import yaml

import slow_control_pb2 as sc

# Load configuration
parser = argparse.ArgumentParser()
parser.add_argument('config_file', help='Path to slow control config file')
args = parser.parse_args()

with open(args.config_file, 'r') as config_file:
    config = yaml.load(config_file)
server_host = config['User Interface']['host']
server_port = config['User Interface']['output_port']

# Open a socket to the slow control server
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.connect((server_host, server_port))

# Start a terminal for user input
print("SCT Slow Control - Output")
while True:
    # Parse the incoming message
    serialized_message = sock.recv(1024)
    if serialized_message:
        user_update = sc.UserUpdate()
        user_update.ParseFromString(serialized_message)
        for device in user_update.devices:
            for key in sorted(user_update.devices[device].updates):
                value = user_update.devices[device].updates[key]
                print("{}: {}: {}".format(device, key, value))
