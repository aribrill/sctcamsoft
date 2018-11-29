import time

class ExpiringValue():
    def __init__(self, value=None, timeout=10):
        self._value = value
        self.lastUpdated = 0
        self.timeout = timeout
    
    @property
    def value(self):
        return self._value

    @value.setter
    def value(self, value):
        self._value = value
        self.lastUpdated = time.time()

    def is_expired(self):
        return time.time() >= (self.lastUpdated + self.timeout)
