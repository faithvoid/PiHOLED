import time
import psutil
import requests
from luma.core.interface.serial import spi
from luma.oled.device import sh1106 # Change to ssd1306 if you're using an SSD1306 display
from luma.core.render import canvas
from PIL import ImageFont
from gpiozero import Button
from threading import Thread

# Constants
WIDTH = 128
HEIGHT = 64

# Pi-hole API endpoint
PIHOLE_API_URL = "http://127.0.0.1/admin/api.php?summaryRaw&auth=<YOURAUTHTOKEN>"

# Initialize the OLED device with SPI interface
serial = spi(device=0, port=0)  # Adjust the device and port numbers as needed
device = sh1106(serial, width=WIDTH, height=HEIGHT, rotate=2)  # Change to ssd1306 if you're using an SSD1306 display, and change rotate=2 to rotate=0 (or vice versa) to flip the display.

# Load font
font = ImageFont.load_default()

# Button GPIO pins
BUTTON1_PIN = 21  # GPIO pin for KEY1
BUTTON2_PIN = 20  # GPIO pin for KEY2
BUTTON3_PIN = 16  # GPIO pin for KEY3

# Joystick GPIO pins - Uncomment Up/Down/Press if adding your own functionality that requires it.
## JOYSTICK_UP_PIN = 6
## JOYSTICK_DOWN_PIN = 19
JOYSTICK_LEFT_PIN = 5
JOYSTICK_RIGHT_PIN = 26
## JOYSTICK_PRESS_PIN = 13

# Button objects
button1 = Button(BUTTON1_PIN, hold_time=3)
button2 = Button(BUTTON2_PIN, hold_time=3)
button3 = Button(BUTTON3_PIN, hold_time=3)

# Joystick objects - Uncomment Up/Down/Press if adding your own functionality that requires it.
## joystick_press = Button(JOYSTICK_PRESS_PIN, hold_time=0)
## joystick_up = Button(JOYSTICK_UP_PIN, hold_time=0)
## joystick_down = Button(JOYSTICK_DOWN_PIN, hold_time=0)
joystick_left = Button(JOYSTICK_LEFT_PIN, hold_time=0)
joystick_right = Button(JOYSTICK_RIGHT_PIN, hold_time=0)

# Brightness levels
brightness_levels = [0.1, 0.5, 1.0]  # Low, medium, high
current_brightness_index = 0

# Menu states
STATS_MENU = 0
NETWORK_MENU = 1
current_menu_state = STATS_MENU

# Function - Get Network Information
def get_network_info():
    try:
        stats = psutil.net_if_addrs()['wlan0']
        ip_address = [addr.address for addr in stats if addr.family == 2][0]
        return ip_address
    except:
        return "N/A"
        
# Function - Get PiHole Queries
def get_queries_info():
    try:
        response = requests.get(PIHOLE_API_URL)
        response.raise_for_status()  # Raise an exception for HTTP errors
        data = response.json()
        blocked_queries = data.get('ads_blocked_today', 'N/A')
        total_queries = data.get('dns_queries_today', 'N/A')
        return blocked_queries, total_queries
    except Exception as e:
        print(f"Error fetching queries info: {e}")
        return "N/A", "N/A"

# Function - Display System Information
def display_info(cpu_usage, ram_usage, sd_usage):
    with canvas(device) as draw:
        draw.text((0, 0), f"- PiHole | SYSTEM -", font=font, fill=255)
        draw.text((0, 10), f"CPU: {cpu_usage}%", font=font, fill=255)
        draw.text((0, 20), f"RAM: {ram_usage}%", font=font, fill=255)
        draw.text((0, 30), f"Storage: {sd_usage}%", font=font, fill=255)

# Function - Display Network Information
def display_network_info(ip_address, sent, recv, blocked_queries, total_queries):
    with canvas(device) as draw:
        draw.text((0, 0), f"- PiHole | NETWORK -", font=font, fill=255)
        draw.text((0, 10), f"IP: {ip_address}", font=font, fill=255)
        draw.text((0, 20), f"Sent: {sent} kB/s", font=font, fill=255)
        draw.text((0, 30), f"Recv: {recv} kB/s", font=font, fill=255)
        draw.text((0, 40), f"Queries: {total_queries}", font=font, fill=255)
        draw.text((0, 50), f"Blocked: {blocked_queries}", font=font, fill=255)

# Function - Display Brightness Cycling
def handle_brightness_cycle():
    global current_brightness_index
    current_brightness_index = (current_brightness_index + 1) % len(brightness_levels)
    device.contrast(int(255 * brightness_levels[current_brightness_index]))


# Functions - Button1, Button2, Button3, Joystick_Left, Joystick_Right functions
def handle_button1_hold():
    print("Button 1 held for 3 seconds")
    # Restart the Raspberry Pi
    print("Restarting!")
    time.sleep(1)  # Add a small delay before restarting to allow time for the message to be displayed
    device.cleanup()
    import os
    os.system("sudo reboot")

def handle_button2_hold():
    print("Button 2 held for 3 seconds")
    # Shutdown the Raspberry Pi
    print("Shutting down...")
    time.sleep(1)  # Add a small delay before shutting down to allow time for the message to be displayed
    device.cleanup()
    import os
    os.system("sudo shutdown now")

# Button3 Hold is commented out by default as it's not needed here (yet?). Feel free to uncomment it and use it in your own modifications though!

def handle_button3_hold():
    print("Button 3 held for 3 seconds")
    handle_brightness_cycle()

def handle_button3_press():
    print("Button 3 pressed")
    handle_brightness_cycle()

def handle_joystick_left():
    global current_menu_state
    current_menu_state -= 1
    if current_menu_state < 0:
        current_menu_state = 1  # Wrap around to the last menu state

def handle_joystick_right():
    global current_menu_state
    current_menu_state += 1
    if current_menu_state > 1:
        current_menu_state = 0  # Wrap around to the first menu state

# End of Button/Joystick Functions
        
# Assign button and joystick handlers
button1.when_held = handle_button1_hold
button2.when_held = handle_button2_hold
button3.when_pressed = handle_button3_press
joystick_left.when_pressed = handle_joystick_left
joystick_right.when_pressed = handle_joystick_right

# Main

def main():
    while True:
        ip_address = get_network_info()
        cpu_usage = psutil.cpu_percent()
        ram_usage = psutil.virtual_memory().percent
        sd_usage = psutil.disk_usage('/').percent  # Get storage usage percentage
        blocked_queries, total_queries = get_queries_info()

        if current_menu_state == STATS_MENU:
            display_info(cpu_usage, ram_usage, sd_usage)
        elif current_menu_state == NETWORK_MENU:
            # Get network stats
            network_info = psutil.net_io_counters()
            sent = round(network_info.bytes_sent / 1024, 2)  # Convert bytes to KB
            recv = round(network_info.bytes_recv / 1024, 2)  # Convert bytes to KB
            display_network_info(ip_address, sent, recv, blocked_queries, total_queries)

        time.sleep(5)  # Refresh every 5 seconds

if __name__ == "__main__":
    main()

pause()  # Keep the script running to handle button events
