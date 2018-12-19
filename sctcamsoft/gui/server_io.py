import socket
import shlex
import yaml

from sctcamsoft.slow_control_client import SlowControlClient
from PyQt5.QtCore import QThread, pyqtSignal, pyqtSlot

class ServerIO(QThread):

    on_update = pyqtSignal(object)

    def __init__(self, host, server_input_port, 
                 server_output_port, header_length, commands):
        QThread.__init__(self)

        self._sc_client = SlowControlClient(host, server_input_port,
                                            server_output_port, header_length,
                                            commands)

    def run(self):
        while True:
            try:
                updates = self._sc_client.recv_updates()
                if updates is not None:
                    for update in updates:
                        self.on_update.emit(update)
            except (socket.error, ConnectionError):
                print('Connection to server lost.')
                self.sleep(5)

    @pyqtSlot(str)
    def send_command(self, command):
        try:
            self._sc_client.send_command(command)
        except (socket.error, ConnectionError):
            print('Error communicating with server.')
            self.sleep(5)
