# Server for SCT Camera slow control

import argparse
from collections import namedtuple
import selectors
import socket
import sys
import threading

import yaml

from slow_control_classes import *
from fan_control import FanController
from power_control import PowerController
import slow_control_pb2 as sc

Alert = namedtuple('Alert', ['device', 'variable', 'lower_limit',
    'upper_limit'])
UserCommand = namedtuple('UserCommand', ['command', 'args'])

class UserHandler():

    def __init__(self, config):
        self.host = config['host']
        self.input_port = config['input_port']
        self.output_port = config['output_port']
        self.selector = selectors.DefaultSelector()
        self.user_command = None

        def add_socket(port, accept_fn):
            sock = socket.socket()
            sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
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
            conn = key.fileobj
            try:
                callback(conn, mask)
            except ConnectionError as e:
                self.selector.unregister(conn)
                conn.close()
        return self.user_command
        
class ServerController(DeviceController):
   
    def __init__(self, config, user_commands, devices):
        print("Slow Control Server")
        print("Initializing server...")
        self.alerts = []
        self.timers = []
        self.user_handler = UserHandler(config['user_interface'])
        self.update = {}
        self.user_commands = user_commands
        try:
            self._validate_commands(self.user_commands)
        except ConfigurationError as e:
            print("Error: the command '{}' is incorrectly defined. "
                    "Shutting down.".format(str(e)))
            sys.exit()
        # For uniquely labeling messages; reset in each update
        self._message_count = 0
        self._error_count = 0
        print("Configuring devices:")
        self.device_controllers = {'server': self}
        for device, controller in devices.items():
            print("Configuring {}...".format(device))
            try:
                self.device_controllers[device] = controller(
                        config.get(device, {}))
            except ConfigurationError as e:
                print("Error: the configuration parameter '{}' for device "
                        "'{}' is missing or invalid. Shutting down.".format(
                            str(e), device))
                sys.exit()
        print("Configuration complete.")

    def _validate_commands(self, user_commands):
        for command_name, command_params in user_commands.items():
            # Low level or special commands
            if 'device' in command_params and 'command' in command_params:
                # Validate special commands
                if (command_params['device'] is None 
                        and command_params['command'] == 'enter_repeat_mode'):
                    for key in ['interval', 'n_executions',
                            'execute_immediately']:
                        if not key in command_params['args']:
                            raise ConfigurationError('enter_repeat_mode: args: '
                                    + key)
                continue
            # High level commands
            if 'command_list' in command_params:
                for arg, arg_keys in command_params.get('args', {}).items():
                    for key in ['index', 'arg']:
                        if not key in arg_keys:
                            raise ConfigurationError(command_name + ': args: '
                                    + arg + ': ' + key)
                continue
            raise ConfigurationError(command_name)

    # Break down user command into an unprocessed list of device commands
    # Recursively process nested high-level commands
    def _parse_user_command(self, user_command):
        
        # Combine command arguments from user input and prespecified values
        def get_command_args(args, user_input):
            cmd_args = {**args, **user_input} # User input overrides values
            # Check for missing args
            missing_args = [a for a in cmd_args if a is None]
            for arg in missing_args:
                raise CommandArgumentError('missing argument: {}'.format(arg))
            # Check for extra args
            extra_args = list(set(cmd_args) - set(args))
            for arg in extra_args:
                raise CommandArgumentError('extra argument: {}'.format(arg))
            return cmd_args

        cmd_def = self.user_commands[user_command.command]
        args = cmd_def.get('args', {})
        user_input = user_command.args
        # Base case: one command for a particular device ("low level")
        if 'device' in cmd_def and 'command' in cmd_def:
            cmd_args = get_command_args(args, user_input)
            device_command = DeviceCommand(cmd_def['device'],
                    cmd_def['command'], cmd_args)
            return [device_command]
        # Recursive case: list of commands ("high level")
        else: #'command_list' in cmd_def
            device_commands = []
            for index, command in enumerate(cmd_def['command_list']):
                sub_arg_names = {a: args[a]['arg'] for a in args 
                        if args[a]['index'] == index}
                sub_args = {sub_arg_names[a]: args[a]['val'] 
                        if 'val' in args[a] else None for a in sub_arg_names}
                sub_user_input = {sub_arg_names[a]: user_input[a] 
                        for a in sub_arg_names if a in user_input}
                cmd_args = get_command_args(sub_args, sub_user_input)
                user_subcommand = UserCommand(command, cmd_args)
                device_subcommands = self._parse_user_command(user_subcommand)
                device_commands.extend(device_subcommands)
            return device_commands
   
    def _execute_device_command_list(self, device_command_list):

        repeat_depth = 0
        repeat_cmds = []
        RepeatParams = namedtuple('RepeatParams', ['interval', 'n_executions',
            'execute_immediately'])
        for dc in device_command_list:
            # Begin mode to list commands to repeatedly execute later
            if dc.device is None and dc.command == 'enter_repeat_mode':
                if repeat_depth == 0: # This is the first nested repeat
                    n_executions = dc.args['n_executions']
                    if n_executions is not None:
                        n_executions = int(n_executions)
                    repeat_params = RepeatParams(
                            interval=float(dc.args['interval']),
                            n_executions=n_executions,
                            execute_immediately=dc.args['execute_immediately'])
                else:
                    repeat_cmds.append(dc)
                repeat_depth += 1
            # Exit this mode unless the exit is in a nested repeat mode
            elif dc.device is None and dc.command == 'exit_repeat_mode':
                repeat_depth -= 1
                # Set the commands for repeated execution
                if repeat_depth == 0:
                    timer = {'interval': repeat_params.interval,
                            'n_executions': repeat_params.n_executions,
                            'execute_immediately': repeat_params.execute_immediately,
                            'command_list': repeat_cmds}
                    timer['passed'] = timer['execute_immediately']
                    self.timers.append(timer)

                    def timer_fn(timer):
                        def start_timer():
                            timer['passed'] = True
                            n_executions = timer['n_executions']
                            if n_executions is None or n_executions > 1:
                                threading.Timer(timer['interval'],
                                        start_timer).start()
                        return start_timer

                    start_timer = timer_fn(timer)
                    threading.Timer(timer['interval'], start_timer).start()
                    repeat_cmds = []
                else: repeat_cmds.append(dc)
            # Add the command to the list for repeated execution
            elif repeat_depth > 0:
                repeat_cmds.append(dc)
            # Execute the command
            else:
                try: # Handling for all exceptions
                    try:
                        device_controller = self.device_controllers[dc.device]
                    except KeyError as e:
                        raise DeviceNameError("Warning: invalid device: "
                                "{}".format(dc.device))
                    try: # Handling for specific exceptions
                        device_update = device_controller.execute_command(dc)
                    except CommandNameError:
                        raise CommandNameError("Warning: invalid command "
                                "name: {}".format(dc.command))
                    except CommunicationError:
                        raise CommunicationError("Warning: cannot communicate "
                                "with {} controller".format(dc.device))
                except (CommandArgumentError, CommandNameError,
                        CommandSequenceError, CommunicationError,
                        DeviceNameError) as e:
                    device_update = {'server':
                            {'error_' + str(self._error_count): e}}
                    self._error_count += 1
                # Add device update to rest of the updates
                if device_update is not None:
                    for device, values in device_update.items():
                        if device not in self.update:
                            self.update[device] = {}
                        for key, value in values.items():
                            self.update[device][key] = value
    
    def execute_command(self, command):
        cmd = command.command
        update = None
        if cmd == 'print_message':
            message = command.args['message']
            if message is None:
                raise CommandArgumentError('must be string: message')
            update = {'message' + str(self._message_count): 
                    command.args['message']}
            self._message_count += 1
        elif cmd == 'set_alert':
            alert_arg_types = {'device': str, 'variable': str,
                    'lower_limit': float, 'upper_limit': float}
            alert_args = {}
            for arg, arg_type in alert_arg_types.items():
                try:
                    value = command.args[arg]
                except KeyError:
                    raise CommandArgumentError('missing argument {}'.format(
                        arg))
                if value is None:
                    raise CommandArgumentError('unspecified argument: '
                            '{}'.format(arg))
                try:
                    alert_args[arg] = arg_type(value)
                except TypeError:
                    raise CommandArgumentError('invalid type of argument: '
                            '{}'.format(arg))
            self.alerts.append(Alert(**alert_args))
        else:
            raise CommandNameError
        
        return {'server': update} if update else None

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
    
    def _execute_timed_commands(self):
        for timer in self.timers:
            if timer['n_executions'] is not None and timer['n_executions'] <= 0:
                continue
            if timer['passed']:
                timer['passed'] = False
                if timer['n_executions'] is not None:
                    timer['n_executions'] -= 1
                self._execute_device_command_list(timer['command_list'])

    def run_server(self):
        # Start server main loop
        while True:
            # Process any commands on an automatic timer
            self._execute_timed_commands()
            # Check alerts and add any found to update
            self._check_alerts()
            # Send an update to the user and receive a command (if any)
            user_command = self.user_handler.communicate_user(self.update)
            # Reset internal variables
            self.update = {}
            self._message_count = 0
            self._error_count = 0
            # Execute user command
            if user_command is not None:
                try:
                    device_command_list = self._parse_user_command(user_command)
                except CommandArgumentError:
                    continue
                self._execute_device_command_list(device_command_list)

parser = argparse.ArgumentParser()
parser.add_argument('config_file', help='Path to slow control config file')
parser.add_argument('commands_file', help='Path to slow control commands file')
args = parser.parse_args()

with open(args.config_file, 'r') as config_file:
    config = yaml.load(config_file)

with open(args.commands_file, 'r') as commands_file:
    user_commands = yaml.load(commands_file)

devices = {
#       'server': self --> automatically included
        'fan': FanController,
        'power': PowerController
        }
server = ServerController(config, user_commands, devices)

server.run_server()
