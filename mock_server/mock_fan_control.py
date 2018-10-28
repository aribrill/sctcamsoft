import sys
sys.path.append("..")

import socket
import telnetlib
import time

from slow_control_classes import *

SLEEP_SECS = 3

class FanController(DeviceController):

    def __init__(self, device, config):
        self.device = device
        self._telnet_settings = {'host': None, 'port': None, 'timeout': None}
        for setting in self._telnet_settings:
            try:
                self._telnet_settings[setting] = config[setting]
            except KeyError:
                raise ConfigurationError(self.device, setting,
                        "missing configuration parameter")
        
        try:
            if self._telnet_settings['timeout'] is not None:
                self._telnet_settings['timeout'] = float(
                        self._telnet_settings['timeout'])
        except ValueError:
            raise ConfigurationError(self.device, 'timeout',
                    "must be a number or None")


        self._isconnected = False
        self._is_on = False
        self._voltage = -1
        self._current = -1

    def _open_connection(self):
        self._isconnected = True

    def _close_connection(self):
        self._isconnected = False

    def execute_command(self, command):
        cmd = command.command
        update = None
        if cmd == "open_connection":
            if self._isconnected == True:
                raise CommandSequenceError(self.device, cmd, 
                        "Fan connection is already open, "
                        "close before reopening.")
            self._open_connection()
        elif self._isconnected == False:
            raise CommunicationError(self.device)
        elif cmd == "close_connection":
            self._close_connection()
        elif cmd == "check_connection":
            update = (self.device, 'connected', int(self._isconnected))
        elif cmd == "turn_on":
            self._is_on = True
            self._voltage = 12.0
            self._current = 2.0
            time.sleep(SLEEP_SECS)
        elif cmd == "turn_off":
            self._is_on = False
            self._voltage = 0.0
            self._current = 0.0
            time.sleep(SLEEP_SECS)
        elif cmd == "read_voltage":
            voltage = self._voltage
            update = (self.device, 'voltage', voltage)
        elif cmd == "read_current":
            current = self._current
            update = (self.device, 'current', current)
        else:
            raise CommandNameError(self.device, cmd)
        return update
