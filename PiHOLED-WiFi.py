import time
import psutil
import requests
from luma.core.interface.serial import spi
from luma.oled.device import sh1106
from luma.core.render import canvas
from PIL import ImageFont

# Constants
WIDTH = 128
HEIGHT = 64

# Pi-hole API endpoint
PIHOLE_API_URL = "http://127.0.0.1/admin/api.php?summaryRaw&auth=<YOURAUTHTOKENHERE>"

# Initialize the OLED device with SPI interface
serial = spi(device=0, port=0)  # Adjust the device and port numbers as needed
device = sh1106(serial, width=WIDTH, height=HEIGHT)  # Change to ssd1306 if you're using an SSD1306 display

# Load font
font = ImageFont.load_default()

# Configuration
flip_screen = False  # Set to True to flip the screen 180 degrees

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
        if flip_screen:
            # Draw text flipped 180 degrees
            draw.text((WIDTH-1, HEIGHT-1), f"IP: {ip_address}", font=font, fill=255, anchor="rd")
            draw.text((WIDTH-1, HEIGHT-11), f"CPU %: {cpu_usage}%", font=font, fill=255, anchor="rd")
            draw.text((WIDTH-1, HEIGHT-21), f"RAM %: {ram_usage}%", font=font, fill=255, anchor="rd")
            draw.text((WIDTH-1, HEIGHT-31), f"Total Queries: {total_queries}", font=font, fill=255, anchor="rd")
            draw.text((WIDTH-1, HEIGHT-41), f"Blocked Queries: {blocked_queries}", font=font, fill=255, anchor="rd")
        else:
            draw.text((0, 0), f"IP: {ip_address}", font=font, fill=255)
            draw.text((0, 10), f"CPU %: {cpu_usage}%", font=font, fill=255)
            draw.text((0, 20), f"RAM %: {ram_usage}%", font=font, fill=255)
            draw.text((0, 30), f"Total Queries: {total_queries}", font=font, fill=255)
            draw.text((0, 40), f"Blocked Queries: {blocked_queries}", font=font, fill=255)

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
