"""Server for slow control for the SCT camera.
Initialize and run a main loop over connections to each instrument for
control and monitoring; the database for logging; and any number of user
interfaces, which may be either command-line or graphical interfaces for
input or read-only monitors.
"""

import configparser
import socketserver

# Load configuration
config = configparser.ConfigParser()
config.read('slow_control_config.ini')
host = config['Networking']['Host']
port = config['Networking'].getint('Port')

# Start up the server
class ServerHandler(socketserver.StreamRequestHandler):

    def handle(self):
        # self.rfile and self.wfile are file-like objects created by
        # the handler to read from and write to the client
        while True:
            self.message = self.rfile.readline().strip()
            if not self.message: return
            print("{} wrote:".format(self.client_address[0]))
            print(self.message)
            self.wfile.write(self.message.upper())

class ThreadedTCPServer(socketserver.ThreadingMixIn, socketserver.TCPServer):
    pass

# Start up and run the server
with ThreadedTCPServer((host, port), ServerHandler) as server:
    server.serve_forever()
