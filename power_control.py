# Control for camera power supply

import os
import subprocess

from slow_control_classes import Command, DeviceController

class PowerController(DeviceController):

    def __init__(self, config):
        self.ip = config['ip']
        self.MIB_list_path = config['MIB_list_path']
        if not self.is_ready():
            print("Warning: power control not set up")

    def _snmp_cmd(self, snmpcmd, parameters):
        snmp_command = (snmpcmd + ' -v 2c -m ' + self.MIB_list_path +
                ' -c guru ' + self.ip + ' ' + parameters)
        return snmp_command

    def _list_snmp_commands(self, cmd):
        cmd_to_snmp = {
                'start_main_switch': [
                    self._snmp_cmd('snmpset', 'sysMainSwitch.0 i 1'),
                    'sleep 2'],
                'stop_main_switch': [
                    self._snmp_cmd('snmpset', 'sysMainSwitch.0 i 0'),
                    'sleep 2'],
                'start_70V': [
                    self._snmp_cmd('snmpset', 'outputVoltage.u0 Float: 70.0'),
                    self._snmp_cmd('snmpset', 'outputSwitch.u0 i 1')],
                'stop_70V': [
                    self._snmp_cmd('snmpset', 'outputSwitch.u0 i 0')],
                'start_HV': [
                    # TODO: How is the HV voltage actually set?
                    self._snmp_cmd('snmpset', 'outputSwitch.u4 i 1')],
                'stop_HV': [
                    self._snmp_cmd('snmpset', 'outputSwitch.u4 i 0')],
                'read_70V_current': [
                    self._snmp_cmd('snmpwalk', 'outputMeasurementCurrent.u0')],
                'read_70V_voltage': [
                    self._snmp_cmd('snmpwalk',
                        'outputMeasurementSenseVoltage.u0')],
                'read_HV_current': [
                    self._snmp_cmd('snmpwalk', 'outputMeasurementCurrent.u4')],
                'read_HV_voltage': [
                    self._snmp_cmd('snmpwalk',
                        'outputMeasurementSenseVoltage.u4')]
                }
        return cmd_to_snmp[cmd]

    def execute_command(self, command):
        cmd = command.command
        snmp_commands = self._list_snmp_commands(cmd)
        if not self.is_ready():
            print("Warning: skipping command, power control is not ready")
            return None
        if cmd in ['start_main_switch', 'stop_main_switch', 'start_70V',
            'stop_70V', 'start_HV', 'stop_HV']:
            for snmp_command in snmp_commands:
                subprocess.run(snmp_command)
            return None
        elif cmd in ['read_70V_current', 'read_70V_voltage',
                'read_HV_current', 'read_HV_voltage']:
            snmp_command = snmp_commands[0]
            completed_process = subprocess.run(snmp_command,
                    capture_output=True, text=True)
            # Parse output string to get numerical reading
            # Units are V and A
            update = float(completed_process.stdout.split()[-2])
            return update
        else:
            raise ValueError("command {} not recognized".format(cmd))

    def is_ready(self):
        is_ready = True
        if not os.path.isfile(self.MIB_list_path):
            print("No MIB list found at path".format(self.MIB_list_path))
            is_ready = False
        return is_ready
