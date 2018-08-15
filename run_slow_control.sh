#!/bin/bash

CONFIG=$1
gnome-terminal -- bash -c "python server.py $CONFIG; bash"
gnome-terminal -- bash -c "python -u user_output.py $CONFIG | tee -a slow_control.log; bash"
gnome-terminal -- bash -c "python user_input.py $CONFIG; bash"
