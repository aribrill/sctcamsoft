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

        # Add the connection to the list of connections
        connection = server_status.connections.add()
        connection.client_type = sc.Connection.UNKNOWN
        connection.status = sc.Connection.OPEN
        connection.thread_id = threading.get_ident()

        # Read and respond to messages from the connection until it's closed
        while True:
            # Read the message
            try:
                serialized_message = self.request.recv(1024)
                if not serialized_message: raise EOFError
            except (ConnectionResetError, EOFError):
                # If connection reset or message empty, close the connection
                connection.status = sc.Connection.CLOSED
                return
            # Otherwise, parse it
            message_wrapper = sc.MessageWrapper()
            message_wrapper.ParseFromString(serialized_message)
            wrapped_message = message_wrapper.WhichOneof('wrapped_message')
            print(wrapped_message)
            # Take action depending on the message type and contents
            if wrapped_message == 'user_command':
                command = message_wrapper.user_command.command
                if command == sc.UserCommand.SERVER_STATUS:
                    #self.request.sendall(server_status.SerializeToString())
                    print(server_status)

class ThreadedTCPServer(socketserver.ThreadingMixIn, socketserver.TCPServer):
    pass

# Start up and run the server
with ThreadedTCPServer((server_status.host, server_status.port),
        ServerHandler) as server:
    server.serve_forever()
