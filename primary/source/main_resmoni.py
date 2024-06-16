import time
import threading
import serial
from serial.tools import list_ports
from joinlog import log, check_for_updates, read_new_logs, extract_player_events
from monitor import format_system_stats
from pystray import Icon, Menu, MenuItem
from PIL import Image
import win32gui
import win32con
from datetime import datetime

enable_resource_monitor = True  # Flag to enable/disable resource monitor
enable_resource_monitor_display = False # Flag to enable/disable resource monitor display

# Function to find and initialize the serial connection
def initialize_serial_connection():
    ports = list_ports.comports()
    device = [info for info in ports if "CH340" in info.description]
    if device:
        ser = serial.Serial(device[0].device, 115200)
        log(f"Connected to serial port: {device[0].device}")
        # Send initial message upon successful connection
        send_serial_data("Serial connection established", ser)
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
        ser.write(b'\n')  # Optional: send a newline character after the data
        log(f"Sent data over serial: {data}")

def forground(hwnd, title):
    global window_id
    name = win32gui.GetWindowText(hwnd)
    if name.find(title) >= 0:
        window_id = hwnd

        win32gui.ShowWindow(window_id, win32con.SW_MINIMIZE)

def forground_console():
    if win32gui.IsIconic(window_id):
        win32gui.ShowWindow(window_id,1)

# Function to handle quitting the application
def quit_app(icon, item):
    icon.stop()
    if ser:
        ser.close()
    quit()

# Initialize the serial connection
ser = initialize_serial_connection()


timestamp = datetime.now().strftime("%Y/%m/%d %H:%M:%S")
print(f"[{timestamp}][Start] Welcome to Flow Deck CYD!")

win32gui.EnumWindows(forground, 'FlowDeckCYD.exe')

# Create an icon and menu for the system tray
image = Image.open(r'resources\icon.ico')
menu = Menu(
    MenuItem('View console', forground_console, default=True),
    MenuItem('Quit', quit_app)
)
icon = Icon(name='flow-deck-cyd', icon=image, title='flow-deck-cyd', menu=menu)

# Function to run the icon in a separate thread
def run_icon():
    icon.run()

# Start the icon in a separate thread
icon_thread = threading.Thread(target=run_icon)
icon_thread.daemon = True  # This will allow the program to exit when the main thread exits
icon_thread.start()

# Main loop to monitor log file for updates
while True:
    if enable_resource_monitor:
        stats = format_system_stats()
        if enable_resource_monitor_display:
           print(stats)
        send_serial_data(stats)
    
    if check_for_updates():
        new_logs = read_new_logs()
        entries = extract_player_events(new_logs)
        for entry in entries:
            print(entry)
            send_serial_data(entry)
    time.sleep(1)  # Wait for 1 second before checking again
