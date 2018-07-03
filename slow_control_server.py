"""Server for slow control for the SCT camera.
Initialize and run a main loop over connections to each instrument for
control and monitoring; the database for logging; and any number of user
interfaces, which may be either command-line or graphical interfaces for
input or read-only monitors.
"""

import configparser
import socketserver
import threading

import slow_control_pb2 as sc

# Load server configuration
config = configparser.ConfigParser()
config.read('slow_control_config.ini')

# Define status of the server, loading from the configuration file as needed
server_status = sc.ServerStatus()
server_status.state = sc.ServerStatus.READY
server_status.host = config['Networking']['Host']
server_status.port = config['Networking'].getint('Port')

# Set up the server
class ServerHandler(socketserver.StreamRequestHandler):

    def handle(self):
        # self.rfile and self.wfile are file-like objects created by
        # the handler to read from and write to the client
        while True:
            # Read the message
            serialized_message = self.rfile.readline().strip()
            # If message is empty, close the connection
            if not serialized_message: return
            # Otherwise, parse it
            message_wrapper = sc.MessageWrapper()
            message_wrapper.ParseFromString(serialized_message)
            message_type = message_wrapper.type
            # Take action depending on the message type and contents
            if message_type == sc.MessageWrapper.USER_COMMAND:
                command = message_wrapper.user_command.command
                if command == sc.UserCommand.SERVER_STATUS:
                    #self.wfile.write(server_status.SerializeToString())
                    print(server_status)

class ThreadedTCPServer(socketserver.ThreadingMixIn, socketserver.TCPServer):
    pass

# Start up and run the server
with ThreadedTCPServer((server_status.host, server_status.port),
        ServerHandler) as server:
    server.serve_forever()
