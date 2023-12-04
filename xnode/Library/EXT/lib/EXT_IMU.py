from machine import I2C
import time, struct

try :
    import xbee     
    board = 'B'
except:  
    board = 'A'

class IMU:
    def __init__(self):
        if(board=='B'):
            self._i2c = I2C(1)
        else:
            self._i2c = I2C(baudrate=10000)

        self._i2c.writeto_mem(0x28, 0X3D, bytes([0x00])) #Enter configuration mode.
        time.sleep(0.19) #datsheet recommends 19ms
    
        self._i2c.writeto_mem(0x28, 0X07, bytes([0x00])) #Make sure we're in config mode and on page0(param, data), page1(conf)
                            
        self._i2c.writeto_mem(0x28, 0X3F, bytes([0x20])) #Reset the device
        time.sleep(0.65) #Wait 650ms after reset for chip to be ready (as suggested in datasheet)
        
        self._i2c.writeto_mem(0x28, 0X3E, bytes([0x00])) #Set to normal power mode. low power(0x01)
        
        self._i2c.writeto_mem(0x28, 0X3F, bytes([0x80])) #External oscillator
        
        self._i2c.writeto_mem(0x28, 0X3D, bytes([0x0C])) #Enter normal operation mode (NDOF)
        time.sleep(0.19)
        
        time.sleep(0.5) #first, get data deley
    
    def calibration(self):
        cal = self._i2c.readfrom_mem(0x28, 0x35, 1)[0]
        
        sys = (cal >> 6) & 0x03  #NDOF 
        gyro = (cal >> 4) & 0x03
        accel = (cal >> 2) & 0x03
        mag = cal & 0x03
        
        return sys, gyro, accel, mag
            
    def _read_vector(self, address):   
        buf = self._i2c.readfrom_mem(0x28, address, 6)
        xyz = struct.unpack('hhh', struct.pack('BBBBBB', buf[0], buf[1], buf[2], buf[3], buf[4], buf[5]))

        if address == 0x08:     #accel
            scaling = 100.0
        elif address == 0x0E:   #magnetic
            scaling = 16.0
        elif address == 0x14:   #gyro
            scaling = 916.0     #i * 0.001090830782496456
        elif address == 0x1A:   #euler
            scaling = 16.0  
        elif address == 0x28:   #lineraccel
            scaling = 100.0
        elif address == 0x2E:   #gravity
            scaling = 100.0
            
        return tuple([i / scaling for i in xyz])

    def accel(self):
        return self._read_vector(0x08)

    def magnetic(self):
        return self._read_vector(0x0E)

    def gyro(self):
        return self._read_vector(0x14)

    def euler(self):
        return self._read_vector(0x1A)

    def lineraccel(self):
        return self._read_vector(0x28)

    def gravity(self):
        return self._read_vector(0x2E)

    def quat(self):               
        buf = self._i2c.readfrom_mem(0x28, 0x20, 8)
        wxyz = struct.unpack('hhhh', struct.pack('BBBBBBBB', buf[0], buf[1], buf[2], buf[3], buf[4], buf[5], buf[6], buf[7]))
    
        return tuple([i / (1 << 14) for i in wxyz])
    
    def temp(self):
        t = self._i2c.readfrom_mem(0x28, 0x34, 1)[0]
        if t > 127:
            return t - 256
        else:
            return t
    