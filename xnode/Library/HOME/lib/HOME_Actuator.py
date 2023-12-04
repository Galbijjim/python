from machine import Pin

##################################################################
class FAN:
    def __init__(self, pin='D5'):
        self._pin = Pin(pin, mode=Pin.OUT, value=0)

    def on(self):
        self._pin(1)

    def off(self):
        self._pin(0)
    
    def stat(self):
        return self._pin() == 1
##################################################################
class Light:
    def __init__(self, pin='D6'):
        self._pin = Pin(pin, mode=Pin.OUT, value=0)

    def on(self):
        self._pin(1)

    def off(self):
        self._pin(0)
    
    def stat(self):
        return self._pin() == 1