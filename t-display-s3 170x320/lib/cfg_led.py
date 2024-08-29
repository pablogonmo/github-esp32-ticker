from machine import Pin, SPI

def config():
    return SPI(
        1,                   # SPI bus id (1 or 2 on ESP32)
        baudrate=1000000,    # SPI clock speed, 1 MHz is typically a good starting point
        polarity=0,          # Clock polarity
        phase=0,             # Clock phase
        sck=Pin(39),         # Clock pin
        mosi=Pin(40)         # Data pin
        )