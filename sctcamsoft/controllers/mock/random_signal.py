from numpy import random

class RandomSignal():    
    def __init__(self, mean, stdev, decimal_places=3):
        self._mean = mean
        self._stdev = stdev
        self._nextIndex = 0
        self._values = []
        self._round_to = decimal_places
        self._computeRandVals()

    def read(self):
        if (self._nextIndex >= len(self._values)):
            self._computeRandVals()

        nextVal = self._values[self._nextIndex]
        self._nextIndex += 1

        return round(nextVal, self._round_to)

    def _computeRandVals(self):
        num_values = 100
        self._values = random.normal(self._mean, self._stdev, num_values)
        self._nextIndex = 0
