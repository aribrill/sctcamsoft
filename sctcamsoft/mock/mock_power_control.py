from sctcamsoft.slow_control_classes import *
from hardware_state_helpers import *

from random_signal import RandomSignal

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

        hw_state = get_device_state(device)

        self._is_main_switch_on = hw_state['main_switch_on']
        self._is_supply_on = hw_state['supply_on']
        self._is_high_voltage_on = hw_state['high_voltage_on']

        add_noise = hw_state['noisy_signal']

        self._zero_signal = RandomSignal(0, 0.01 if add_noise else 0.0)

        self._supply_current_sig = RandomSignal(
            hw_state['supply_current'], 
            0.2 if add_noise else 0.0)
        self._supply_nominal_voltage = hw_state['supply_nominal_voltage']
        self._supply_measured_voltage_sig = RandomSignal(
            hw_state['supply_measured_voltage'], 
            1 if add_noise else 0)

        self._hv_current_sig = RandomSignal(
            hw_state['hv_current'], 
            0.1 if add_noise else 0.0)
        self._hv_nominal_voltage = hw_state['hv_nominal_voltage']
        self._hv_measured_voltage_sig = RandomSignal(
            hw_state['hv_measured_voltage'], 
            1 if add_noise else 0)
        
    def execute_command(self, command):
        cmd = command.command
        if cmd == 'turn_on_main_switch':
            self._is_main_switch_on = True
        elif cmd == 'turn_off_main_switch':
            self._is_main_switch_on = False
        elif cmd == 'start_supply':
            self._is_supply_on = True
        elif cmd == 'stop_supply':
            self._is_supply_on = False
        elif cmd == 'start_HV':
            self._is_high_voltage_on = True
        elif cmd == 'stop_HV':
            self._is_high_voltage_on = False

        elif cmd == 'read_supply_current':
            if (self._is_main_switch_on and self._is_supply_on): 
                update_value = self._supply_current_sig.read()
            else:
                update_value = self._zero_signal.read()

        elif cmd == 'read_supply_nominal_voltage':
                update_value = self._supply_nominal_voltage

        elif cmd == 'read_supply_measured_voltage':
            if (self._is_main_switch_on and self._is_supply_on):
                update_value = self._supply_measured_voltage_sig.read()
            else:
                update_value = self._zero_signal.read()

        elif cmd == 'read_HV_current':
            if (self._is_main_switch_on and self._is_high_voltage_on):
                update_value = self._hv_current_sig.read()
            else:
                update_value = self._zero_signal.read()
                
        elif cmd == 'read_HV_nominal_voltage':
            update_value = self._hv_nominal_voltage

        elif cmd == 'read_HV_measured_voltage':
            if (self._is_main_switch_on and self._is_high_voltage_on):
                update_value = self._hv_measured_voltage_sig.read()
            else:
                update_value = self._zero_signal.read()
            
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
