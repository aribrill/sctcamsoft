# Server for SCT Camera slow control

import argparse
from collections import namedtuple
import selectors
import socket
import threading
import time

import yaml

from slow_control_classes import DeviceCommand
from fan_control import FanController
from power_control import PowerController
import slow_control_pb2 as sc

Alert = namedtuple('Alert', ['device', 'variable', 'lower_limit',
    'upper_limit'])
UserCommand = namedtuple('Command', ['command', 'args'])

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
            self.user_command = UserCommand(user_command.command,
                    dict(user_command.args))
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
   
    def __init__(self, config, user_commands, devices):
        print("Slow Control Server")
        print("Initializing server...")
        self.alerts = []
        self.timers = []
        self.user_handler = UserHandler(config['User Interface'])
        self.update = {}
        self.user_commands = user_commands
        # For uniquely labeling messages; reset in each update
        self.message_count = 0
        print("Initializing devices:")
        self.device_controllers = {'server': self}
        for device, controller in devices.items():
            print("Initializing {}...".format(device))
            self.device_controllers[device] = controller(config[device])
        print("Initialization complete.")

    # Break down command into a list of device commands
    def _parse_user_command(self, user_command):
        
        # Combine command arguments from user input and prespecified values
        def get_command_args(args, user_input):
            cmd_args = {**args, **user_input} # User input overrides values
            # Check for missing args
            missing_args = [a for a in cmd_args if a is None]
            for arg in missing_args:
                print("Warning: no input or value for argument '{}' "
                            "specified".format(arg))
            # Check for extra args
            extra_args = list(set(cmd_args) - set(args))
            for arg in extra_args:
                print("Warning: extra argument '{}' specified".format(arg))
            return cmd_args

        cmd_def = self.user_commands[user_command.command]
        args = cmd_def.get('args', {})
        # Handle special case for setting a repeating command
        if '__command_args' in args:
            args.pop('__command_args')
            args.update(commands[args['command']].get('args', {}))
        user_input = user_command.args
        # Base case: one command for a particular device ("low level")
        if 'device' in cmd_def and 'command' in cmd_def:
            cmd_args = get_command_args(args, user_input)
            device_command = DeviceCommand(cmd_def['device'],
                    cmd_def['command'], cmd_args)
            return [device_command]
        # Recursive case: list of commands ("high level")
        elif 'command_list' in cmd_def:
            device_commands = []
            for list_index, command in enumerate(cmd_def['command_list']):
                sub_arg_names = {a: args[a]['arg'] for a in args 
                        if args[a]['list_index'] == list_index}
                sub_args = {sub_arg_names[a]: args[a]['value'] for a in
                        sub_arg_names}
                sub_user_input = {sub_arg_names[a]: user_input[a] for a in
                        sub_arg_names if a in user_input}
                cmd_args = get_command_args(sub_args, sub_user_input)
                user_subcommand = UserCommand(command, cmd_args)
                device_subcommands = self._parse_user_command(user_subcommand)
                device_commands.extend(device_subcommands)
            return device_commands
        else:
            print("Warning: command definition incorrectly specified! "
                    "Skipping command.")
            return []
    
    def _execute_device_command(self, device_command):
        command = device_command.command
        device_controller = self.device_controllers[device_command.device]
        device_update = None
        try:
            # Execute a device command
            if device_controller is not self:
                device_update = device_controller.execute_command(
                        device_command)
            # Execute a server command
            elif command == 'print_message':
                device_update = {'message'+str(self.message_count): device_command.args['message']}
                self.message_count += 1
            elif command == 'sleep':
                time.sleep(float(device_command.args['secs']))
            elif command == 'set_alert':
                self.alerts.append(Alert(device=device_command.args['device'],
                    variable=device_command.args['variable'],
                    lower_limit=float(device_command.args['lower_limit']),
                    upper_limit=float(device_command.args['upper_limit'])))
            elif command == 'set_repeating_command':
                repeat_args = {a: device_command.args[a] for a in 
                        device_command.args if a not in ['command', 'interval']}
                repeat_cmd = HighLevelCommand(
                        command=device_command.args['command'],
                        args=repeat_args)
                timer_index = len(self.timers)
                timer = {'passed': True, 'command': repeat_cmd}
                self.timers.append(timer)
                def start_timer():
                    self.timers[timer_index]['passed'] = True
                    threading.Timer(float(device_command.args['interval']),
                            start_timer).start()
                start_timer()
            elif command == '_process_timed_commands':
                for timer in self.timers:
                    if timer['passed']:
                        timer['passed'] = False
                        self._process_user_command(timer['command'])
        except Exception as e:
            raise
            
        return {device_command.device: device_update} if device_update else None

    def _process_update(self, update):
        if update is not None:
            for device, values in update.items():
                if device not in self.update:
                    self.update[device] = {}
                for key, value in values.items():
                    self.update[device][key] = value
    
    def _process_user_command(self, user_command):
        device_commands = self._parse_user_command(user_command)
        for device_command in device_commands:
            update = self._execute_device_command(device_command)
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
            self._execute_device_command(DeviceCommand(device='server',
                command='_process_timed_commands', args={}))
            # Check alerts and add any found to update
            self._check_alerts()
            # Send any updates to the user, and receive any commands
            user_command = self.user_handler.communicate_user(self.update)
            self.message_count = 0
            self.update = {}
            if user_command is not None:
                self._process_user_command(user_command)

parser = argparse.ArgumentParser()
parser.add_argument('config_file', help='Path to slow control config file')
parser.add_argument('commands_file', help='Path to slow control commands file')
args = parser.parse_args()

with open(args.config_file, 'r') as config_file:
    config = yaml.load(config_file)

with open(args.commands_file, 'r') as commands_file:
    user_commands = yaml.load(commands_file)

devices = {
        'fan': FanController,
        'power': PowerController
        }
server = SlowControlServer(config, user_commands, devices)

server.run_server()
