
class FanControls():
    def __init__(self, 
                 on_button, off_button, 
                 voltage_textedit, current_textedit,
                 alert_textedit, update_signal, send_command_signal):
        self._on_button = on_button
        self._off_button = off_button
        self._voltage_textedit = voltage_textedit
        self._current_textedit = current_textedit
        self._alert_textedit = alert_textedit

        self._on_button.clicked.connect(self.fans_on)
        self._off_button.clicked.connect(self.fans_off)
        update_signal.connect(self.on_update)
        self._send_command_signal = send_command_signal

    def fans_on(self):
        self._send_command_signal.emit('start_fans')
        # user_input.send_command('start_fans')

    def fans_off(self):
        self._send_command_signal.emit('stop_fans')
        # user_input.send_command('stop_fans')

    def voltage_update(self, new_voltage):
        self._voltage_textedit.setText(new_voltage)

    def current_update(self, new_current):
        self._current_textedit.setText(new_current)

    def draw_alert(self, state, notifcation):
        self._alert_textedit.setText(notifcation)

    def on_update(self, update):
        alert_vars = ['fan_current', 'fan_voltage']

        if (update.device == 'ALERT' and (update.variable in alert_vars)):
            self.draw_alert('alert', 'ALERT: {} {}'.format(update.variable, update.value))
        elif (update.device == 'fan'):
            self.draw_alert('ok', 'OK')
            if (update.variable == 'voltage'):
                self.voltage_update(update.value)
            elif (update.variable == 'current'):
                self.current_update(update.value)
