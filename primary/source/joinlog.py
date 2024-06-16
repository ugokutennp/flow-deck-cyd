import os
import re
from collections import defaultdict
from datetime import datetime

# Set the home directory and log directory paths
home_dir = os.path.expanduser("~")
log_dir_path = os.path.join(home_dir, r"AppData\LocalLow\VRChat\VRChat")
log_file_path = None
last_position = 0
startup_time = datetime.now()  # Record the startup time
enable_logging = True  # Flag to enable/disable logging

# Function to print log messages based on the enable_logging flag
def log(message):
    if enable_logging:
        timestamp = datetime.now().strftime("%Y/%m/%d %H:%M:%S")
        print(f"[{timestamp}][Debug] {message}")

# Function to get the latest log file path
def get_latest_log_file_path():
    log_files = [f for f in os.listdir(log_dir_path) if f.startswith("output_log") and f.endswith(".txt")]
    log_files.sort(key=lambda f: os.path.getmtime(os.path.join(log_dir_path, f)), reverse=True)
    return os.path.join(log_dir_path, log_files[0]) if log_files else None

# Function to get the last modified time of a file
def get_file_last_modified_time(path):
    return os.path.getmtime(path)

# Function to check if the log file has been updated or changed
def check_for_updates():
    global log_file_path, last_position
    latest_log_file_path = get_latest_log_file_path()
    if latest_log_file_path != log_file_path:
        log_file_path = latest_log_file_path
        last_position = 0  # Reset the position when log file changes
        log(f"New log file detected: {log_file_path}")
        return True

    current_modified_time = get_file_last_modified_time(log_file_path)
    if not hasattr(check_for_updates, "last_modified_time"):
        check_for_updates.last_modified_time = current_modified_time

    if current_modified_time != check_for_updates.last_modified_time:
        check_for_updates.last_modified_time = current_modified_time
        log(f"Log file has been updated: {log_file_path}")
        return True
    return False

# Function to extract player join and leave events from log lines
def extract_player_events(log_lines):
    events = defaultdict(lambda: {"join": [], "left": []})
    for line in log_lines:
        joined_match = re.match(r"(\d{4}\.\d{2}\.\d{2} \d{2}:\d{2}:\d{2}).* \[Behaviour\] OnPlayerJoined (.+)", line)
        left_match = re.match(r"(\d{4}\.\d{2}\.\d{2} \d{2}:\d{2}:\d{2}).* \[Behaviour\] OnPlayerLeft (.+)", line)
        
        if joined_match:
            timestamp = joined_match.group(1)
            log_time = datetime.strptime(timestamp, "%Y.%m.%d %H:%M:%S")
            if log_time >= startup_time:
                player_name = joined_match.group(2).strip()
                events[timestamp]["join"].append(player_name)

        if left_match:
            timestamp = left_match.group(1)
            log_time = datetime.strptime(timestamp, "%Y.%m.%d %H:%M:%S")
            if log_time >= startup_time:
                player_name = left_match.group(2).strip()
                events[timestamp]["left"].append(player_name)

    entries = []
    for timestamp, event in events.items():
        time_part = timestamp.split()
        date_part = time_part[0].replace(".", "/")
        time_part = time_part[1]
        formatted_time = f"[{date_part} {time_part}]"

        if event["join"]:
            join_players = ",".join(event["join"])
            entries.append(f"{formatted_time}[Join] {join_players}")

        if event["left"]:
            left_players = ",".join(event["left"])
            entries.append(f"{formatted_time}[Left] {left_players}")

    return entries

# Function to read new lines from the log file
def read_new_logs():
    global last_position
    with open(log_file_path, 'r', encoding='utf-8') as file:
        file.seek(last_position)
        new_lines = file.readlines()
        last_position = file.tell()
    return new_lines

# Get the latest log file path on startup
log_file_path = get_latest_log_file_path()
log("Monitoring start")
log(f"Program started at {startup_time}")
log(f"Initial log file: {log_file_path}")
