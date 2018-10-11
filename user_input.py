"""Input client for slow control.
Terminal to type in commands, the output of which are displayed
in the output client to prevent blocking.
"""

import argparse
import socket

import yaml

import slow_control_pb2 as sc

# Load configuration
parser = argparse.ArgumentParser()
parser.add_argument('config_file', help='Path to slow control config file')
parser.add_argument('commands_file', help='Path to slow control commands file')
args = parser.parse_args()

with open(args.config_file, 'r') as config_file:
    config = yaml.load(config_file)
server_host = config['User Interface']['host']
server_port = config['User Interface']['input_port']

# Open a socket to the slow control server
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.connect((server_host, server_port))

with open(args.commands_file, 'r') as commands_file:
    commands = yaml.load(commands_file)

# Return a serialized message containing the UserCommand corresponding
# to the input entered by the user. If the command isn't valid, return None.
def parse_and_serialize_user_input(user_input):
    user_input = user_input.strip().split(' ')
    command = user_input[0]
    if command not in commands:
        raise ValueError("command '{}' not recognized".format(command))
    args = commands[command]['args']
    values = user_input[1:]
    if len(args) != len(values):
        raise IndexError("command '{}' requires {} arguments, {} given".format(
            command, len(args), len(values)))
    message = sc.UserCommand()
    message.command = command
    for arg, value in zip(args, values):
        message.args[arg] = value
    return message.SerializeToString()

# Start a terminal for user input
print("SCT Slow Control - Input")
# Identify self to server
while True:
    user_input = input('> ')
    if user_input in ['exit', 'q']:
        sock.close()
        break
    try:
        serialized_command = parse_and_serialize_user_input(user_input)
        sock.sendall(serialized_command)
    except (ValueError, IndexError) as e:
        print(e)
        continue
