import time
import psutil
import requests
from luma.core.interface.serial import spi
from luma.oled.device import sh1106
from luma.core.render import canvas
from PIL import ImageFont
from gpiozero import Button
from signal import pause

# Constants
WIDTH = 128
HEIGHT = 64

# Pi-hole API endpoint
PIHOLE_API_URL = "http://127.0.0.1/admin/api.php?summaryRaw&auth=<AUTHTOKENHERE>"

# Initialize the OLED device with SPI interface
serial = spi(device=0, port=0)  # Adjust the device and port numbers as needed
device = sh1106(serial, width=WIDTH, height=HEIGHT, rotate=2)  # Change to ssd1306 if you're using an SSD1306 display, change rotate between 0 & 2 to rotate 180 degrees.

# Load font
font = ImageFont.load_default()

# Button GPIO pins
BUTTON1_PIN = 21  # GPIO pin for KEY1
BUTTON2_PIN = 20  # GPIO pin for KEY2
BUTTON3_PIN = 16  # GPIO pin for KEY3

# Button objects, switch button1_pin & button3_pin if rotating display.
button1 = Button(BUTTON1_PIN, hold_time=3) # Restarts the Raspberry Pi.
button2 = Button(BUTTON2_PIN, hold_time=3) # Shuts down the Raspberry Pi.
button3 = Button(BUTTON3_PIN) # Adjusts display brightness 

# Brightness levels
brightness_levels = [0.1, 0.5, 1.0]  # Low, medium, high
current_brightness_index = 0

# Change "eth0" to "wlan0" (or your respective wireless card ID) if using a wireless network. 
def get_network_info():
    try:
        stats = psutil.net_if_addrs()['eth0']
        ip_address = [addr.address for addr in stats if addr.family == 2][0]
        return ip_address
    except:
        return "N/A"

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

def display_info(ip_address, cpu_usage, ram_usage, blocked_queries, total_queries):
    with canvas(device) as draw:
        draw.rectangle((0, 0, WIDTH - 1, HEIGHT - 1), outline=255)
        draw.text((0, 0), f"IP: {ip_address}", font=font, fill=255)
        draw.text((0, 10), f"CPU: {cpu_usage}%", font=font, fill=255)
        draw.text((0, 20), f"RAM: {ram_usage}%", font=font, fill=255)
        draw.text((0, 30), f"Total Queries: {total_queries}", font=font, fill=255)
        draw.text((0, 4c0), f"Blocked Queries: {blocked_queries}", font=font, fill=255)

def handle_brightness_cycle():
    global current_brightness_index
    current_brightness_index = (current_brightness_index + 1) % len(brightness_levels)
    device.contrast(int(255 * brightness_levels[current_brightness_index]))

def handle_button1_press():
    print("Button 1 pressed")

def handle_button1_hold():
    print("Button 1 held for 3 seconds")
    # Restart the Raspberry Pi
    print("Restarting!")
    time.sleep(1)  # Add a small delay before restarting to allow time for the message to be displayed
    device.cleanup()
    import os
    os.system("sudo reboot")

def handle_button2_press():
    print("Button 2 pressed")

def handle_button2_hold():
    print("Button 2 held for 3 seconds")
    # Shutdown the Raspberry Pi
    print("Shutting down.")
    time.sleep(1)  # Add a small delay before shutting down to allow time for the message to be displayed
    device.cleanup()
    import os
    os.system("sudo shutdown now")

def handle_button3_press():
    print("Button 3 pressed")
    handle_brightness_cycle()

# Assign button press and hold handlers
button1.when_pressed = handle_button1_press
button1.when_held = handle_button1_hold

button2.when_pressed = handle_button2_press
button2.when_held = handle_button2_hold

button3.when_pressed = handle_button3_press

def main():
    try:
        while True:
            ip_address = get_network_info()
            cpu_usage = psutil.cpu_percent()
            ram_usage = psutil.virtual_memory().percent
            blocked_queries, total_queries = get_queries_info()
            display_info(ip_address, cpu_usage, ram_usage, blocked_queries, total_queries)
            time.sleep(5)  # Refresh every 5 seconds
    except KeyboardInterrupt:
        pass

if __name__ == "__main__":
    main()

pause()  # Keep the script running to handle button events
