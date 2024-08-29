from machine import Pin, Timer
import utime

class Buttons():
    def __init__(self, pin_number, short_press_callback, long_press_callback, double_click_callback, long_press_duration=2, double_click_duration=0.5):
        self.name = "t-display-s3"
        self.center = Pin(pin_number, Pin.IN, Pin.PULL_UP)

        self.short_press_callback = short_press_callback
        self.long_press_callback = long_press_callback
        self.double_click_callback = double_click_callback
        self.long_press_duration = long_press_duration
        self.double_click_duration = double_click_duration

        self.press_start_time = None
        self.last_press_time = None
        self.click_count = 0
        self.debounce_time = 50  # milliseconds

        self.single_click_timer = Timer(-1)  # Timer for single click

        self.center.irq(trigger=Pin.IRQ_FALLING | Pin.IRQ_RISING, handler=self._button_handler)

    def _button_handler(self, pin):
        current_time = utime.ticks_ms()

        # Debounce mechanism
        if self.press_start_time and utime.ticks_diff(current_time, self.press_start_time) < self.debounce_time:
            return

        if pin.value() == 0:  # Button pressed
            self.press_start_time = current_time
        else:  # Button released
            if self.press_start_time is not None:
                press_duration = utime.ticks_diff(current_time, self.press_start_time) / 1000
                self.press_start_time = None

                if press_duration >= self.long_press_duration:
                    self.long_press_callback()
                    self.click_count = 0  # Reset click count on long press
                else:
                    if self.last_press_time is not None and utime.ticks_diff(current_time, self.last_press_time) / 1000 <= self.double_click_duration:
                        self.click_count += 1
                    else:
                        self.click_count = 1

                    self.last_press_time = current_time

                    if self.click_count == 2:
                        self.single_click_timer.deinit()  # Cancel the single-click timer
                        self.double_click_callback()
                        self.click_count = 0  # Reset click count after double click
                    else:
                        # Set a timer to check for single click after double_click_duration
                        self.single_click_timer.init(period=int(self.double_click_duration * 1000), mode=Timer.ONE_SHOT, callback=self._handle_single_click)

    def _handle_single_click(self, timer):
        if self.click_count == 1:
            self.short_press_callback()
        self.click_count = 0  # Reset click count after handling the single click
