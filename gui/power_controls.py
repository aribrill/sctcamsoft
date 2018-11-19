
class PowerControls():
    def __init__(self, 
                 on_button, off_button, 
                 supply_current_textedit, hv_current_textedit,
                 update_signal, send_command_signal):
        self._on_button = on_button
        self._off_button = off_button
        self._supply_current_textedit = supply_current_textedit
        self._hv_current_textedit = hv_current_textedit

        self._on_button.clicked.connect(self.start_camera_power)
        self._off_button.clicked.connect(self.stop_camera_power)
        update_signal.connect(self.on_update)
        self._send_command_signal = send_command_signal

    def start_camera_power(self):
        self._send_command_signal.emit('start_camera_power')

    def stop_camera_power(self):
        self._send_command_signal.emit('stop_camera_power')

    def update_supply_current(self, new_voltage):
        self._supply_current_textedit.setText(new_voltage)

    def update_hv_current(self, new_current):
        self._hv_current_textedit.setText(new_current)

    def on_update(self, update):
        if (update.device == 'power'):
            if (update.variable == 'supply_current'):
                self.update_supply_current(update.value)
            elif (update.variable == 'HV_current'):
                self.update_hv_current(update.value)
