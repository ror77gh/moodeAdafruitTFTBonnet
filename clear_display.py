import board
from adafruit_rgb_display import st7789
from digitalio import DigitalInOut, Direction

# Standard SPI connections for ST7789
# Create ST7789 LCD display class.

cs_pin = DigitalInOut(board.CE0)
dc_pin = DigitalInOut(board.D25)
reset_pin = DigitalInOut(board.D24)
BAUDRATE = 24000000
spi = board.SPI()
disp = st7789.ST7789(
    spi,
    height=240,
    y_offset=80,
    rotation=180,
    cs=cs_pin,
    dc=dc_pin,
    rst=reset_pin,
    baudrate=BAUDRATE,
    )

disp.fill(0)
backlight = DigitalInOut(board.D26)
backlight.switch_to_output()
backlight.value = False
