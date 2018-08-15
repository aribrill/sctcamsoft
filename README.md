# sct-slow-control
Slow control software for the CTA SCT camera

## Usage

```bash
cd /path/to/slow/control
# Open three terminals to the server, user output, and user input programs
./run_slow_control.sh config.yml
```
In the user input terminal, type in commands and arguments as defined in config.yml. View output in the user output terminal. The output is also copied to a text file called slow_control.log.

## Dependencies
- PyYAML
- pySerial (for fan control)
