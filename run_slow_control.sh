#!/bin/bash

export NO_AT_BRIDGE=1
gnome-terminal -- bash -c "source activate slowcontrol; python server.py config.yml commands.yml; source deactivate; bash" &
sleep 3
gnome-terminal -- bash -c "source activate slowcontrol; python -u user_output.py config.yml | tee -a slow_control.log; source deactivate; bash" &
gnome-terminal -- bash -c "source activate slowcontrol; python user_input.py config.yml commands.yml; source deactivate; bash" &
