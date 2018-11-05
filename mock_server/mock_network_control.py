# Control for camera networking

import os
import subprocess

from slow_control_classes import *
from random_signal import RandomSignal
from hardware_state_helpers import *

class NetworkController(DeviceController):

    def __init__(self, device, config):
        self.device = device
        try:
            self.timeout = int(config['timeout'])
        except KeyError:
            raise ConfigurationError(self.device, 'timeout',
                    "missing configuration parameter")
        except ValueError:
            raise ConfigurationError(self.device, 'timeout',
                    "must be an integer")

        hw_state = get_device_state(device)
        self._network_activity_sig = RandomSignal(
            hw_state['avg_packet_number'], 
            50 if hw_state['noisy_count'] else 0, 0)

    def execute_command(self, command):
        cmd = command.command
        update = None
        if cmd == "check_interface_activity":
            try:
                interface = command.args['interface']
            except KeyError:
                raise CommandArgumentError(self.device, cmd, 'interface',
                        "missing argument")
            if interface is None:
                raise CommandArgumentError(self.device, cmd, 'interface',
                        "argument not specified")
            
            num_packets = int(self._network_activity_sig.read())
            update = (self.device, interface, num_packets)
        else:
            raise CommandNameError(self.device, cmd)
        return update
