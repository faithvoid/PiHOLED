# PiHOLED
PiHOLED is a basic, no frills Python script to display PiHole &amp; Raspberry Pi hardware statistics on SH1106-based 1.3 inch OLED display HATs (can be modified to run on SSD1306-based. 

## Requirements:
- TBA

## How to install:
- Download PiHOLED or PiHOLED-WiFi (depending on whether you're using a wired or wireless connection)
- Copy the corresponding PiHOLED.py to your /home/dietpi directory
- Copy the PiHOLED.service script to /lib/systemd/system
- Type "systemctl enable PiHOLED && systemctl enable PiHOLED

## How to use with SSD1306-based HAT:
- Open PiHOLED.py in Nano or a similar text editor
- Change these two lines to the following:
- "from luma.oled.device import sh1106" -> "from luma.oled.device import ssd1306"
- device = sh1106(serial, width=WIDTH, height=HEIGHT)  -> "device = ssd1306(serial, width=WIDTH, height=HEIGHT)"

- ## Bugs:
- TBA
