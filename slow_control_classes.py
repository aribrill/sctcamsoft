# Shared slow control classes and definitions

from abc import ABC, abstractmethod
from collections import namedtuple

# args are values given by the user as input and are strings. The
# DeviceController shall cast them to another type if needed.
DeviceCommand = namedtuple('DeviceCommand', ['device', 'command', 'args'])

class DeviceController(ABC):

    @abstractmethod
    def __init__(self, config):
        raise NotImplementedError()

    # Execute the specified command (of type Command), returning either a
    # dict containing update values or None.
    @abstractmethod
    def execute_command(self, command):
        raise NotImplementedError()

    # Return True if device is initialized and able to communicate, and
    # False otherwise.
    @abstractmethod
    def is_ready(self):
        raise NotImplementedError()
