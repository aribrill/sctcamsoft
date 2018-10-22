# SCT Slow Control
Slow control software for the CTA SCT camera

## Installation
Use the provided conda environment file to create an [Anaconda](https://www.anaconda.com/) environment containing all dependencies for the slow control code using the command `conda env create -f environment.yml`. Alternatively, all the dependencies as specified in that file may be installed separately. Compile the protocol buffers definition file with `protoc -I=. --python_out=. ./slow_control.proto`.

## Configuration

Configuration is provided using two YAML files. First, config.yml specifies configuration parameters for connecting to devices such as IP addresses and timeout values. Second, commands.yml lists the available commands. There are three types of commands: low level, which cause an action by a specific device; special, which change the mode for how the server interprets commands (e.g. enter repeat mode); and high level, which are a list of commands (which themselves may be of any type). The arguments to commands may be specified by default values in commands.yml or user input.

## Usage

To run the slow control software, first run the run the server program using `sudo python server.py config.yml commands.yml`. Running as superuser is necessary for monitoring network activity. When the server is running and configured, run the user input and output programs with `python user_input.py config.yml commands.yml` and `python user_output.py config.yml`. 

A script for running all three programs either locally or remotely on the camera server is available along with instructions on the SCT Camera Slow Control Confluence page.

In the user input terminal, type in commands and arguments as defined in commands.yml. View output in the user output terminal. The traceback for all errors handled by the server is printed in the server terminal.
