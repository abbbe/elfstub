import psutil

def get_process_cpu_usage(pid, duration=1):
    """Get the CPU usage of a process over a specified duration."""
    p = psutil.Process(pid)
    return p.cpu_percent(duration)
