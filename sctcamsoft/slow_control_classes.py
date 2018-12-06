# Shared slow control classes and definitions

from abc import ABC, abstractmethod
from collections import namedtuple

# args are values given by the user as input and are strings. The
# DeviceController shall cast them to another type if needed.
DeviceCommand = namedtuple('DeviceCommand', ['device', 'command', 'args'])

class SlowControlError(Exception):
    """Base class for custom exceptions in the slow control software"""
    
    def __init__(self, device):
        self.device = device
        self.message = ""

class CommandArgumentError(SlowControlError):
    """Exception raised for invalid or missing command arguments"""
    
    def __init__(self, device, command, argument, message):
        self.device = device
        self.command = command
        self.argument = argument
        self.message = "{}: {}: {}".format(command, argument, message)

class CommandNameError(SlowControlError):
    """Exception raised for invalid command names."""
    
    def __init__(self, device, command):
        self.device = device
        self.command = command
        self.message = "{}: invalid command name".format(command)

class CommandSequenceError(SlowControlError):
    """Exception raised for calling a command in an unsupported order.
    For example, opening a connection when it is already open."""
    
    def __init__(self, device, command, message):
        self.device = device
        self.command = command
        self.message = "{}: {}".format(command, message)

class CommunicationError(SlowControlError):
    """Exception raised for errors communicating with a device"""
    
    def __init__(self, device):
        self.device = device
        self.message = "not connected"

class ConfigurationError(SlowControlError):
    """Exception raised for missing or invalid configuration parameters.
    Raise only during initialization."""
    
    def __init__(self, device, parameter, message):
        self.device = device
        self.parameter = parameter
        self.message = "{}: {}".format(parameter, message)

class DeviceNameError(SlowControlError):
    """Exception raised for invalid device names."""

    def __init__(self, device):
        self.device = device
        self.message = "invalid device"

class VariableError(SlowControlError):
    """Exception raised for invalid variable values."""
    
    def __init__(self, device, variable, value, message):
        self.device = device
        self.variable = variable
        self.value = value
        self.message = "{}: {}: {}".format(variable, value, message)

class DeviceController(ABC):

    @abstractmethod
    def __init__(self, device, config, *args):
        raise NotImplementedError()

    # Execute the specified command (of type DeviceCommand), returning either
    # a dict containing update values or None.
    @abstractmethod
    def execute_command(self, command):
        raise NotImplementedError()
