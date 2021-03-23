# Based on the RGB Matrix Portal Room CO2 Monitor by Carter Nelson
# https://learn.adafruit.com/matrix-portal-room-co2-monitor
# emojis from https://onlineunicodetools.com/convert-emoji-to-image
# indexed bmp conversion at https://online-converting.com/image/convert2bmp/

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

text = "        "
font = bitmap_font.load_font("/SourceSansPro-Black-42.bdf")
color = 0xFFFFFF

# current condition label
text_label = label.Label(font, text=text, color=color, x=65, y=120)
# current CO2 value(good/poor/warning/danger)
digits_label = label.Label(font, text=text, color=color, x=75, y=160)
# current condition emoji
bitmap, palette = adafruit_imageload.load("/emojis.bmp")
emoji = displayio.TileGrid(
    bitmap,
    pixel_shader=palette,
    x=int((clue.display.width / 2) - 37),
    y=3,
    width=1,
    height=1,
    tile_width=72,
    tile_height=80,
)

co2_group = displayio.Group(max_size=4)
co2_group.append(emoji)
co2_group.append(text_label)
co2_group.append(digits_label)

def update_display(value):
    value = abs(round(value))
    digits_label.text = str(value)

    if value < CO2_CUTOFFS[0]:
        text_label.text = "GOOD"
        text_label.x = 65
        emoji[0] = 0
    elif value < CO2_CUTOFFS[1]:
        text_label.text = "POOR"
        text_label.x = 65
        emoji[0] = 1
    elif value < CO2_CUTOFFS[2]:
        text_label.text = "WARNING"
        text_label.x = 30
        emoji[0] = 3
    else:
        text_label.text = "DANGER"
        text_label.x = 40
        emoji[0] = 4

update_display(scd30.CO2)
clue.display.show(co2_group)

while True:
    if scd30.data_available:
        update_display(scd30.CO2)
    time.sleep(UPDATE_RATE)