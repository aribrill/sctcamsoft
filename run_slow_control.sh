#!/bin/bash

CONFIG=$1
gnome-terminal -- bash -c "source activate slowcontrol; python server.py $CONFIG; source deactivate; bash" &
sleep 4
gnome-terminal -- bash -c "source activate slowcontrol; python -u user_output.py $CONFIG | tee -a slow_control.log; source deactivate; bash" &
gnome-terminal -- bash -c "source activate slowcontrol; python user_input.py $CONFIG; source deactivate; bash" &
