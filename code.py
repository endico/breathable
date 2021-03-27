# Based on the RGB Matrix Portal Room CO2 Monitor by Carter Nelson
# https://learn.adafruit.com/matrix-portal-room-co2-monitor
# emojis from https://onlineunicodetools.com/convert-emoji-to-image
# indexed bmp conversion at https://online-converting.com/image/convert2bmp/
# https://learn.adafruit.com/adafruit-magtag-project-selector/code-run-through

import time
import board
import displayio
import adafruit_imageload
from adafruit_bitmap_font import bitmap_font
from adafruit_display_text import bitmap_label as label

from adafruit_clue import clue
import adafruit_scd30

# --| User Config |----
CO2_CUTOFFS = (1000, 2000, 5000)
UPDATE_RATE = 2
# ---------------------

# load bitmap early to make sure there is a large enough
# chunk of memory before any fragmentation occurs
bitmap, palette = adafruit_imageload.load("/emojis.bmp")

# the SCD30 CO2 sensor
# https://circuitpython.readthedocs.io/projects/scd30/en/latest/api.html
scd30 = adafruit_scd30.SCD30(board.I2C())

# If both buttons are pressed at startup then calibrate the sensor.
# Require user interaction to verify this wasn't accidental. If user
# doesn't release both buttons in 10 seconds then skip calibration
def calibrate():
    small_font = bitmap_font.load_font("Exo-SemiBold-18.pcf")
    small_font.load_glyphs(b'RPCabcdefghiklmnoqrstuwy1234567890,')
    color = 0xFFFFFF

    c_text_label = label.Label(
        small_font,
        text="",
        color=color,
        line_spacing=1.1,
        x=10,
        y=30,
        )
    c_timer_label = label.Label(
        small_font,
        text="",
        color=color,
        line_spacing=1.0,
        anchor_point=(0.5, 0.0),
        anchored_position=(clue.display.width / 2, 160),
        )
    group = displayio.Group(max_size=4)
    group.append(c_text_label)
    group.append(c_timer_label)
    clue.display.show(group)

    interaction_timer = 10
    while interaction_timer > 0:
        interaction_timer = interaction_timer - 1
        if (clue.button_a or clue.button_b):
            c_text_label.text = "Release\nbuttons to\nbegin calibration"
            c_timer_label.text = str(interaction_timer)
        else:
            while (clue.button_a or clue.button_b):
                pass
            c_timer_label.text = ""
            c_text_label.text = "Press button\nwhen you are\noutdoors"
            while not (clue.button_a or clue.button_b):
                pass
            while (clue.button_a or clue.button_b):
                pass
            c_text_label.text = "Press button\nwhen sensor is\nin the shade"
            while not (clue.button_a or clue.button_b):
                pass
            while (clue.button_a or clue.button_b):
                pass
            c_text_label.text = "Press button\nwhen sensor is\nprotected from\nthe wind"
            while not (clue.button_a or clue.button_b):
                pass
            while (clue.button_a or clue.button_b):
                pass
            c_text_label.text = "Press button,\nput down the\nsensor and stand\nback during\ncalibration"
            while not (clue.button_a or clue.button_b):
                pass
            c_text_label.text = "Calibrating"
            c_timer_label.text = " "
            wait_timer = 180  # wait at least 2 minutes for air to clear
            while wait_timer > 0:
                c_timer_label.text = str(wait_timer)
                wait_timer = wait_timer - 1
                time.sleep(1)
            c_timer_label.text = "0"
            scd30.forced_recalibration_reference = 400
            break
        time.sleep(0.25)
    c_timer_label.text = "0"
######################## End Calibrate Definition

# if both buttons are pressed on startup then calibrate CO2 sensor
if clue.button_a and clue.button_b:
    calibrate()

scd30.ambient_pressure = clue.pressure

font = bitmap_font.load_font("/SourceSansPro-Black-42.pcf")
font.load_glyphs(b'ADEGINNOPRRW1234567890')
color = 0xFFFFFF

# current condition label
text_label = label.Label(font, color=color, x=65, y=140)
# current CO2 value(good/poor/warning/danger)
digits_label = label.Label(font, color=color, x=35, y=180)
emoji = displayio.TileGrid(
    bitmap,
    pixel_shader=palette,
    x=int((clue.display.width / 2) - 37),
    y=23,
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
    digits_label.text = str(value) + " ppm"

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