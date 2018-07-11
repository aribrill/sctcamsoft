"""Output client for slow control.
Terminal to display the output of commands corresponding to inputs
given in the input client to prevent blocking.
"""

import configparser
import socket

import slow_control_pb2 as sc

# Load configuration
config = configparser.ConfigParser()
config.read('slow_control_config.ini')
server_host = config['Networking']['Host']
server_port = config['Networking'].getint('Port')

# Open a socket to the slow control server
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.connect((server_host, server_port))

# Start a terminal for user input
print("SCT Slow Control - Output")
message_wrapper = sc.MessageWrapper()
message_wrapper.client_type = sc.CLIENT_USER_OUTPUT
sock.sendall(message_wrapper.SerializeToString())
while True:
    # Parse the incoming message
    serialized_message = sock.recv(1024)
    message_wrapper = sc.MessageWrapper()
    message_wrapper.ParseFromString(serialized_message)
    wrapped_message = message_wrapper.WhichOneof('wrapped_message')
    if wrapped_message == 'server_status':
        print(message_wrapper.server_status)
