#--------------------------------------------------------
# UART 
#--------------------------------------------------------
from pop import Uart

EOL_R = b'\r'
uart = Uart()

def readLine():
    buffer = ""
    
    while True:
        oneByte = uart.read(1)
        
        if oneByte == EOL_R:
            return buffer
        else:
            buffer += oneByte.decode()

def writeLine(buffer):
    uart.write(buffer + '\n')

#--------------------------------------------------------
# USER CODE 
#--------------------------------------------------------
from time import sleep
from machine import Pin

doorlock = None
light = None
fan = None

def setup():
    global doorlock, light, fan
    
    uart = Uart()
    writeLine("Starting...")
    
    doorlock = Pin('D0', Pin.OUT, value=0)    #릴레이 채널1 ('D0')
    light1 = Pin('D6', Pin.OUT, value=0)       #릴레이 채널2 ('D6')
    light2 = Pin('D5', Pin.OUT, value=0)         #릴레이 채널3 ('D5')

def loop():
    cmd = readLine().lower().split(" ")
            
    if cmd[0] == "doorlock":
        if len(cmd) == 1:
            doorlock.on()
            sleep(0.5)
            doorlock.off()
        else:
            writeLine("Unknown option")
    elif cmd[0] == "light1":
        if len(cmd) == 2:
            if cmd[1] == "on":
                light.on()
            elif cmd[1] == "off":
                light.off()
            else:
                writeLine("Unknown option")
        else:
            writeLine("Unknown command")
    elif cmd[0] == "light2":
        if len(cmd) == 2:
            if cmd[1] == "on":
                light.on()
            elif cmd[1] == "off":
                light.off()
            else:
                writeLine("Unknown option")
        else:
            writeLine("Unknown command")
    else:
        writeLine("Unknown command")

#--------------------------------------------------------
# MAIN 
#--------------------------------------------------------        
def main():
    setup()
    while True:
        loop()
        sleep(0.01)
    
if __name__ == '__main__':
    main()