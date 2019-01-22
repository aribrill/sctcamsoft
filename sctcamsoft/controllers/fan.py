# Slow control for fan

# Telnet protocol follows example at http://www.pythonforbeginners.com/code-snippets-source-code/python-using-telnet
# Another useful example: https://docs.python.org/2/library/telnetlib.html
# Telnet supported added to FAN class May 27 2018 by Justin Vandenbroucke
# Modified for DeviceController class and Python 3 Aug 14 2018 by Ari Brill

__all__ = ['FanController',]

import socket
import telnetlib
import time

from sctcamsoft.slow_control_classes import *

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
        self._ser = None

    def _open_connection(self):
        try:
            self._ser = telnetlib.Telnet(
                    self._telnet_settings['host'],
                    self._telnet_settings['port'],
                    self._telnet_settings['timeout'])
        except OSError:
            raise CommunicationError(self.device)

    def _close_connection(self):
        if self._ser is not None:
            self._ser.close()
        self._ser = None

    def _send_cmd(self, cmd):
        try:
            self._ser.write("{}\n".format(cmd).encode('ascii'))
            time.sleep(0.5)
            val = self._ser.read_until('\n'.encode('ascii'), timeout=1)
            val = val.decode('ascii')[:6] # strip non-numerical output
            return val
        except OSError:
            self._ser = None
            raise CommunicationError(self.device)

    def execute_command(self, command):
        cmd = command.command
        update = None
        if cmd == "open_connection":
            if self._ser is not None:
                raise CommandSequenceError(self.device, cmd, 
                        "Fan connection is already open, "
                        "close before reopening.")
            self._open_connection()
        elif cmd == "check_connection":
            update = (self.device, 'connected', int(self._ser is not None))
        elif self._ser is None:
            raise CommunicationError(self.device)
        elif cmd == "close_connection":
            self._close_connection()
        elif cmd == "turn_on":
            self._send_cmd("PWR ON")
            time.sleep(SLEEP_SECS)
        elif cmd == "turn_off":
            self._send_cmd("PWR OFF")
            time.sleep(SLEEP_SECS)
        elif cmd == "read_voltage":
            voltage = self._send_cmd("VREAD")
            update = (self.device, 'voltage', voltage)
        elif cmd == "read_current":
            current = self._send_cmd("IREAD")
            update = (self.device, 'current', current)
        else:
            raise CommandNameError(self.device, cmd)
        return update
