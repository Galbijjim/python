import time
import struct

from machine import Pin, I2C, ADC

import xbee as xnode
from digi import ble

try:
    from HOME_Power import Power, Textlcd
except:
    pass
try:
    from HOME_Door import Pir, DoorLock
except:
    pass
try:
    from HOME_Kitchen import GasDetect, GasBreaker
except:
    pass
try:
    from HOME_Actuator import FAN, Light
except:
    pass   
try:
    from EXT_Basic import Buttons, Leds, Buzzer
except:
    pass
try:
    from EXT_PIR import Pir
except:
    pass
try:
    from EXT_IRThermo import IRThermo
except:
    pass
try:
    from EXT_IMU import IMU
except:
    pass
try:
    from EXT_GPS import GPS
except:
    pass

from uos import urandom

def rand():
    return int.from_bytes(urandom(4), "big")

def sqrt(src):
    t = src
    for k in range(16):
        if t < 1.0:
            break
        t = (t*t + src) / (2.0*t)
    return t

from sys import stdin
from sys import stdout 

class Uart:            
    def read(self, num = None):
        if num is None : 
            return stdin.buffer.read()
        else: 
            return stdin.buffer.read(num)
    
    def write(self, n):
        stdout.buffer.write(n)    

class Led:
    def __init__(self):
        self._pin = Pin("D9", Pin.OUT, value=1)

    def on(self):
        self._pin(0)

    def off(self):
        self._pin(1)
    
    def stat(self):
        return self._pin() == 0

class Battery:
    def __init__(self):
        self.adc = ADC("D2")

    def read(self):
        return round(((self.adc.read() * 3.3 / 4095) * (3.2/2)), 1)

class AmbientLight:
    def __init__(self, cont=False):
        self.cont = cont
        self._i2c = I2C(1)
        
        # init
        self._i2c.writeto(0x23, bytes([0x01])) #power on
        self._i2c.writeto(0x23, bytes([0x07])) #reset
        
        if self.cont:
            self._i2c.writeto(0x23, bytes([0x11])) #cont_hires_2 mode
            time.sleep(0.180)

    def stop(self):
        self._i2c.writeto(0x23, bytes([0x00])) #power down
            
    def read(self):
        if not self.cont:
            self._i2c.writeto(0x23, bytes([0x21])) #one_hires_2 mode
            time.sleep(0.180)
            
        data = self._i2c.readfrom(0x23, 2)
        return round((data[0] << 8 | data[1]) / (1.2 * 2)) 
    
#--------------------------------------------------------------------

