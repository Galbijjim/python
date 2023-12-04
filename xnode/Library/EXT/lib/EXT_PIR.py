from machine import Pin
import time

try :
    import xbee     
    board = 'B'
except:  
    board = 'A'

class Pir:
    ENTER = 1
    LEAVER = 2
    BOTH = (ENTER | LEAVER)
    
    def __init__(self):
        if(board == 'B'):
            self._pin = Pin("P2", Pin.IN)
        else:
            self._pin = Pin("P17", Pin.IN)
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
    