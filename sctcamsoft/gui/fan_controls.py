from expiring_value import ExpiringValue

from PyQt5 import QtGui

class FanControls():
    def __init__(self, 
                 on_button, off_button, 
                 voltage_textedit, current_textedit,
                 alert_textedit, update_signal, 
                 timer_signal, send_command_signal):
        self._on_button = on_button
        self._off_button = off_button

        self._voltage = ExpiringValue(0.0, timeout=35)
        self._voltage_textedit = voltage_textedit

        self._current = ExpiringValue(0.0, timeout=35)
        self._current_textedit = current_textedit
        
        self._alert = ExpiringValue("", timeout=15)
        self._alert_textedit = alert_textedit

        self._on_button.clicked.connect(self.fans_on)
        self._off_button.clicked.connect(self.fans_off)
        update_signal.connect(self.on_update)
        timer_signal.connect(self._check_expired)
        self._send_command_signal = send_command_signal

    def fans_on(self):
        self._send_command_signal.emit('start_fans')

    def fans_off(self):
        self._send_command_signal.emit('stop_fans')

    def draw_controls(self):
        def update_with_expiration_state(expiring_val, lineedit):
            if (expiring_val.is_expired()):
                strike_font = QtGui.QFont()
                strike_font.setStrikeOut(True)
                lineedit.setFont(strike_font)
            else:
                std_font = QtGui.QFont()
                std_font.setStrikeOut(False)
                lineedit.setFont(std_font)
            lineedit.setText(str(expiring_val.value))

        update_with_expiration_state(self._voltage, self._voltage_textedit)
        update_with_expiration_state(self._current, self._current_textedit)

        self.draw_alert()

    def draw_alert(self):
        if self._alert.is_expired():
            self._alert_textedit.setText("OK")
        else:
            self._alert_textedit.setText(self._alert.value)

    def on_update(self, update):
        alert_vars = ['fan_current', 'fan_voltage']

        if (update.device == 'ALERT' and (update.variable in alert_vars)):
            self._alert.value = 'ALERT: {} {}'.format(update.variable, update.value)
            self.draw_alert()
        elif (update.device == 'fan'):
            if (update.variable == 'voltage'):
                self._voltage.value = update.value
            elif (update.variable == 'current'):
                self._current.value = update.value
            self.draw_controls()
    
    def _check_expired(self):
        if (self._voltage.is_expired() or self._current.is_expired() or self._alert.is_expired()):
            self.draw_controls()
