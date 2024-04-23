"""
Custom logging handler module.

This module provides a custom file handler for the Python logging framework.
It allows logging to files with a timestamped name and can automatically
create the necessary directories if they do not exist.
"""

import logging
import os
from datetime import datetime
from typing import Optional


class CustomFileHandler(logging.FileHandler):
    """
    A custom file handler that logs to a file with a timestamped name.

    This handler creates a new log file with a name based on the current date
    and time. It also ensures that the specified directory exists, creating
    it if necessary.

    Args:
        log_directory (str): The directory where log files will be created.
        mode (str, optional): The mode in which to open the file ('a' for append). Defaults to 'a'.
        encoding (str, optional): The encoding to use for the file. Defaults to None.
        delay (bool, optional): If True, delays file creation until logging is required. Defaults to False.
    """

    def __init__(
        self,
        log_directory,
        mode: str = "a",
        encoding: Optional[str] = None,
        delay: bool = False,
    ):
        self.log_directory = log_directory
        self.mode = mode
        self.encoding = encoding
        self.delay = delay

        # Generate the file_name based on the current time
        now = datetime.now()
        file_name = f"{self.log_directory}-{now:%Y-%m-%dT%H:%M:%S}.log"

        # Create the logs directory if it doesn't exist
        os.makedirs(os.path.dirname(file_name), exist_ok=True)

        # Initialize the FileHandler
        super().__init__(file_name, mode=mode, encoding=encoding, delay=delay)

    def close(self) -> None:
        """
        Closes the file handler, ensuring that any buffered output is written.

        This method overrides the `close` method of `FileHandler` to ensure
        proper cleanup.
        """
        super().close()

    def emit(self, record: logging.LogRecord) -> None:
        """
        Emits a log record, writing it to the file.

        This method overrides the `emit` method of `FileHandler` to ensure
        proper handling of log records.

        Args:
            record (logging.LogRecord): The log record to emit.
        """
        super().emit(record)
