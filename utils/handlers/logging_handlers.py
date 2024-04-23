"""TODO: Module docstring"""

import logging
import os
from datetime import datetime


class CustomFileHandler(logging.FileHandler):
    """TODO: Function docstring"""

    def __init__(self, log_directory, mode="a", encoding=None, delay=False):
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

    def close(self):
        """TODO: Function docstring"""
        super().close()

    def emit(self, record):
        """TODO: Function docstring"""
        super().emit(record)
