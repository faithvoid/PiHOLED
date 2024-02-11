# PiHOLED
PiHOLED is a basic, no frills Python script to display PiHole &amp; Raspberry Pi hardware statistics on SH1106-based 1.3 inch (128x64) OLED display HATs, such as the Waveshare 1.3inch OLED Raspberry Pi HAT (can be modified to run on SSD1306-based HATs). Tested on a Raspberry Pi Zero W running DietPi but should theoretically work on any SBC + distro combination with a similar GPIO pinout. 

Supports safe reboot by holding KEY1 for 3 seconds, safe shutdown by holding KEY2 for 3 seconds, rotating between brightness settngs with KEY3, and switching between system / network statistics using the joystick (left + right).

![](1.jpg)
![](2.jpg)
<p align="center"><i> An aesthetically modified build of PiHOLED using the supErphoniX2 font. </i> </p>

## Requirements:
- SPI + I2C enabled in DietPi/Raspbian (or similar distro)
- python3
- python3-pip
- libopenjp2-7
- psutil (pip)
- requests (pip)
- luma.oled (pip)
- gpiozero (pip)


To install these on DietPi, install Python & RPi.GPIO via the DietPi Software installer & afterwards type "sudo apt install libopenjp2-7 && pip3 install psutil requests luma.oled" into your terminal. 

For non-DietPi users, type "sudo apt install python3 python3-pip libopenjp2-7 && pip3 install psutil requests luma.oled gpiozero" instead, and modify the .service file to reflect your username.

## How to install:
- Download PiHOLED.py
- Copy PiHOLED.py to your /home/dietpi directory
- Edit PiHOLED.py & replace <YOURAUTHTOKEN> with your the contents of "WEBPASSWORD" in "/etc/pihole/setupVars.con".
- Copy the PiHOLED.service script to /lib/systemd/system
- Type "systemctl enable PiHOLED && systemctl start PiHOLED"

## Configuration:
- Rotate Screen: You can rotate the screen 180 degrees by finding "rotate=2" and changing it to "rotate=0" (or vice versa).

## How to use with SSD1306-based HAT:
- Open PiHOLED.py in Nano or a similar text editor
- Change these two lines to the following:
- "from luma.oled.device import sh1106" -> "from luma.oled.device import ssd1306"
- "device = sh1106(serial, width=WIDTH, height=HEIGHT, rotate=2)"  -> "device = ssd1306(serial, width=WIDTH, height=HEIGHT, rotate=2)"

## TBD:
- Choose better font for increased visual clarity. (supErphoniX2 works great at size 9 but it's not open-source).
- Add music section as third page
- Merge this project + RetroSTATS (RetroPie stats can be page 4?)

## Bugs:
- TBA

Any and all feedback (optimizations, etc) is appreciated! Although feature requests will most likely be ignored as the scope of this project (basic PiHole + Pi statistics) has largely been covered already.
