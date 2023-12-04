from machine import I2C
try :
    import xbee     
    board = 'B'
except:  
    board = 'A'

class IRThermo:
    def __init__(self):
        if(board == 'B'):
            self._i2c = I2C(1, freq=100000) #this sensor does not respond to the default 400000 i2c bus speed
        else:
            self._i2c = I2C(1, baudrate=100000)
           
    def _read(self, addr):
        data = self._i2c.readfrom_mem(0x5A, addr, 3)
        return (data[1] << 8 | data[0]) * 0.02 - 273.15

    def ambient(self):
        return self._read(0x06)

    def object(self):
        return self._read(0x07)