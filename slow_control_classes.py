# Shared slow control classes and definitions

from abc import ABC, abstractmethod
from collections import namedtuple

# args are values given by the user as input and are strings. The
# DeviceController shall cast them to another type if needed.
DeviceCommand = namedtuple('DeviceCommand', ['device', 'command', 'args'])

class SlowControlError(Exception):
    """Base class for custom exceptions in the slow control software"""
    pass

class CommandArgumentError(SlowControlError):
    """Exception raised for invalid or missing command arguments"""
    pass

class CommandNameError(SlowControlError):
    """Exception raised for invalid command names."""
    pass

class CommandSequenceError(SlowControlError):
    """Exception raised for calling a command in an unsupported order.
    For example, opening a connection when it is already open."""
    pass

class CommunicationError(SlowControlError):
    """Exception raised for errors communicating with a device"""
    pass

class ConfigurationError(SlowControlError):
    """Exception raised for missing or invalid configuration parameters.
    Raise only during initialization."""
    pass

class DeviceNameError(SlowControlError):
    """Exception raised for invalid device names."""
    pass

class VariableError(SlowControlError):
    """Exception raised for invalid variable values."""
    pass

class DeviceController(ABC):

    @abstractmethod
    def __init__(self, config, *args):
        raise NotImplementedError()

    # Execute the specified command (of type DeviceCommand), returning either
    # a dict containing update values or None.
    @abstractmethod
    def execute_command(self, command):
        raise NotImplementedError()
