"""Server for slow control for the SCT camera.
Initialize and run a main loop over connections to each instrument for
control and monitoring; the database for logging; and any number of user
interfaces, which may be either command-line or graphical interfaces for
input or read-only monitors.
"""

import socketserver

# Settings
HOST = "thinkpad"
PORT = 31415

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
with ThreadedTCPServer((HOST, PORT), ServerHandler) as server:
    server.serve_forever()

# Start main loop
#while True:
    # Read new messages
    # Execute each message
