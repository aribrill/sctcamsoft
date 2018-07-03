"""Server for slow control for the SCT camera.
Initialize and run a main loop over connections to each instrument for
control and monitoring; the database for logging; and any number of user
interfaces, which may be either command-line or graphical interfaces for
input or read-only monitors.
"""

import configparser
import socketserver

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
            self.message = self.rfile.readline().strip()
            # If message is empty, close the connection
            if not self.message: return
            # If message is "status", send the status
            if self.message == b"status":
                print(server_status)
            #self.wfile.write(server_state.name.encode())

class ThreadedTCPServer(socketserver.ThreadingMixIn, socketserver.TCPServer):
    pass

# Start up and run the server
with ThreadedTCPServer((server_status.host, server_status.port),
        ServerHandler) as server:
    server.serve_forever()
