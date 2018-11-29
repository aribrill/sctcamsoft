# sct-slow-control GUI
## Requirements
Ensure that the protocol buffers and pyqt5 libraries are installed in your python 3 environment before attempting to run the GUI.

## Running the GUI
The GUI is started via the main.py script in the gui folder. It expects the same parameters as the server itself - a config.yml and a commands.yml file. If testing locally, simply refer to the config and commands file in the repo's root folder.

```
python main.py ../config.yml ../commands.yml
```

If you're trying to test the GUI against the mock server on your own machine, reconfigure such that `host: localhost`. Run the mock server first (using the same config and commands file), then start the GUI. 