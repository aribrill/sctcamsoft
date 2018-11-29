import socket
import shlex
import yaml

import slow_control_pb2 as sc
from PyQt5.QtCore import QThread, pyqtSignal, pyqtSlot

class ServerIO(QThread):

    on_update = pyqtSignal(object)

    def __init__(self, host, server_input_port, 
                 server_output_port, commands):
        QThread.__init__(self)

        self._host = host
        self._send_cmd_port = server_input_port
        self._recv_update_port = server_output_port

        self.attempt_connect_send()
        self.attempt_connect_recv()

        self._commands = commands

    def attempt_connect_send(self):
        self._send_cmd_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._send_cmd_sock.connect((self._host, self._send_cmd_port))

    def attempt_connect_recv(self):
        self._recv_update_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._recv_update_sock.connect((self._host, self._recv_update_port))

    def run(self):
        while True:
            try:
                serialized_message = self._recv_update_sock.recv(1024)
                if serialized_message:
                    user_update = sc.UserUpdate()
                    user_update.ParseFromString(serialized_message)
                    for update in user_update.updates:
                        if (update.device == 'ALERT'):
                            print("ALERT: {}".format(update.variable))
                        self.on_update.emit(update)
            except (socket.error, ConnectionError):
                print('Connection to server lost.')
                self.sleep(5)
                # print('Attempting to reconnect to rcv socket.')
                # self.attempt_connect_recv()

    @pyqtSlot(str)
    def send_command(self, command):
        raw_user_input = shlex.split(command.strip())
        command = raw_user_input[0]
        user_input = raw_user_input[1:]

        if command not in self._commands:
            raise ValueError("command '{}' not recognized".format(command))
        
        args = self._commands[command].get('args', {})
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
            
        serialized_command = message.SerializeToString()

        try:
            self._send_cmd_sock.sendall(serialized_command)
        except (socket.error, ConnectionError):
            print('Error communicating with server.')
            self.sleep(5)
            # print('Attempting to reconnect to send_cmd socket.')
            # print('cmd will not be automatically resent.')
            # self.attempt_connect_send()
