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
        protocol = config.get('protocol', 'telnet')
        if protocol == 'serial':
            self.ser = serial.Serial(port='/dev/ttyACM0',
                    baudrate=115200,
                    bytesize=8,
                    parity='N',
                    stopbits=1)
        elif protocol == 'telnet':
            host = config['telnet_host']
            port = config['telnet_port']
            timeout = config.get('telnet_timeout', None)
            if timeout is None:
                self.ser = telnetlib.Telnet(host, port)
            else:
                try:
                    self.ser = telnetlib.Telnet(host, port, timeout)
                except socket.timeout as e:
                    print("WARNING: Could not connect to fan")
        else:
            raise ValueError("ERROR: Unknown protocol '{}'".format(protocol))

    def _send_cmd(self, cmd):
        self.ser.write("{}\n".format(cmd))
        time.sleep(0.1)
        val = self.ser.read_all()
        return val

    def _close(self):
        self.ser.close()

    def _turn_on(self): 
        #5V pulse, used to trigger a laser when not using the LED
        self._send_cmd("PWR ON")

    def _turn_off(self):
        self._send_cmd("PWR OFF")
        self.close()
        time.sleep(1)
    
    def _read_voltage(self):
        val = self._send_cmd("VREAD")
        time.sleep(1)
        return val

    def _read_current(self):
        val = self._send_cmd("IREAD")
        time.sleep(1)
        return val

    def execute_command(self, command):
        cmd = command.command
        update = None
        if cmd == "turn_on":
            self._turn_on()
        elif cmd == "turn_off":
            fan._turn_off()
        elif cmd == "read_voltage":
            voltage = self._read_voltage()
            update = {'voltage': voltage}
        elif cmd == "read_current":
            current = self._read_current()
            update = {'current': current}
        else:
            raise ValueError("command {} not recognized".format(cmd))
        return update
