import time
import threading
import serial
import sys
import signal
from serial.tools import list_ports
from pystray import Icon, Menu, MenuItem
from PIL import Image, ImageDraw
from datetime import datetime
from joinlog import log, check_for_updates, read_new_logs, extract_player_events


# Function to find and initialize the serial connection
def initialize_serial_connection():
    ports = list_ports.comports()
    device = [info for info in ports if "CH340" in info.description]
    if device:
        ser = serial.Serial(device[0].device, 115200)
        log(f"Connected to serial port: {device[0].device}")
        timestamp = datetime.now().strftime("%Y/%m/%d %H:%M:%S")
        send_serial_data(f"[{timestamp}][Serial] Serial connection established", ser)
        return ser
    else:
        log("CH340 device not found")
        return None

# Function to send data over serial and log the sent data
def send_serial_data(data, ser=None):
    if ser is None:
        ser = globals().get('ser')
    if ser:
        ser.write(data.encode('utf-8'))
        ser.write(b'\n')
        log(f"Sent data over serial: {data}")

# Function to handle quitting the application
def quit_app(icon, item):
    global running
    running = False
    if ser:
        timestamp = datetime.now().strftime("%Y/%m/%d %H:%M:%S")
        send_serial_data(f"[{timestamp}][Serial] Serial connection is closing", ser)
        ser.close()
    icon.stop()
    sys.exit()

# Function to handle reconnecting the serial connection
def reconnect_serial(icon, item):
    global ser
    if ser:
        ser.close()
    ser = initialize_serial_connection()

# Signal handler for clean exit
def signal_handler(sig, frame):
    quit_app(icon, None)

# Register signal handlers
signal.signal(signal.SIGINT, signal_handler)
signal.signal(signal.SIGTERM, signal_handler)

# Initialize the serial connection
ser = initialize_serial_connection()

timestamp = datetime.now().strftime("%Y/%m/%d %H:%M:%S")
print(f"[{timestamp}][Start] Welcome to Flow Deck CYD!")

# Create an icon and menu for the system tray
try:
    image = Image.open(r'resources\icon.ico')
except Exception as e:
    log(f"Icon file not found: {e}")
    # Create a default icon if the specified icon is not found
    image = Image.new('RGB', (64, 64), color=(73, 109, 137))
    draw = ImageDraw.Draw(image)
    draw.rectangle([0, 0, 64, 64], fill=(255, 255, 255))

menu = Menu(
    MenuItem('Reconnect', reconnect_serial),
    MenuItem('Quit', quit_app)
)
icon = Icon(name='FlowDeckCYD', icon=image, title='FlowDeckCYD', menu=menu)

# Function to run the icon in a separate thread
def run_icon():
    icon.run()

# Start the icon in a separate thread
icon_thread = threading.Thread(target=run_icon)
icon_thread.daemon = True  # Allow the program to exit when the main thread exits
icon_thread.start()

# Flag to control the running state
running = True

# Main loop to monitor log file for updates
def monitor_logs():
    while running:
        if check_for_updates():
            new_logs = read_new_logs()
            entries = extract_player_events(new_logs)
            for entry in entries:
                print(entry)
                send_serial_data(entry)
        time.sleep(1)  # Wait for 1 second before checking again

monitor_logs_thread = threading.Thread(target=monitor_logs)
monitor_logs_thread.daemon = True  # Allow the program to exit when the main thread exits
monitor_logs_thread.start()

# Keep the main thread running to allow the tray icon to function
try:
    while running:
        time.sleep(1)
except (KeyboardInterrupt, SystemExit):
    quit_app(icon, None)
