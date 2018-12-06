__all__ = ['FanController',]

import socket
import telnetlib
import time

from sctcamsoft.slow_control_classes import *
from sctcamsoft.controllers.mock.random_signal import RandomSignal

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

        hw_state = config['mock']
        add_noise = hw_state['noisy_signal']

        self._isconnected = hw_state['is_connected']
        self._is_on = hw_state['fans_on']
        self._voltage_sig = RandomSignal(hw_state['voltage'], 0.7 if add_noise else 0)
        self._current_sig = RandomSignal(hw_state['current'], 0.5 if add_noise else 0)
        self._zero_sig =RandomSignal(0, 0.01 if add_noise else 0.0)

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
            time.sleep(SLEEP_SECS)
        elif cmd == "turn_off":
            self._is_on = False
            time.sleep(SLEEP_SECS)
        elif cmd == "read_voltage":
            if (self._is_on):
                voltage = self._voltage_sig.read()
            else: 
                voltage = self._zero_sig.read()
            update = (self.device, 'voltage', voltage)
        elif cmd == "read_current":
            if (self._is_on):
                current = self._current_sig.read() 
            else:
                current = self._zero_sig.read()
            update = (self.device, 'current', current)
        else:
            raise CommandNameError(self.device, cmd)
        return update
