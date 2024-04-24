"""
This module provides general utility functions including loading configuration data from a YAML file
and monitoring system resources such as CPU and memory usage.

The `load_yaml_config` function reads a specified YAML file and returns its contents as a Python dictionary.
If the YAML file does not exist at the specified path, a `FileNotFoundError` is raised.

The `monitor_resources` function continuously displays the current CPU and memory usage, updating once per second.
It also includes a signal handler to handle `SIGINT` for graceful termination.

Attributes:
ENCODING (str): The character encoding used for reading the YAML file.

Functions:
- load_yaml_config(yaml_path: str) -> dict:
  Loads configuration data from a YAML file at the given path.

- monitor_resources():
  Continuously monitors and displays CPU and memory usage.

- signal_handler(sig, frame):
  Handles `SIGINT` (Ctrl+C) for graceful termination during resource monitoring.
"""

import os
import signal
import sys
import time

import psutil
import yaml

ENCODING = "utf-8"


def load_yaml_config(yaml_path: str):
    """
    Load configuration from a YAML file.

    Args:
        yaml_path (str): Path to the YAML file containing configurations.

    Returns:
        dict: The loaded configuration.
    """
    if not os.path.exists(yaml_path):
        raise FileNotFoundError(f"YAML configuration file '{yaml_path}' not found.")

    with open(yaml_path, "r", encoding=ENCODING) as f:
        config = yaml.safe_load(f)

    return config


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
