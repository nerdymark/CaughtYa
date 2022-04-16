import machine
from machine import Timer
from time import sleep
 
interruptCounter = 0
totalInterruptsCounter = 0
 
def callback(pin):
    global interruptCounter
    interruptCounter = interruptCounter+1

def total(t):
    frequency = count
    count = 0
 
buzz = machine.Pin(22, machine.Pin.IN, machine.Pin.PULL_UP)
buzz.irq(trigger=machine.Pin.IRQ_FALLING, handler=callback)
button = machine.Pin(20, machine.Pin.OUT)

# Press button to start pairing
sleep(1)
button(True)
sleep(1)
button(False)


while True:
 
    if interruptCounter>0:

        state = machine.disable_irq()
        interruptCounter = interruptCounter-1
        machine.enable_irq(state)

        totalInterruptsCounter = totalInterruptsCounter+1

        # Time it - Does not work yet.......
        # TODO: Use Timer to decode buzzes.
        timer = Timer(-1)
        timer.init(period=1000, mode=Timer.PERIODIC, callback=total)

        sleep(1)
        print(frequency)
        button(True)


    else:
        # Send to Mu plotter
        sleep(1)
        button(False)
