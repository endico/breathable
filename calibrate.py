# https://learn.adafruit.com/adafruit-scd30/field-calibration
# https://www.sensirion.com/fileadmin/user_upload/customers/sensirion/Dokumente/9.5_CO2/Sensirion_CO2_Sensors_SCD30_Field_Calibration.pdf

import time
import board
import displayio
from adafruit_bitmap_font import bitmap_font
from adafruit_display_text import bitmap_label as label
from adafruit_clue import clue
import adafruit_scd30
import supervisor

scd30 = adafruit_scd30.SCD30(board.I2C())
font = bitmap_font.load_font("Exo-SemiBold-18.pcf")
font.load_glyphs(b'RPCabcdefghiklmnoqrstuwy1234567890,')
color = 0xFFFFFF

text_label = label.Label(
    font,
    text=" ",
    color=color,
    line_spacing=1.1,
    x=10,
    y=30,
    )
timer_label = label.Label(
    font,
    text="",
    color=color,
    line_spacing=1.0,
    anchor_point=(0.5, 0.0),
    anchored_position=(clue.display.width / 2, 160),
    )
group = displayio.Group(max_size=4)
group.append(text_label)
group.append(timer_label)
clue.display.show(group)

initiation_timer = 10
while initiation_timer > 0:
    initiation_timer = initiation_timer - 1
    if (clue.button_a or clue.button_b) :
        text_label.text = "Release\nbuttons to\nbegin calibration"
        timer_label.text = str(initiation_timer)
    else:
        while (clue.button_a or clue.button_b):
            pass
        timer_label.text = " "
        text_label.text = "Press button\nwhen you are\noutdoors"
        while not (clue.button_a or clue.button_b):
            pass
        while (clue.button_a or clue.button_b):
            pass
        text_label.text = "Press button\nwhen sensor is\nin the shade"
        while not (clue.button_a or clue.button_b):
            pass
        while (clue.button_a or clue.button_b):
            pass
        text_label.text = "Press button\nwhen sensor is\nprotected from\nthe wind"
        while not (clue.button_a or clue.button_b):
            pass
        while (clue.button_a or clue.button_b):
            pass
        text_label.text = "Press button,\nput down the\nsensor and stand\nback during\ncalibration"
        while not (clue.button_a or clue.button_b):
            pass
        text_label.text = "Calibrating"
        timer_label.text = " "
        wait_timer = 180 # wait at least 2 minutes for air to clear
        while wait_timer > 0:
            timer_label.text = str(wait_timer)
            wait_timer = wait_timer - 1
            time.sleep(1)
        timer_label.text = "0"
        scd30.forced_recalibration_reference = 400
        break
    time.sleep(0.25) # sleep while waiting to verify this wasn't accidental
timer_label.text = "0"
supervisor.reload()