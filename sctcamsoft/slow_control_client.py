__all__ = ['SlowControlClient',]

import socket
import shlex

import sctcamsoft.slow_control_pb2 as sc

class SlowControlClient():

    def __init__(self, host, server_input_port, 
                server_output_port, header_length, 
                commands):
        self._server_host = host
        self._server_input_port = server_input_port
        self._server_output_port = server_output_port
        self._header_length = header_length
        self._commands = commands

        self._send_cmd_sock = None
        self._recv_msg_sock = None
        self._connect_sockets()

    def _connect_sockets(self):
        if self._server_input_port is not None:
            self._send_cmd_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self._send_cmd_sock.connect((self._server_host, self._server_input_port))

        if self._server_output_port is not None:
            self._recv_msg_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self._recv_msg_sock.connect((self._server_host, self._server_output_port))

    def _parse_and_serialize_command(self, cmd_string):
        raw_user_input = shlex.split(cmd_string.strip())
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
        serialized_message = message.SerializeToString()
        header = "{{:0{}d}}".format(self._header_length).format(len(serialized_message))

        return header.encode() + serialized_message

    def can_send(self):
        return (self._server_input_port is not None 
                and self._commands is not None
                and self._send_cmd_sock is not None)

    def can_receive(self):
        return (self._server_output_port is not None
                and self._recv_msg_sock is not None)

    def send_command(self, cmd_string):
        if not self.can_send():
            raise RuntimeError('SC client is not configured to send, '
                               'yet a send method was called.')

        message = self._parse_and_serialize_command(cmd_string)
        self._send_cmd_sock.sendall(message)

    def recv_updates(self):
        if not self.can_receive():
            raise RuntimeError('SC client is not configured to receive, '
                               'yet a receive method was called.')

        header = self._recv_msg_sock.recv(self._header_length)
        if header:
            serialized_message = self._recv_msg_sock.recv(int(header))
            if serialized_message:
                user_update = sc.UserUpdate()
                user_update.ParseFromString(serialized_message)
                return user_update.updates
                
        return None
