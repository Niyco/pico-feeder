import machine
import time

brightness = 1
frequency = 100
assert 0 <= brightness and brightness <= 1

led = machine.Pin('LED', machine.Pin.OUT)
on_time = brightness / frequency
off_time = (1 - brightness) / frequency

try:
    while True:
        led.value(True)
        time.sleep(on_time)
        led.value(False)
        time.sleep(off_time)
finally:
    led.value(False)