from machine import Pin, ADC
import utime

import usys
import ustruct as struct
from machine import Pin, SPI, SoftSPI
from nrf24l01 import NRF24L01
from micropython import const

if usys.platform == "rp2":  # Hardware SPI with explicit pin definitions
    spi = SPI(0, sck=Pin(18), mosi=Pin(19), miso=Pin(4))
    cfg = {"spi": spi, "csn": 5, "ce": 3}
else:
    raise ValueError("Unsupported platform {}".format(usys.platform))

pipes = (b"\xe1\xf0\xf0\xf0\xf0", b"\xd2\xf0\xf0\xf0\xf0")


def initiator():
    csn = Pin(cfg["csn"], mode=Pin.OUT, value=1)
    ce = Pin(cfg["ce"], mode=Pin.OUT, value=0)
    spi = cfg["spi"]
    nrf = NRF24L01(spi, csn, ce, payload_size=16)

    nrf.open_tx_pipe(pipes[0])
    nrf.open_rx_pipe(1, pipes[1])
    nrf.start_listening()

    num_needed = 160
    num_successes = 0
    num_failures = 0
    led_state = 0
    
    print("NRF24L01 initiator mode, sending %d packets..." % num_needed)

    while num_successes < num_needed and num_failures < num_needed:
        # stop listening and send packet
        nrf.stop_listening()
        
        millis = utime.ticks_ms()
        led_state = max(1, (led_state << 1) & 0x0F)
        #print("sending:", millis, millis2, led_state)
        
        xAxis = ADC(Pin(27))
        yAxis = ADC(Pin(26))
        button = Pin(16,Pin.IN, Pin.PULL_UP)
        xValue = xAxis.read_u16()
        xValue_ = yAxis.read_u16()
        yValue = yAxis.read_u16()
        yValue_ = xAxis.read_u16()
        print("sending:", xValue, yValue, xValue_, yValue_)
        
        try:
            nrf.send(struct.pack("iiii", xValue, yValue, xValue_, yValue_))
        except OSError:
            pass

        # start listening again
        nrf.start_listening()

        # wait for response, with 250ms timeout
        start_time = utime.ticks_ms()
        timeout = False
        while not nrf.any() and not timeout:
            if utime.ticks_diff(utime.ticks_ms(), start_time) > 200:
                timeout = True

        if timeout:
            print("failed, response timed out")
            num_failures += 1

        else:
            # recv packet
            (got_millis,) = struct.unpack("i", nrf.recv())

            # print response and round-trip delay
            print(
                "got response:",
                got_millis,
                "(delay",
                utime.ticks_diff(utime.ticks_ms(), got_millis),
                "ms)",
            )
            num_successes += 1

        # delay then loop
        utime.sleep_ms(200)

    print("initiator finished sending; successes=%d, failures=%d" % (num_successes, num_failures))
    
initiator()