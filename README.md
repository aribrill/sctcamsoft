# SCT Slow Control
Slow control software for the CTA SCT camera. This software allows the camera operator to control and automatically monitor the SCT camera and ancillary devices.

## Installation
Use the provided conda environment file to create an [Anaconda](https://www.anaconda.com/) environment containing all dependencies for the slow control code using the command `conda env create -f environment.yml`. Alternatively, all the dependencies as specified in that file may be installed separately. Compile the protocol buffers definition file with `protoc -I=. --python_out=. ./slow_control.proto`.

## Configuration

Configuration is provided using two YAML files. First, config.yml specifies configuration parameters for connecting to devices such as IP addresses and timeout values. Second, commands.yml lists the available commands. There are three types of commands: low level, which cause an action by a specific device; special, which change the mode for how the server interprets commands (e.g. enter repeat mode); and high level, which are a list of commands (which themselves may be of any type). The arguments to commands may be specified by default values in commands.yml or user input.

## Usage

To run the slow control software, first run the run the server program using `sudo python server.py config.yml commands.yml`. Running as superuser is necessary for monitoring network activity. When the server is running and configured, run the user input and output programs with `python user_input.py config.yml commands.yml` and `python user_output.py config.yml`. When done, close out of all three programs using Ctrl^C.

A script for running all three programs either locally or remotely on the camera server is available along with instructions on the SCT Camera Slow Control Confluence page.

In the user input terminal, type in commands and arguments as defined in commands.yml. View output in the user output terminal. The traceback for all errors handled by the server is printed in the server terminal.

## Supported Commands

Control and monitoring is available for three devices: camera fans, camera power, and network connection. See commands.yml for a complete list of supported commands. It is possible to set alerts for any numerical monitoring variable.

The slow control software provides high-level commands to automate normal camera operation. Type `startup` to prepare camera for operation (Operations Manual sec. 5.1 and 5.2). When everything is connected and on, type `start_HV` to turn on HV, and `stop_HV` to turn it off. When done taking data, type `shutdown` to prepare camera for shutdown (Manual sec. 6.1).


## GUI
The GUI is started via the main.py script in the gui folder. It expects the same parameters as the server itself - a config.yml and a commands.yml file. If testing locally, simply refer to the config and commands file in the repo's root folder.

```
python main.py ../config.yml ../commands.yml
```

If you're trying to test the GUI against the mock server on your own machine, reconfigure such that `host: localhost`. Run the mock server first (using the same config and commands file), then start the GUI. 

## Mock SCT Slow Control Server
This folder represents an instance of the sct-slow-control server backed by virtual hardware.

### Running the Server
Run the mock server as though it were the normal server script. If using the main `config.yml` and `commands.yml`, the call should look like this:
```
python mock_server.py ../config.yml ../commands.yml
```

Connect to the server using the standard `user_input.py` and `user_output.py` terminals.

### Configuring the Virtual Hardware
At startup, each mock device pulls its configuration from `mock_server/hardware_state.yml`. Here, you can set the default values of the signals returned by each "device" - currents, voltages, connection and on/off states, etc. 

Many of the devices also a have "noisy_" option. Setting it to `true` will make each mocked value returned by the server vary a bit around the number defined in `hardware_state.yml`.
