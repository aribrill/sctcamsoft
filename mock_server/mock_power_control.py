from slow_control_classes import *

class PowerController(DeviceController):

    def __init__(self, device, config):
        self.device = device
        try:
            self.ip = config['ip']
        except KeyError:
            raise ConfigurationError(self.device, 'ip',
                    "missing configuration parameter")
        try:
            self.MIB_list_path = config['MIB_list_path']
        except KeyError:
            raise ConfigurationError(self.device, 'MIB_list_path',
                    "missing configuration parameter")

        self._is_main_switch_on = False

        self._is_supply_on = False
        self._supply_current = -1.0
        self._supply_nominal_voltage = -1.0
        self._supply_measured_voltage = -1.0

        self._is_high_voltage_on = False
        self._hv_current = -1.0
        self._hv_nominal_voltage = -1.0
        self._hv_measured_voltage = -1.0

    def setSupply(self, is_on, current, nom_volts, meas_volts):
        self._is_supply_on = is_on
        self._supply_current = current
        self._supply_nominal_voltage = nom_volts
        self._supply_measured_voltage = meas_volts

    def setHV(self, is_on, current, nom_volts, meas_volts):
        self._is_high_voltage_on = is_on
        self._hv_current = current
        self._hv_nominal_voltage = nom_volts
        self._hv_measured_voltage = meas_volts
        

    def execute_command(self, command):
        cmd = command.command
        if cmd == 'turn_on_main_switch':
            self._is_main_switch_on = True
            if self._is_supply_on:
                self._supply_current = 20.4
                self._supply_measured_voltage = 70.1
            if self._is_high_voltage_on:
                self._hv_current = 20.2
                self._hv_measured_voltage = 70.05
        elif cmd == 'turn_off_main_switch':
            self._is_main_switch_on = False
            self._supply_current = 0.0
            self._supply_measured_voltage = 0.0
            self._hv_current = 0.0
            self._hv_measured_voltage = 0.0
        elif cmd == 'start_supply':
            self._is_supply_on = True
            self._supply_nominal_voltage = 70.0
            if self._is_main_switch_on:
                self._supply_current = 20.4
                self._supply_measured_voltage = 70.1
        elif cmd == 'stop_supply':
            self._is_supply_on = False
            self._supply_nominal_voltage = 0.0
            if self._is_main_switch_on:
                self._supply_current = 0.005
                self._supply_measured_voltage = 0.1
        elif cmd == 'start_HV':
            self._is_high_voltage_on = True
            self._hv_nominal_voltage = 70.0
            if self._is_main_switch_on:
                self._hv_current = 20.2
                self._hv_measured_voltage = 70.05
        elif cmd == 'stop_HV':
            self._is_high_voltage_on = False
            self._hv_nominal_voltage = 0.0
            if self._is_main_switch_on:
                self._hv_current = 0.001
                self._hv_measured_voltage = 0.05
        elif cmd == 'read_supply_current':
            update_value = self._supply_current
        elif cmd == 'read_supply_nominal_voltage':
            update_value = self._supply_nominal_voltage
        elif cmd == 'read_supply_measured_voltage':
            update_value = self._supply_measured_voltage
        elif cmd == 'read_HV_current':
            update_value = self._hv_current
        elif cmd == 'read_HV_nominal_voltage':
            update_value = self._hv_nominal_voltage
        elif cmd == 'read_HV_measured_voltage':
            update_value = self._hv_measured_voltage

        commands_with_variables = {
            'read_supply_current': 'supply_current',
            'read_supply_nominal_voltage': 'supply_nominal_voltage',
            'read_supply_measured_voltage': 'supply_measured_voltage',
            'read_HV_current': 'HV_current',
            'read_HV_nominal_voltage': 'HV_nominal_voltage',
            'read_HV_measured_voltage': 'HV_measured_voltage'
        }   
        
        if cmd in commands_with_variables:
            return (self.device, commands_with_variables[cmd], update_value)
