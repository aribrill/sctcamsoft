import os

import yaml

hw_state_yml_relpath = "hardware_state.yml"

def get_device_state(device):
    cwd_path = os.path.dirname(os.path.realpath(__file__))
    hw_state_yml_abspath = os.path.join(cwd_path, hw_state_yml_relpath)
    
    with open(hw_state_yml_abspath, 'r') as hardware_state_file:
        device_states = yaml.load(hardware_state_file)
    return device_states.get(device, {})
    