# Slow control for fan

# Telnet protocol follows example at http://www.pythonforbeginners.com/code-snippets-source-code/python-using-telnet
# Another useful example: https://docs.python.org/2/library/telnetlib.html
# protocol provided to FAN constructor should be 'serial' or (default) 'telnet'
# Telnet supported added May 27 2018 by Justin Vandenbroucke
# Modified for DeviceController class and Python 3 Aug 14 2018 by Ari Brill

import socket
import telnetlib
import time

import serial

from slow_control_classes import Command, DeviceController

class FanController(DeviceController):

    def __init__(self, config):
        self._protocol = config.get('protocol', 'telnet')
        self._ser = None
        self._open_connection()
        if not self.is_ready():
            print("Warning: fan control not set up")

    def _open_connection(self):
        if self._ser is not None:
            print("Warning: connection to fan is already open, close before "
                    "reopening.")
            return 
        try:
            if self._protocol == 'serial':
                self._ser = serial.Serial(port='/dev/ttyACM0',
                        baudrate=115200,
                        bytesize=8,
                        parity='N',
                        stopbits=1)
            elif self._protocol == 'telnet':
                host = config['telnet_host']
                port = config['telnet_port']
                timeout = config.get('telnet_timeout', None)
                if timeout is None:
                    self._ser = telnetlib.Telnet(host, port)
                else:
                    self._ser = telnetlib.Telnet(host, port, timeout)
            else:
                raise ValueError("ERROR: Unknown protocol '{}'".format(
                    self._protocol))
        except socket.timeout as e:
            print("WARNING: Could not connect to fan")
        except ConnectionRefusedError as e:
            print("WARNING: Connection refused")
        except OSError as e:
            print("WARNING: Camera fan power supply unavailable")

    def _close_connection(self):
        if self._ser is not None:
            self._ser.close()
        self._ser = None

    def _send_cmd(self, cmd):
        self._ser.write("{}\n".format(cmd).encode('ascii'))
        time.sleep(0.5)
        val = self._ser.read_until('\n'.encode('ascii'), timeout=1)
        val = val.decode('ascii')[:6] # strip non-numerical output
        return val

    def execute_command(self, command):
        cmd = command.command
        update = None
        if not self.is_ready():
            print("Warning: skipping command, fan is not ready")
            return update
        if cmd == "open_connection":
            self._open_connection()
        elif cmd == "close_connection":
            self._close_connection()
        elif cmd == "turn_on":
            self._send_cmd("PWR ON")
        elif cmd == "turn_off":
            self._send_cmd("PWR OFF")
        elif cmd == "read_voltage":
            voltage = self._send_cmd("VREAD")
            update = {'voltage': voltage}
        elif cmd == "read_current":
            current = self._send_cmd("IREAD")
            update = {'current': current}
        else:
            raise ValueError("command {} not recognized".format(cmd))
        return update

    def is_ready(self):
        return (self._ser is not None)
