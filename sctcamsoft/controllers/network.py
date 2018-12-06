# Control for camera networking

__all__ = ['NetworkController',]

import os
import subprocess

from sctcamsoft.slow_control_classes import *

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

    def _construct_tcpdump_command(self, interface):
        cmd = ("timeout " + str(self.timeout) + " tcpdump -p -i " + interface
                + " 2>&1 | tail -2 | head -1 | awk '{print $1}'")
        return cmd

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
            tcpdump_command = self._construct_tcpdump_command(interface)
            # Return number of packets send over interface within timeout
            completed_process = subprocess.run(tcpdump_command, check=True,
                    stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                    encoding='ascii', shell=True)
            try:
                num_packets = int(completed_process.stdout)
            except ValueError:
                # tcpdump returned an error -> interface not connected
                num_packets = -1
            update = (self.device, interface, num_packets)
        else:
            raise CommandNameError(self.device, cmd)
        return update
