from machine import Pin, I2C, ADC
import time


##################################################################
class DoorLock:
    def __init__(self, pin1='D0',pin2='D7'):
        self._pin1 = Pin(pin1, mode=Pin.OUT, value=0)
        self._pin2=Pin(pin2,Pin.IN)

    def work(self):
        self._pin1(0)
        time.sleep(0.1)
        self._pin1(1)
        time.sleep(0.1)
        self._pin1(0)

    def open(self):
        if self.read()==0:
            self._pin1(0)
            time.sleep(0.1)
            self._pin1(1)
            time.sleep(0.1)
            self._pin1(0)
            
    def close(self):
        if self.read()==1:
            self._pin1(0)
            time.sleep(0.1)
            self._pin1(1)
            time.sleep(0.1)
            self._pin1(0)   
                 
    def read(self):
        return self._pin2()
    
##################################################################
class Pir:
    ENTER = 1
    LEAVER = 2
    BOTH = (ENTER | LEAVER)
    
    def __init__(self, pin='P2'):
        self._pin = Pin(pin, Pin.IN)
        self._stat = False
            
    def read(self):
        return self._pin()

    def check(self, mode=ENTER, delay=300):
        ret = (self.read() == 1)
        
        if self._stat != ret:
            self._stat = not self._stat
            
            t = time.ticks_ms()
            while time.ticks_ms() - t <= delay: pass
            
            if mode == Pir.ENTER and self._stat:
                return True
            elif mode == Pir.LEAVER and not self._stat:
                return False
            elif mode == Pir.BOTH:
                return ret
        
        return None