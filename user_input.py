"""Input client for slow control.
Terminal to type in commands, the output of which are displayed
in the output client to prevent blocking.
"""

import argparse
import socket
import shlex

import yaml

import slow_control_pb2 as sc

# Load configuration
parser = argparse.ArgumentParser()
parser.add_argument('config_file', help='Path to slow control config file')
parser.add_argument('commands_file', help='Path to slow control commands file')
args = parser.parse_args()

with open(args.config_file, 'r') as config_file:
    config = yaml.load(config_file)
server_host = config['user_interface']['host']
server_port = config['user_interface']['input_port']

# Open a socket to the slow control server
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.connect((server_host, server_port))

with open(args.commands_file, 'r') as commands_file:
    commands = yaml.load(commands_file)

# Return a serialized message containing the UserCommand corresponding
# to the input entered by the user. If the command isn't valid, return None.
def parse_and_serialize_user_input(raw_user_input):
    raw_user_input = shlex.split(raw_user_input.strip())
    command = raw_user_input[0]
    user_input = raw_user_input[1:]
    if command not in commands:
        raise ValueError("command '{}' not recognized".format(command))
    args = commands[command].get('args', {})
    unspecified_args = [a for a in args if args[a] is None 
            or isinstance(a, dict) and args[a].get('value') is None]
    if len(user_input) == len(args):
        user_args = args
    elif len(user_input) == len(unspecified_args):
        user_args = unspecified_args
    else:
        raise IndexError("command '{}' requires {} arguments, {} given".format(
            command, len(args), len(user_input)))
    message = sc.UserCommand()
    message.command = command
    for user_arg, input_value in zip(user_args, user_input):
        message.args[user_arg] = input_value
    return message.SerializeToString()

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
        sock.close()
        break
    try:
        serialized_command = parse_and_serialize_user_input(raw_user_input)
        sock.sendall(serialized_command)
    except (ValueError, IndexError) as e:
        print(e)
        continue
