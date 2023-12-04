from machine import I2C, Pin
import time

##################################################################
class PCA9685:
    REG_MODE1 = 0x00
    REG_MODE2 = 0x01
    REG_PRESCALE = 0xFE
    REG_LED0_ON_L = 0x06
    REG_LED0_ON_H = 0x07
    REG_LED0_OFF_L = 0x08
    REG_LED0_OFF_H = 0x09
    REG_ALL_ON_L = 0xFA
    REG_ALL_ON_H = 0xFB
    REG_ALL_OFF_L = 0xFC
    REG_ALL_OFF_H = 0xFD

    RESTART = 1<<7
    AI = 1<<5
    SLEEP = 1<<4
    ALLCALL	= 1<<0
    OCH = 1<<3
    OUTDRV = 1<<2
    INVRT = 1<<4

    def __init__(self, addr=0x40):
        self._i2c = I2C(1)
        self._sAddr = addr
                
        self.init()

        self._curChannel = -1

    def init(self):
        buf = self.AI | self.ALLCALL
        self._i2c.writeto_mem(self._sAddr,self.REG_MODE1,bytes([buf]))
        buf = self.OCH | self.OUTDRV
        self._i2c.writeto_mem(self._sAddr,self.REG_MODE2,bytes([buf]))
        time.sleep(0.05)
        recv = self._i2c.readfrom_mem(self._sAddr,self.REG_MODE1,1)
        buf = recv[0] & (~self.SLEEP)
        self._i2c.writeto_mem(self._sAddr,self.REG_MODE1,bytes([buf]))

    def setChannel(self, ch):
        self._curChannel = ch

    def setDuty(self, percent):
        step = int(round(percent * (4096.0 / 100.0)))
        
        on = step
        off = 0

        on_l = on&0xff
        on_h = on>>8
        off_l = off&0xff
        off_h = off>>8
        
        if self._curChannel >= 0:
            self._i2c.writeto_mem(self._sAddr,self.REG_LED0_ON_L+4*self._curChannel,bytes([on_l]))
            self._i2c.writeto_mem(self._sAddr,self.REG_LED0_ON_H+4*self._curChannel,bytes([on_h]))
            self._i2c.writeto_mem(self._sAddr,self.REG_LED0_OFF_L+4*self._curChannel,bytes([off_l]))
            self._i2c.writeto_mem(self._sAddr,self.REG_LED0_OFF_H+4*self._curChannel,bytes([off_h]))
        elif self._curChannel == -1:
            self._i2c.writeto_mem(self._sAddr,self.REG_ALL_ON_L,bytes([on_l]))
            self._i2c.writeto_mem(self._sAddr,self.REG_ALL_ON_H,bytes([on_h]))
            self._i2c.writeto_mem(self._sAddr,self.REG_ALL_OFF_L,bytes([off_l]))
            self._i2c.writeto_mem(self._sAddr,self.REG_ALL_OFF_H,bytes([off_h]))

    def setFreq(self, freq):
        prescale = int(round(25000000/(4096*freq))-1)
        if prescale < 3:
            prescale = 3
        elif prescale > 255:
            prescale = 255

        recv = self._i2c.readfrom_mem(self._sAddr,self.REG_MODE1,1)
        buf = (recv[0] &(~self.SLEEP))|self.SLEEP
        self._i2c.writeto_mem(self._sAddr,self.REG_MODE1,bytes([buf]))
        self._i2c.writeto_mem(self._sAddr,self.REG_PRESCALE,bytes([prescale]))
        self._i2c.writeto_mem(self._sAddr,self.REG_MODE1,bytes(recv))
        time.sleep(0.05)
        buf = recv[0] | self.RESTART
        self._i2c.writeto_mem(self._sAddr,self.REG_MODE1,bytes([buf]))

    def setInvertPulse(self):
        recv = self._i2c.readfrom_mem(self._sAddr,self.REG_MODE2,1)
        buf = recv[0] | self.INVRT
        self._i2c.writeto_mem(self._sAddr,self.REG_MODE2,bytes([buf]))
        time.sleep(0.05)

##################################################################
class GasBreaker(PCA9685):
    def __init__(self, addr=0x40):
        super().__init__(addr)

        self.setChannel(-1)
        self.setFreq(1526)
        self.setDuty(0)
        
        self.setChannel(8)
        self.setDuty(100)
        self.setChannel(9)
        self.setDuty(100)
    
    def open(self):
        self.setChannel(3)
        self.setDuty(100)
        self.setChannel(2)
        self.setDuty(0)

    def close(self):
        self.setChannel(2)
        self.setDuty(100)
        self.setChannel(3)
        self.setDuty(0)  

    def release(self):
        self.setChannel(3)
        self.setDuty(0)
        self.setChannel(2)
        self.setDuty(0)  

##################################################################
class GasDetect:
    def __init__(self, pin = "D7"):
        self._pin = Pin(pin, Pin.IN)
            
    def read(self):
        return self._pin()