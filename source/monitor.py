import psutil
import GPUtil
from datetime import datetime

def get_system_stats():
    # Get CPU usage
    cpu_usage = psutil.cpu_percent(interval=None)

    # Get RAM usage
    ram = psutil.virtual_memory()
    ram_usage = ram.used / (1024 ** 3)
    ram_total = ram.total / (1024 ** 3)

    # Get GPU usage
    gpus = GPUtil.getGPUs()
    if gpus:
        gpu = gpus[0]
        gpu_usage = gpu.load * 100
        vram_usage = gpu.memoryUsed / 1024
        vram_total = gpu.memoryTotal / 1024
    else:
        gpu_usage = 0
        vram_usage = 0
        vram_total = 0

    return cpu_usage, gpu_usage, ram_usage, ram_total, vram_usage, vram_total

def format_system_stats():
    # Get system statistics
    cpu_usage, gpu_usage, ram_usage, ram_total, vram_usage, vram_total = get_system_stats()
    
    # Get current time
    current_time = datetime.now().strftime("%Y/%m/%d %H:%M:%S")
    
    # retun statistics with specified format
    return f"[{current_time}][Monitor] CPU:{cpu_usage:.1f}%, GPU:{gpu_usage:.1f}%, RAM:{ram_usage:.1f}GB/{ram_total:.1f}GB, VRAM:{vram_usage:.1f}GB/{vram_total:.1f}GB"
