#!/bin/bash

export NO_AT_BRIDGE=1
gnome-terminal -- bash -c "source activate sct-slow-control; sudo env 'PATH=$PATH' python server.py config.yml commands.yml; source deactivate; bash" &
sleep 3
gnome-terminal -- bash -c "source activate sct-slow-control; python -u user_output.py config.yml; source deactivate; bash" &
gnome-terminal -- bash -c "source activate sct-slow-control; python user_input.py config.yml commands.yml; source deactivate; bash" &
