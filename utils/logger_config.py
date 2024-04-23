"""
Module for configuring a logger with specified destination.

This module provides a function `setup_logger` to set up a logger with the specified destination.
The logger is configured to log messages to both a file with a name based on the current date 
and a stream (console).

Example:
    To configure a logger to log to a file named 'mylog-2024-04-01.log' in the current directory 
    and also to the console:
    
    >>> import logger_config
    >>> logger = logger_config.setup_logger('mylog')
    >>> logger.info('This is a test log message')

"""

import logging
import logging.config
import os
from datetime import datetime
from typing import Optional

import yaml

from .create_directory import create_directory

DOWNLOAD_LOGGER = "download"
ENCODING = "utf-8"


def load_logging_config(yaml_path: str):
    """
    Load logging configuration from a YAML file.

    Args:
        yaml_path (str): Path to the YAML file containing logging configurations.

    Returns:
        dict: The loaded logging configuration.
    """
    if not os.path.exists(yaml_path):
        raise FileNotFoundError(f"YAML configuration file '{yaml_path}' not found.")

    with open(yaml_path, "r", encoding=ENCODING) as f:
        config = yaml.safe_load(f)

    return config


def setup_logger(
    destination: str,
    yaml_config_path: Optional[str] = None,
    log_to_stream: Optional[bool] = True,
    log_to_file: Optional[bool] = True,
    log_destination: Optional[str] = "logs",
    debug_logging: Optional[bool] = False,
) -> logging.Logger:
    """
    Set up a logger with specified path to output log file or load from a YAML configuration.

    Args:
        destination (str): The relative path to the output log file.
        yaml_config_path (Optional[str]): The path to the yaml config file.
        log_to_stream (Optional[bool]): Whether to log messages to the console (stream). Default is True.
        log_to_file (Optional[bool]): Whether to log messages to a file. Default is True.
        log_destination (Optional[str]): The directory where log files will be saved. Default is "logs".
        debug_logging (Optional[bool]): Whether to enable debug logging. Default is False.

    Returns:
        logging.Logger: The configured logger object.

    Raises:
        ValueError: If neither stream logging nor file logging is enabled.
    """
    if yaml_config_path:
        try:
            # Load logging configuration from the specified YAML file
            config = load_logging_config(yaml_config_path)

            # Update the configuration with additional initialization parameters
            if "file" in config["handlers"]:
                file_handler_conf = config["handlers"]["file"]
                if "init_kwargs" in file_handler_conf:
                    # Adjust the args to unpack the dictionary instead
                    init_kwargs = file_handler_conf.pop("init_kwargs")
                    log_directory = init_kwargs["log_directory"]
                    assert (
                        log_directory
                    ), f"No log_directory found in yaml config ({yaml_config_path})"
                    log_directory += "/" + destination
                    config["handlers"]["file"]["log_directory"] = log_directory

            logging.config.dictConfig(config)

            # Return the logger with the name matching the 'destination'
            return logging.getLogger(DOWNLOAD_LOGGER)
        except Exception as e:
            print(f"Error setting up logger. (Error: {e}.)")
            raise e

    # Fallback to default logger setup logic
    if not log_to_stream and not log_to_file:
        raise ValueError(
            "Logger setup must setup at least one of stream logging and file logging"
        )

    # create_directory(destination)

    # # Create a new logger with the 'destination' argument as the name
    # logger = logging.getLogger(destination)
    # logger.setLevel(logging.DEBUG if debug_logging else logging.INFO)

    # # Prevent propagation of log messages to parent loggers
    # logger.propagate = False

    # formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")

    # # Log to console (stream)
    # if log_to_stream and not any(
    #     isinstance(handler, logging.StreamHandler) for handler in logger.handlers
    # ):
    #     stream_handler = logging.StreamHandler()
    #     stream_handler.setFormatter(formatter)
    #     logger.addHandler(stream_handler)

    # # Log to file
    # if log_to_file:
    #     # Make logs directory
    #     create_directory(destination=log_destination, is_directory=True)
    #     create_directory(
    #         destination=f"{log_destination}/{destination}", is_directory=False
    #     )

    #     file_handler = logging.FileHandler(
    #         f"{log_destination}/{destination}-{datetime.now():%Y-%m-%dT%H:%M:%S}.log"
    #     )
    #     file_handler.setFormatter(formatter)
    #     logger.addHandler(file_handler)

    # return logger
