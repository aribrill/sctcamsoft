# Control for camera power supply

import os
import subprocess

from slow_control_classes import *

class PowerController(DeviceController):

    def __init__(self, config):
        try:
            self.ip = config['ip']
        except KeyError as e:
            raise ConfigurationError('ip') from e
        try:
            self.MIB_list_path = config['MIB_list_path']
        except KeyError as e:
            raise ConfigurationError('MIB_list_path') from e

    def _snmp_cmd(self, snmpcmd, parameters):
        snmp_command = (snmpcmd + ' -v 2c -m ' + self.MIB_list_path +
                ' -c guru ' + self.ip + ' ' + parameters)
        return snmp_command.split()

    def _cmd_to_snmp(self, cmd):
        cmd_to_snmp = {
                'turn_on_main_switch': [
                    self._snmp_cmd('snmpset', 'sysMainSwitch.0 i 1'),
                    ['sleep', '2']],
                'turn_off_main_switch': [
                    self._snmp_cmd('snmpset', 'sysMainSwitch.0 i 0'),
                    ['sleep',  '2']],
                'start_supply': [
                    self._snmp_cmd('snmpset', 'outputVoltage.u0 Float: 70.0'),
                    self._snmp_cmd('snmpset', 'outputSwitch.u0 i 1')],
                'stop_supply': [
                    self._snmp_cmd('snmpset', 'outputSwitch.u0 i 0')],
                'start_HV': [
                    self._snmp_cmd('snmpset', 'outputVoltage.u4 Float: 70.0'),
                    self._snmp_cmd('snmpset', 'outputSwitch.u4 i 1')],
                'stop_HV': [
                    self._snmp_cmd('snmpset', 'outputSwitch.u4 i 0')],
                'read_supply_current': [
                    self._snmp_cmd('snmpwalk', 'outputMeasurementCurrent.u0')],
                'read_supply_nominal_voltage': [
                    self._snmp_cmd('snmpwalk', 'outputVoltage.u0')],
                'read_supply_measured_voltage': [
                    self._snmp_cmd('snmpwalk',
                        'outputMeasurementSenseVoltage.u0')],
                'read_HV_current': [
                    self._snmp_cmd('snmpwalk', 'outputMeasurementCurrent.u4')],
                'read_HV_nominal_voltage': [
                    self._snmp_cmd('snmpwalk', 'outputVoltage.u4')],
                'read_HV_measured_voltage': [
                    self._snmp_cmd('snmpwalk',
                        'outputMeasurementSenseVoltage.u4')]
                }
        try:
            snmp_commands = cmd_to_snmp[cmd]
        except KeyError as e:
            raise CommandNameError from e
        return snmp_commands

    def execute_command(self, command):
        cmd = command.command
        snmp_commands = self._cmd_to_snmp(cmd)
        commands_with_variables = {
                'read_supply_current': 'supply_current',
                'read_supply_nominal_voltage': 'supply_nominal_voltage',
                'read_supply_measured_voltage': 'supply_measured_voltage',
                'read_HV_current': 'HV_current',
                'read_HV_nominal_voltage': 'HV_nominal_voltage',
                'read_HV_measured_voltage': 'HV_measured_voltage'
                }
        try:
            if cmd in commands_with_variables:
                snmp_command = snmp_commands[0]
                completed_process = subprocess.run(snmp_command, check=True,
                        stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                        encoding='ascii')
                # Parse output string to get numerical reading only
                # Units are V and A
                update_value = completed_process.stdout.split()[-2]
                return (update_commands[cmd], update_value)
            else:
                for snmp_command in snmp_commands:
                    subprocess.run(snmp_command)
                return None
        except OSError as e:
            raise CommunicationError from e
