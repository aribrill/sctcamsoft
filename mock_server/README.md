# Mock SCT Slow Control Server
This folder represents an instance of the sct-slow-control server backed by virtual hardware.

## Running the Server
Run the mock server as though it were the normal server script. If using the main `config.yml` and `commands.yml`, the call should look like this:
```
python mock_server.py ../config.yml ../commands.yml
```

Connect to the server using the standard `user_input.py` and `user_output.py` terminals.

## Configuring the Virtual Hardware
At startup, each mock device pulls its configuration from `mock_server/hardware_state.yml`. Here, you can set the default values of the signals returned by each "device" - currents, voltages, connection and on/off states, etc. 

Many of the devices also a have "noisy_" option. Setting it to `true` will make each mocked value returned by the server vary a bit around the number defined in `hardware_state.yml`.
