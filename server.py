# Server for SCT Camera slow control

import argparse
from collections import namedtuple
import selectors
import socket
import threading
import time

import yaml

from slow_control_classes import HighLevelCommand, Command
from fan_control import FanController
from power_control import PowerController
import slow_control_pb2 as sc

Alert = namedtuple('Alert', ['device', 'variable', 'lower_limit', 'upper_limit'])

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
                    user_update.devices[device].updates[str(key)] = str(val)
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
   
    def __init__(self, config, high_level_commands, devices):
        print("Slow Control Server")
        print("Initializing server...")
        self.alerts = []
        self.timers = []
        self.user_handler = UserHandler(config['User Interface'])
        self.update = {}
        self.high_level_commands = high_level_commands
        print("Initializing devices:")
        self.device_controllers = {'server': self}
        for device, controller in devices.items():
            print("Initializing {}...".format(device))
            self.device_controllers[device] = controller(config[device])

    def _parse_high_level_command(self, high_level_command):
        # Get list of device commands with args assigned as specified
        device_command_defs = self.high_level_commands[
                high_level_command.command]['device_commands']
        user_input = high_level_command.args
        device_commands = []
        for cmd_def in device_command_defs:
            cmd_args = {}
            for arg in cmd_def.get('args', []):
                if arg in user_input:
                    cmd_args[arg] = user_input[arg]
                else:
                    cmd_args[arg] = cmd_def['values'][arg]
            device_command = Command(cmd_def['device'], cmd_def['command'],
                    cmd_args)
            device_commands.append(device_command)
        return device_commands
    
    def _execute_command(self, command):
        cmd = command.command
        device_controller = self.device_controllers[command.device]
        device_update = None
        try:
            # Execute a device command
            if device_controller is not self:
                device_update = device_controller.execute_command(command)
            # Execute a server command
            elif cmd == 'print_message':
                device_update = {'message'+str(command.args['msg_num']): command.args['message']}
            elif cmd == 'sleep':
                time.sleep(float(command.args['secs']))
            elif cmd == 'set_alert':
                self.alerts.append(Alert(device=command.args['device'],
                    variable=command.args['variable'],
                    lower_limit=float(command.args['lower_limit']),
                    upper_limit=float(command.args['upper_limit'])))
            elif cmd == 'repeat_high_level_command':
                repeat_cmd = HighLevelCommand(
                        command=command.args['high_level_command'],
                        args={})
                timer_index = len(self.timers)
                timer = {'passed': True, 'command': repeat_cmd}
                self.timers.append(timer)
                def start_timer():
                    self.timers[timer_index]['passed'] = True
                    threading.Timer(float(command.args['interval']),
                            start_timer).start()
                start_timer()
            elif cmd == '_process_timed_commands':
                for timer in self.timers:
                    if timer['passed']:
                        timer['passed'] = False
                        self._process_high_level_command(timer['command'])
        except Exception as e:
            raise
            
        return {command.device: device_update} if device_update else None

    def _process_update(self, update):
        if update is not None:
            for device, values in update.items():
                if device not in self.update:
                    self.update[device] = {}
                for key, value in values.items():
                    self.update[device][key] = value
    
    def _process_high_level_command(self, high_level_command):
        device_commands = self._parse_high_level_command(high_level_command)
        for command in device_commands:
            update = self._execute_command(command)
            self._process_update(update)

    def _check_alerts(self):
        for i, alert in enumerate(self.alerts):
            alert_id = 'ALERT_{}'.format(i)
            try:
                alert_value = self.update[alert.device][alert.variable]
            except KeyError as e: # no value to check, skip it
                continue
            try:
                alert_value = float(alert_value)
            except ValueError as e:
                print("Warning: could not convert {} to float to check alert".format(alert_value))
                continue
            if not alert.lower_limit <= alert_value <= alert.upper_limit:
                self.update[alert_id] = {
                        'device': alert.device,
                        'variable': alert.variable,
                        'value': alert_value,
                        'lower_limit': alert.lower_limit,
                        'upper_limit': alert.upper_limit
                        }

    def run_server(self):
        # Start server main loop
        while True:
            # Process any commands on an automatic timer
            self._execute_command(Command(device='server',
                command='_process_timed_commands', args={}))
            # Check alerts and add any found to update
            self._check_alerts()
            # Send any updates to the user, and receive any commands
            user_command = self.user_handler.communicate_user(self.update)
            self.update = {}
            if user_command is not None:
                self._process_high_level_command(user_command)

parser = argparse.ArgumentParser()
parser.add_argument('config_file', help='Path to slow control config file')
parser.add_argument('commands_file', help='Path to slow control commands file')
args = parser.parse_args()

with open(args.config_file, 'r') as config_file:
    config = yaml.load(config_file)

with open(args.commands_file, 'r') as commands_file:
    high_level_commands = yaml.load(commands_file)

devices = {
        'fan': FanController,
        'power': PowerController
        }
server = SlowControlServer(config, high_level_commands, devices)

server.run_server()
