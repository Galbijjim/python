from machine import I2C, Pin
import time

try :
    import xbee     
    board = 'B'
except:  
    board = 'A'

class Buzzer:
    def __init__(self):
        if(board == 'B'):
            self._pin = Pin('P0', Pin.OUT, value=0)
        else:
            self._pin = Pin('P8', Pin.OUT, value=0)

    def on(self):
        self._pin.value(1)

    def off(self):
        self._pin.value(0)

    def beep(self, delay, func=None, param=None, on=50, off=10):
        _func = func
        _param = param
        
        self.on()
        t_on = time.ticks_ms()
        t_off = 0
        
        while delay:               
            if t_on and time.ticks_ms() - t_on > on:        
                self.off()
                t_on = 0
                t_off = time.ticks_ms()
                
            if t_off and time.ticks_ms() - t_off > off:
                t_on = time.ticks_ms()
                t_off = 0
                            
                self.on()  
                delay -= 1
                if _func:
                    _func(_param) if _param else _func()
                    
        self.off()      

class _PCA9535:
    def __init__(self):
        self._i2c = I2C(1)
        self._i2c.writeto_mem(0x24, 0x06, bytes([0xFF]))
        self._i2c.writeto_mem(0x24, 0x07, bytes([0x00]))
    
    def write(self, n):
        self._i2c.writeto_mem(0x24, 0x03, bytes([0xFF & ~n]))
    
    def read(self):
        return ~self._i2c.readfrom_mem(0x24, 0x00, 1)[0] & 0x03
    
class _Led():
    def __init__(self, leds):
        self._index = 0
        self._leds = leds
        
    def on(self):
        self._leds[self._index-1] = True
    
    def off(self):
        self._leds[self._index-1] = False
        
class Leds(_PCA9535):
    def __init__(self):
        super().__init__()
        self._stat = 0x00
        self._count = 8
   
    def __call__(self):
        return tuple([((self._stat >> i) & 0x1) == 1 for i in range(7+1)])
    
    def __getitem__(self, index):
        return ((self._stat >> index) & 0x01) == 1
    
    def __setitem__(self, index, value):
        if value:
            self._stat |= (1 << index)
        else:
            self._stat &= ~(1 << index)
        self.write(self._stat)

    def __iter__(self):
        self._led = _Led(self)
        return self
    
    def __next__(self):
        if self._led._index < self._count:
            self._led._index += 1
            return self._led
        else:
            raise StopIteration
        
    def on(self):
        self.write(0xff)
        
    def off(self):
        self.write(0x00)

    def write(self, n):
        self._stat = n
        super().write(self._stat)
        
    def clear(self):
        self._stat = 0x00
        self.write(self._stat)

class Buttons(_PCA9535):
    def __init__(self):
        super().__init__()

    def __getitem__(self, index):
        bits = self.read()
        return (bits & 0x01) if index == 0 else ((bits >> 1) & 0x01) if index == 1 else None
    
    def __call__(self):
        bits = self.read()        
        return bits & 0x01, (bits >> 1) & 0x01