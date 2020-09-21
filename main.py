"""
https://github.com/jantman/micropython-esp32-pulse-generator

GPIO 4
"""
from machine import Pin, Timer, PWM
from utime import sleep_ms
import micropython

micropython.alloc_emergency_exception_buf(100)

OPTIONS = [
    [0, 0, 'Off'],
    [0, 3000, '1/3 pps (20 ppm)'],
    [0, 1000, '1 pps (60 ppm)'],
    [0, 500, '2 pps (120 ppm)'],
    [0, 250, '4 pps (240 ppm)'],
    [1, 10, '10 pps (600 ppm)'],
    [1, 20, '20 pps (1,200 ppm)'],
    [1, 40, '40 pps (2,400 ppm)'],
    [1, 100, '100 pps (6,000 ppm)'],
    [1, 200, '200 pps (12,000 ppm)'],
    [1, 1000, '1,000 pps (60,000 ppm)'],
    [1, 5000, '5,000 pps (350,000 ppm)'],
    [1, 10000, '10,000 pps (600,000 ppm)'],
]


class PulseGenerator:

    def __init__(self):
        #self._pin = Pin(4, mode=Pin.OPEN_DRAIN, value=1, pull=Pin.PULL_DOWN)
        self._pin = Pin(4, mode=Pin.OUT, value=1, pull=Pin.PULL_DOWN)
        self._timer = None
        self._sleep_ms = 0
        self._pwm = None

    def reset(self):
        if self._timer is not None:
            self._timer.deinit()
            self._timer = None
        if self._pwm is not None:
            self._pwm.deinit()
            self._pwm = None
        self._pin.value(1)

    def run(self):
        while True:
            self.print_menu()
            try:
                value = int(input('Enter selection: '))
                selected = OPTIONS[value]
            except Exception:
                print('Invalid input')
                continue
            self.reset()
            if selected[0] == 0 and selected[1] == 0:
                self.reset()
            elif selected[0] == 0:
                self.handle_slow(selected[1])
            else:
                self.handle_fast(selected[1])
            print('Set to: %s' % selected[2])

    def print_menu(self):
        for idx, item in enumerate(OPTIONS):
            print('%d) %s' % (idx, item[2]))

    def handle_fast(self, freq):
        self._pwm = PWM(self._pin)
        self._pwm.freq(freq)
        self._pwm.duty(512)

    def handle_slow(self, sleep_ms):
        self._sleep_ms = sleep_ms
        self._timer = Timer(0)
        self._timer.init(
            period=self._sleep_ms, mode=Timer.ONE_SHOT,
            callback=self.slow_timer_callback
        )
        self.slow_timer_callback()

    def slow_timer_callback(self, *args):
        self._pin.value(0)
        sleep_ms(2)
        self._pin.value(1)
        self._timer.init(
            period=self._sleep_ms, mode=Timer.ONE_SHOT,
            callback=self.slow_timer_callback
        )


if __name__ == "__main__":
    PulseGenerator().run()
