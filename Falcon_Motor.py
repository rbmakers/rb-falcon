# PWM Control Example
#
# This example shows how to do PWM with your OpenMV Cam.

import time
from pyb import Pin, Timer

tim4 = Timer(4, freq=1000) # Frequency in Hz
tim5 = Timer(5, freq=1000)

# Generate a 1KHz square wave on TIM4 with 50%, 75% and 50% duty cycles on channels 1, 2 and 3 respectively.
ch1 = tim5.channel(3, Timer.PWM, pin=Pin("M1"), pulse_width_percent=5)
#ch2 = tim5.channel(4, Timer.PWM, pin=Pin("M2"), pulse_width_percent=35)
#ch3 = tim4.channel(3, Timer.PWM, pin=Pin("M3"), pulse_width_percent=5)
#ch4 = tim4.channel(4, Timer.PWM, pin=Pin("M4"), pulse_width_percent=15)

while (True):
    time.sleep_ms(1000)
