from machine import ADC, I2C
import time 

class Textlcd:
    LCD_WIDTH = 16		
    LCD_CMD = 0x00
    LCD_CHR = 0x01
    LCD_LINE1 = 0x00
    LCD_LINE2 = 0x40
    LCD_CLEAR = 0x01
    LCD_HOME = 0x02
    LCD_DISPLAY = 0x04
    LCD_CURSOR = 0x02
    LCD_BLINKING = 0x01
    LCD_DISPLAY_SHIFT_R = 0x1C
    LCD_DISPLAY_SHIFT_L = 0x18
    LCD_CURSOR_SHIFT_R = 0x14
    LCD_CURSOR_SHIFT_L = 0x10
    LCD_ENTRY_MODE_SET = 0x06
    LCD_BACKLIGHT = 0x08
    ENABLE = 0x04
    def __init__(self):
        self._i2c = I2C(1, freq = 300000)
        self.command(0x33)
        self.command(0x32)
        self.command(0x28)
        self.command(0x0F)
        self.command(0x06)
        self.command(0x01)
        time.sleep(0.1)
        self.display_status = 0x0F
        self.returnHome()

    def __del__(self):
        self.display_status = 0x00

    def _byte(self, byte, mode):
        high_bit = mode | (byte & 0xF0) | self.LCD_BACKLIGHT
        low_bit = mode | ((byte << 4) & 0xF0) | self.LCD_BACKLIGHT
        self._enable(high_bit)
        self._enable(low_bit)

    def _enable(self, byte):
        time.sleep(0.005)
        self._i2c.writeto(0x27, bytes([byte | self.ENABLE]))
        time.sleep(0.005)
        self._i2c.writeto(0x27, bytes([byte & ~self.ENABLE]))
        time.sleep(0.005)
        
    def command(self, command):
        self._byte(command,self.LCD_CMD)

    def clear(self):
        self.command(self.LCD_CLEAR)

    def returnHome(self):
        self.command(self.LCD_HOME)

    def displayOn(self):
        self.display_status = self.display_status | self.LCD_DISPLAY
        self.command(self.display_status)

    def displayOff(self):
        self.display_status = self.display_status & ~self.LCD_DISPLAY
        self.command(self.display_status)

    def displayShiftR(self):
        self.command(self.LCD_DISPLAY_SHIFT_R)

    def displayShiftL(self):
        self.command(self.LCD_DISPLAY_SHIFT_L)

    def cursorOn(self, blinking):
        self.display_status = self.display_status | self.LCD_CURSOR
        if blinking == 1:
            self.display_status = self.display_status | self.LCD_BLINKING
        else:
            self.display_status = self.display_status & ~self.LCD_BLINKING

        self.command(self.display_status)

    def cursorOff(self):
        self.display_status = self.display_status & ~self.LCD_CURSOR
        self.display_status = self.display_status & ~self.LCD_BLINKING
        self.command(self.display_status)

    def cursorShiftR(self):
        self.command(self.LCD_CURSOR_SHIFT_R)

    def cursorShiftL(self):
        self.command(self.LCD_CURSOR_SHIFT_L)

    def entryModeSet(self):
        self.command(self.LCD_ENTRY_MODE_SET)

    def setCursor(self, x, y):
        if x > 15:
            x = 15
        if y >= 1:
            y = self.LCD_LINE2
        else:
            y = self.LCD_LINE1
        self.command(0x80 | (x+y))

    def data(self, data):
        self._byte(data, self.LCD_CHR)

    def print(self, str):
        for i in str:
            self.data(ord(i))

class Power:
    def __init__(self):
        self.adc = ADC("D0")
        
    def _clacVolt(self,adcRaw):
        return (adcRaw*3.3/4095)
    
    def _calcAmpere(self,adcRaw):
        return (2.5-(adcRaw*3.3/4095))/0.610 
    
    def _calcWatt(self,adcRaw):
        return (adcRaw*3.3/4095) * ((2.5-(adcRaw*3.3/4095))/0.610) 
    
    def read(self):
        return self.adc.read()
    
    def readVolt(self):
        return self._clacVolt(self.read())
    
    def readAmpere(self):
        return self._calcAmpere(self.read())
    
    def readWatt(self):
        return self._calcWatt(self.read())  