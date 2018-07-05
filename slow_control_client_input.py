"""Input client for slow control.
Terminal to type in commands, the output of which are displayed
in the output client to prevent blocking.
"""

import configparser
import socket

import slow_control_pb2 as sc

# Return a MessageWrapper containing the UserCommand corresponding
# to the user-entered string. If the command isn't valid, return None.
def wrap_and_serialize_command(command):
    user_command = sc.UserCommand()
    if command == "status":
        user_command.command = sc.UserCommand.SERVER_STATUS
    else:
        return None
    message_wrapper = sc.MessageWrapper()
    message_wrapper.user_command.CopyFrom(user_command)
    return message_wrapper.SerializeToString()

# Load configuration
config = configparser.ConfigParser()
config.read('slow_control_config.ini')
server_host = config['Networking']['Host']
server_port = config['Networking'].getint('Port')

# Open a socket to the slow control server
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.connect((server_host, server_port))

# Start a terminal for user input
print("SCT Slow Control - Input")
while True:
    command = input('> ')
    if command in ['exit', 'q']:
        sock.close()
        break
    serialized_command = wrap_and_serialize_command(command)
    if not serialized_command:
        print("Command not recognized: {}".format(command))
        continue
    sock.sendall(serialized_command)
    #sock.sendall(serialized_command + bytes('\n', 'ascii'))
