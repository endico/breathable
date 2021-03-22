# Based on the RGB Matrix Portal Room CO2 Monitor by Carter Nelson
# https://learn.adafruit.com/matrix-portal-room-co2-monitor

import time
import board
import displayio
import adafruit_imageload
from adafruit_bitmap_font import bitmap_font
from adafruit_display_text import label
from adafruit_clue import clue
import adafruit_scd30

# --| User Config |----
CO2_CUTOFFS = (1000, 2000, 5000)
UPDATE_RATE = 2
# ---------------------

# the SCD30 CO2 sensor
# https://circuitpython.readthedocs.io/projects/scd30/en/latest/api.html
scd30 = adafruit_scd30.SCD30(board.I2C())
scd30.ambient_pressure = clue.pressure

print("display width", clue.display.width)
print("display height", clue.display.height)
print(f'clue.pressure:{clue.pressure}')
print(f'clue.altitude:{clue.altitude}')
print(f'clue.sea_level_pressure:{clue.sea_level_pressure}')
# print(f'dir(clue){dir(clue)}')

text = "        "
font = bitmap_font.load_font("/SourceSansPro-Black-42.bdf")
color = 0xFFFFFF

# current condition label
text_label = label.Label(font, text=text, color=color, x=70, y=120)
# current CO2 value(good/poor/warn/dang)
digits_label = label.Label(font, text=text, color=color, x=70, y=160)

co2_group = displayio.Group(max_size=4)
co2_group.append(text_label)
co2_group.append(digits_label)

def update_display(value):
    value = abs(round(value))
    digits_label.text = str(value)

    if value < CO2_CUTOFFS[0]:
        text_label.text = "GOOD"
        bitmap, palette = adafruit_imageload.load("/bmps/thumbsup.bmp",
                                                  bitmap=displayio.Bitmap,
                                                  palette=displayio.Palette)
    elif value < CO2_CUTOFFS[1]:
        text_label.text = "POOR"
        bitmap, palette = adafruit_imageload.load("/bmps/mask.bmp",
                                                  bitmap=displayio.Bitmap,
                                                  palette=displayio.Palette)
    elif value < CO2_CUTOFFS[2]:
        text_label.text = "WARNING"
        bitmap, palette = adafruit_imageload.load("/bmps/scream.bmp",
                                                  bitmap=displayio.Bitmap,
                                                  palette=displayio.Palette)
    else:
        text_label.text = "DANGER"
        bitmap, palette = adafruit_imageload.load("/bmps/skull.bmp",
                                                  bitmap=displayio.Bitmap,
                                                  palette=displayio.Palette)
    emoji = displayio.TileGrid(bitmap, pixel_shader=palette)
    emoji.x = int( (clue.display.width / 2) - 37 )
    emoji.y = 3
    co2_group.append(emoji)
clue.display.show(co2_group)

print("scd30.temperature:", scd30.temperature, "degrees C")
print("scd30.relative_humidity:", scd30.relative_humidity, "%rH")
print("scd30.altitude:", scd30.altitude, "")
print("scd30.ambient_pressure:", scd30.ambient_pressure)

while True:
    if scd30.data_available:
        # protect against NaNs and Nones
        try:
            update_display(scd30.CO2)
        except:
            pass
        time.sleep(UPDATE_RATE)