class Tphg:
    def __init__(self):
        self._i2c = I2C(1)

        self._i2c.writeto_mem(0x77, 0xE0, bytes([0xB6]))  #reset
        time.sleep(0.01)        
        
        # set calibration data
        calibration = self._i2c.readfrom_mem(0x77, 0x89, 25) #coeff_addr1
        calibration += self._i2c.readfrom_mem(0x77, 0xE1, 16) #coeff_addr2
        
        calibration = list(struct.unpack("<hbBHhbBhhbbHhhBBBHbbbBbHhbb", bytes(calibration[1:39])))
        calibration = [float(i) for i in calibration]

        self._temp_calibration = [calibration[x] for x in [23, 0, 1]]
        self._pressure_calibration = [calibration[x] for x in [3, 4, 5, 7, 8, 10, 9, 12, 13, 14]]
        self._humidity_calibration = [calibration[x] for x in [17, 16, 18, 19, 20, 21, 22]]
        self._humidity_calibration[0] /= 16 # flip around H1 & H2
        self._humidity_calibration[1] *= 16
        self._humidity_calibration[1] += self._humidity_calibration[0] % 16
        self._sw_err = (self._i2c.readfrom_mem(0x77, 0x04, 1)[0] & 0xF0) / 16
        
        # set res_heat_0, gas_wait_0       
        self._i2c.writeto_mem(0x77, 0x5A, bytes([0x73])) #res_heat_0 (320 Celsius. ref: datasheet 3.3.5(21pg)) 
        self._i2c.writeto_mem(0x77, 0x64, bytes([0x65])) #gas_wait_0 (b01 100101 = 4 x 37 = 148ms))

        self._i2c.writeto_mem(0x77, 0x75, bytes([0b010 << 2])) #config (filter)
        self._i2c.writeto_mem(0x77, 0x74, bytes([(0b100 << 5) | (0b011 << 2)])) #ctrl_meas(temp, pressure oversample), osrs_p<4:2>,osrs_t<7:5>
        self._i2c.writeto_mem(0x77, 0x72, bytes([0b010])) #ctrl_humi(humidity oversample)
        self._i2c.writeto_mem(0x77, 0x71, bytes([0x10])) #ctrl_gas_1(nb_conv<3:0>:000, run_gas<4>:1)
        
        self._t_fine = None
        self._adc_pres = None
        self._adc_hum = None
        self._adc_gas = None
        self._gas_range = None
        
    def _temperature(self):
        calc_temp = ((self._t_fine * 5) + 128) / 256
        return calc_temp / 100

    def _pressure(self):
        var1 = (self._t_fine / 2) - 64000
        var2 = ((var1 / 4) * (var1 / 4)) / 2048
        var2 = (var2 * self._pressure_calibration[5]) / 4
        var2 = var2 + (var1 * self._pressure_calibration[4] * 2)
        var2 = (var2 / 4) + (self._pressure_calibration[3] * 65536)
        var1 = ((((var1 / 4) * (var1 / 4)) / 8192) * (self._pressure_calibration[2] * 32) / 8) + ((self._pressure_calibration[1] * var1) / 2)
        var1 = var1 / 262144
        var1 = ((32768 + var1) * self._pressure_calibration[0]) / 32768
        calc_pres = 1048576 - self._adc_pres
        calc_pres = (calc_pres - (var2 / 4096)) * 3125
        calc_pres = (calc_pres / var1) * 2
        var1 = (self._pressure_calibration[8] * (((calc_pres / 8) * (calc_pres / 8)) / 8192)) / 4096
        var2 = ((calc_pres / 4) * self._pressure_calibration[7]) / 8192
        var3 = (((calc_pres / 256) ** 3) * self._pressure_calibration[9]) / 131072
        calc_pres += (var1 + var2 + var3 + (self._pressure_calibration[6] * 128)) / 16
        return calc_pres / 100

    def _humidity(self):
        temp_scaled = ((self._t_fine * 5) + 128) / 256
        var1 = (self._adc_hum - (self._humidity_calibration[0] * 16)) - ((temp_scaled * self._humidity_calibration[2]) / 200)
        var2 = (self._humidity_calibration[1] * (((temp_scaled * self._humidity_calibration[3]) / 100) + 
                (((temp_scaled * ((temp_scaled * self._humidity_calibration[4]) / 100)) / 64) / 100) + 16384)) / 1024
        var3 = var1 * var2
        var4 = self._humidity_calibration[5] * 128
        var4 = (var4 + ((temp_scaled * self._humidity_calibration[6]) / 100)) / 16
        var5 = ((var3 / 16384) * (var3 / 16384)) / 1024
        var6 = (var4 * var5) / 2
        calc_hum = (((var3 + var6) / 1024) * 1000) / 4096
        calc_hum /= 1000 
        return 100 if calc_hum > 100 else 0 if calc_hum < 0 else calc_hum

    def _gas(self):
        LOOKUP_TABLE_1 = (2147483647.0, 2147483647.0, 2147483647.0, 2147483647.0, 2147483647.0, 2126008810.0, 2147483647.0, 
            2130303777.0, 2147483647.0, 2147483647.0, 2143188679.0, 2136746228.0, 2147483647.0, 2126008810.0, 2147483647.0, 2147483647.0)

        LOOKUP_TABLE_2 = (4096000000.0, 2048000000.0, 1024000000.0, 512000000.0, 255744255.0, 127110228.0,
            64000000.0, 32258064.0, 16016016.0, 8000000.0, 4000000.0, 2000000.0, 1000000.0, 500000.0, 250000.0, 125000.0)

        var1 = ((1340 + (5 * self._sw_err)) * (LOOKUP_TABLE_1[self._gas_range])) / 65536
        var2 = ((self._adc_gas * 32768) - 16777216) + var1
        var3 = (LOOKUP_TABLE_2[self._gas_range] * var1) / 512
        calc_gas_res = (var3 + (var2 / 2)) / var2
        return int(calc_gas_res)
    
    def _perform_reading(self):        
        ctrl = self._i2c.readfrom_mem(0x77, 0x74, 1)[0] #ctrl_meas
        ctrl = (ctrl & 0xFC) | 0x01  # ctrl_meas, mode<1:0>
        self._i2c.writeto_mem(0x77, 0x74, bytes([ctrl])) #ctrl_temp
        
        new_data = False
        while not new_data:
            data = self._i2c.readfrom_mem(0x77, 0x1D, 15) #meas_status_0
            new_data = data[0] & 0x80 != 0
            time.sleep(0.005)
        
        self._adc_pres = ((data[2] * 4096) + (data[3] * 16) + (data[4] / 16))
        _adc_temp = ((data[5] * 4096) + (data[6] * 16) + (data[7] / 16))
        self._adc_hum = struct.unpack(">H", bytes(data[8:10]))[0]
        self._adc_gas = int(struct.unpack(">H", bytes(data[13:15]))[0] / 64)
        self._gas_range = data[14] & 0x0F

        var1 = (_adc_temp / 8) - (self._temp_calibration[0] * 2)
        var2 = (var1 * self._temp_calibration[1]) / 2048
        var3 = ((var1 / 2) * (var1 / 2)) / 4096
        var3 = (var3 * self._temp_calibration[2] * 16) / 16384
        self._t_fine = int(var2 + var3)
           
    def read(self):
        self._perform_reading()
        return round(self._temperature(), 2), round(self._pressure(), 2), round(self._humidity(), 2), self._gas() 

    def sealevel(self, altitude):
        self._perform_reading()
        press = self._pressure()
        return press / pow((1-altitude/44330), 5.255), press
    
    def altitude(self, sealevel): 
        self._perform_reading()
        press = self._pressure()
        return 44330 * (1.0-pow(press/sealevel,0.1903)), press
    
#--------------------------------------------------------------------
