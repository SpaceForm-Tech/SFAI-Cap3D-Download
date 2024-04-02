import signal
import sys
import time

import psutil


def monitor_resources():
    """
    Monitor CPU and memory usage.

    This function retrieves and prints the current CPU and memory usage of the system.

    Returns:
        None
    """
    while True:
        # Get CPU usage
        cpu_percent = psutil.cpu_percent(interval=1)
        # Get memory usage
        mem = psutil.virtual_memory()
        mem_percent = mem.percent

        # Construct the output string
        output_string = f"CPU Usage: {cpu_percent}%   Memory Usage: {mem_percent}%"

        # Print the output string with a carriage return to overwrite the previous line
        print(output_string, end="\r")

        # Flush the output buffer to ensure the line is immediately printed
        sys.stdout.flush()

        # Pause execution for one second
        time.sleep(1)


def signal_handler(sig, frame):
    """
    Signal handler for SIGINT (Ctrl+C).
    """
    print("\nExiting gracefully...")
    sys.exit(0)


if __name__ == "__main__":
    # Register a signal handler for SIGINT (Ctrl+C)
    signal.signal(signal.SIGINT, signal_handler)
    try:
        monitor_resources()
    except KeyboardInterrupt:
        # Handle KeyboardInterrupt (Ctrl+C) gracefully
        print("\nExiting gracefully...")
        sys.exit(0)
