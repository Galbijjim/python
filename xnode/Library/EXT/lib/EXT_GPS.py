from machine import I2C
import time

class _SC16IS750:
    def __init__(self, baud=9600):
        self._i2c = I2C(1)
        
        div = 12000000 // (baud * 16) #XNode crystal frequency: 12MHz 

        self._write(0x03, 0x80)          #Line Control Register, divisor latch enable(7bit)        
        self._write(0x00, div & 0xFF)    #Division Register LSB
        self._write(0x01, div >> 8)      #Division Register MSB
        self._write(0x03, 0x03)          #no parity(5~3bit) 0~1 stop bit(2bit), 8bit data(0~1bit)
        self.resetFIFO()
        
    def resetFIFO(self):
        self._write(0x02, 0x07) #FIFO Control Register, TX FIFO reset(2bit), RX FIFO reset(1bit), FIFO enable(0bit)

    def isReceive(self):
        return self._read(0x05) & 0b1    #Line Status Register, data in receiver(0bit)

    def available(self):
        return self._read(0x09) #Receive FIFO Level Register, 0~64

    def read(self):
        return self._read(0x00) #Receive Holding Register 
        
    def write(self, data):
        self._write(0x00, data) #Transmit Holding Register 

    def _read(self, reg):
        return self._i2c.readfrom_mem(0x9A >> 1, reg << 3, 1)[0]

    def _write(self, reg, data):
        self._i2c.writeto_mem(0x9A >> 1, reg << 3, bytes([data]))


class GPS:
    #NMEA Checksum Calculator: https://nmeachecksum.eqth.net/
    
    UPDATE_1HZ = "$PMTK220,1000*1F"
    UPDATE_2HZ = "$PMTK220,200*2C"
    #UPDATE_10HZ = "$PMTK220,100*2F"

    OUTPUT_GGA = "$PMTK314,0,0,0,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0*29"
    #OUTPUT_GSA = "$PMTK314,0,0,0,0,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0*29"
    OUTPUT_VTG = "$PMTK314,0,0,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0*29"
    OUTPUT_RMC = "$PMTK314,0,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0*29"    
    #OUTPUT_GSV = "$PMTK314,0,0,0,0,0,1,0,0,0,0,0,0,0,0,0,0,0,0,0*29" 
    
    BAUD_9600   = "$PMTK251,9600*17"
    BAUD_19200  = "$PMTK251,19200*22"
    #BAUD_38400  = "$PMTK251,38400*27"   #Do Not!!!
    #BAUD_115200 = "$PMTK251,115200*1F"  #Do Not!!!
        
    def __init__(self, __first=True):
        
        self._uart = _SC16IS750(9600)
        self.set_cmd(self.UPDATE_1HZ) 
            
        self._OUTPUT_MAX_LEN = 82
        self._buf = [None for _ in range(self._OUTPUT_MAX_LEN)]
        self._buf_pos = 0
        
        self._out = self.OUTPUT_GGA
        self.set_cmd(self._out)
    
    def setFastUpdate(self, fast=True):
        self.set_cmd(self.UPDATE_2HZ if fast else self.UPDATE_1HZ) 
    
    def setOutputMode(self, out):
        self._out = out
        self.set_cmd(self._out)
    
    def read(self):
        while self._buf_pos < self._OUTPUT_MAX_LEN:
            for _ in range(self._uart.available()):
                byte = self._uart.read()
                
                if byte == 36:  #'$'
                    self._buf_pos = 0
                    self._buf[self._buf_pos] = byte
                elif byte != 10: #'\n'
                    self._buf_pos += 1
                    self._buf[self._buf_pos] = byte
                elif byte == 10: 
                    t = bytes(self._buf[:self._buf_pos])
                    if "$PMTK" in t:
                        continue
                    return t
                
        return b''
    
    def parse(self):
        d = self.read().decode().split(',')
               
        if self._out == self.OUTPUT_GGA:
            try:
                return dict(id=d[0], utctime=d[1], latitude=d[2], ns_indicator=d[3], longitude=d[4], ew_indicator=d[5],
                            position_fix_indicator=d[6], satellites_used=d[7], hdop=d[8], msl_altitude=d[9],
                            units_a=d[10], geoidal_separation=d[11], units_g=d[12], age_diff_corr=d[13], checksum=d[14])
            except:
                return {}
        elif self._out == self.OUTPUT_RMC:
            try:
                return dict(id=d[0], utctime=d[1], status=d[2], latitude=d[3], ns_indicator=d[4], longitude=d[5], ew_indicator=d[6],
                            speed_over_ground=d[7], course_over_ground =d[8], date = d[9], magnetic_variation = d[10], magnetic_variation_indicator=d[11],
                            mode = d[12][0], checksum = d[12][1:])
            except:
                return {}
        elif self._out == self.OUTPUT_VTG:
            try:
                return dict(id=d[0], course_a=d[1], reference_a=d[2], course_b=d[3], reference_b=d[4], speed_n=d[5],
                            units_n=d[6], speed_k=d[7], units_k=d[8], mode=d[9][0],checksum = d[9][1:])
            except:
                return {}
        else:
            return {}

    def set_cmd(self, message):
        for i in range(len(message)):
            self._uart.write(ord(message[i]))
        self._uart.write(0xD)
        self._uart.write(0xA)
        time.sleep(1)
