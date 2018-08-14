# Server for SCT Camera slow control

import argparse
from collections import namedtuple
from enum import Enum, auto
import selectors
import socket

import yaml

import slow_control_pb2 as sc

class State(Enum):
    READY = auto()
    ERROR = auto()

HighLevelCommand = namedtuple('HighLevelCommand', ['command', 'args'])
Command = namedtuple('Command', ['device', 'command', 'args'])

class UserHandler():

    def __init__(self, config):
        self.host = config['host']
        self.input_port = config['input_port']
        self.output_port = config['output_port']
        self.selector = selectors.DefaultSelector()
        self.user_command = None

        def add_socket(port, accept_fn):
            sock = socket.socket()
            sock.bind((self.host, port))
            sock.listen()
            sock.setblocking(False)
            self.selector.register(sock, selectors.EVENT_READ, accept_fn)

        add_socket(self.input_port, self._accept_input)
        add_socket(self.output_port, self._accept_output)

    def _accept_input(self, sock, mask):
        conn, addr = sock.accept()
        conn.setblocking(False)
        self.selector.register(conn, selectors.EVENT_READ, self._read)
    
    def _accept_output(self, sock, mask):
        conn, addr = sock.accept()
        conn.setblocking(False)
        self.selector.register(conn, selectors.EVENT_WRITE, self._write)

    def _read(self, conn, mask):
        serialized_message = conn.recv(1024)
        if serialized_message:
            user_command = sc.UserCommand()
            user_command.ParseFromString(serialized_message)
            self.user_command = HighLevelCommand(user_command.command,
                    user_command.args)
        else:
            self.selector.unregister(conn)
            conn.close()

    def _write(self, conn, mask):
        if self.user_update:
            user_update = sc.UserUpdate()
            for device in self.user_update:
                for key, val in self.user_update[device].items():
                    user_update.devices[device].updates[key] = val
            self.user_update = None
            message = user_update.SerializeToString() 
            conn.sendall(message)

    def communicate_user(self, update):
        self.user_command = None
        self.user_update = update
        for key, mask in self.selector.select(timeout=-1):
            callback = key.data
            callback(key.fileobj, mask)
        return self.user_command
        
class SlowControlServer():
   
    def __init__(self, config):
        self.state = State.READY
        self.auto_commands = []
        self.user_handler = UserHandler(config['User Interface'])
        self.device_controllers = {
                'server': self
                }
        self.update = {}
        self.high_level_commands = config['High Level Commands']

    def parse_high_level_command(self, high_level_command):
        # Get list of device commands with args assigned as specified
        device_command_defs = self.high_level_commands[
                high_level_command.command]['device_commands']
        device_commands = []
        for cmd_def in device_command_defs:
            cmd_args = {arg: high_level_command.args[arg] for arg in
                    cmd_def['args']}
            device_command = Command(cmd_def['device'], cmd_def['command'],
                    cmd_args)
            device_commands.append(device_command)
        return device_commands
    
    def execute_command(self, command):
        command_name = command.command
        device_controller = self.device_controllers[command.device]
        # Execute a device command
        if device_controller is not self:
            try:
                device_update = device_controller.execute_command(command)
            except Exception as e:
                self.state = State.ERROR
                print(e)
                device_update = None
        # Execute a server command
        elif command_name == 'set_number':
            self.number = command.args['number']
            device_update = {'number': self.number}
        return {command.device: device_update} if device_update else None

    def process_update(self, update):
        if update is not None:
            for device, values in update.items():
                if device not in self.update:
                    self.update[device] = {}
                for key, value in values.items():
                    self.update[device][key] = value
    
    def process_high_level_command(self, high_level_command):
        device_commands = self.parse_high_level_command(high_level_command)
        for command in device_commands:
            update = self.execute_command(command)
            self.process_update(update)

    def run_server(self):
        # Start server main loop
        while True:
            # Perform auto commands
            for auto_command in self.auto_commands:
                self.process_high_level_command(auto_command)
            # Send any updates to the user, and receive any commands
            user_command = self.user_handler.communicate_user(self.update)
            self.update = {}
            if user_command is not None:
                self.process_high_level_command(user_command)

parser = argparse.ArgumentParser()
parser.add_argument('config_file', help='Path to slow control config file')
args = parser.parse_args()

with open(args.config_file, 'r') as config_file:
    config = yaml.load(config_file)
server = SlowControlServer(config)

print("Slow Control Server")
server.run_server()
