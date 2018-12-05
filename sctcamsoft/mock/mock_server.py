import argparse
from collections import namedtuple
import selectors
import socket
import sys
import threading
import traceback

import yaml

from sctcamsoft.mock_server.mock_fan_control import FanController
from sctcamsoft.mock_server.mock_network_control import NetworkController
from sctcamsoft.mock_server.mock_power_control import PowerController

from sctcamsoft.server import ServerController
    
def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('config_file', help='Path to slow control config file')
    parser.add_argument('commands_file', help='Path to slow control commands file')
    args = parser.parse_args()

    with open(args.config_file, 'r') as config_file:
        config = yaml.load(config_file)

    with open(args.commands_file, 'r') as commands_file:
        user_commands = yaml.load(commands_file)

    devices = {
    #       'server': ServerController --> automatically included as self
            'fan': FanController,
            'network': NetworkController,
            'power': PowerController
            }
    server = ServerController('server', config, user_commands, devices)

    server.run_server()

if __name__ == "__main__":
   main()
