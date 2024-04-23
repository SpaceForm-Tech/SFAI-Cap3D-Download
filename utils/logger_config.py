"""
Module for configuring a logger with specified log_output_file_path.

This module provides a function `setup_logger` to set up a logger with the specified log_output_file_path.
The logger is configured to log messages to both a file with a name based on the current date 
and a stream (console).

Example:
    To configure a logger to log to a file named 'mylog-2024-04-01.log' in the current directory 
    and also to the console:
    
    >>> import logger_config
    >>> logger = logger_config.setup_logger('path/to/logging.yaml', 'path/to/log_output.zip')
    >>> logger.info('This is a test log message')

"""

import logging
import logging.config

from utils.utils import load_yaml_config

DOWNLOAD_LOGGER = "download"


def setup_logger(
    yaml_config_path: str,
    log_output_file_path: str,
) -> logging.Logger:
    """
    Set up a logger with specified path to output log file or load from a YAML configuration.

    Args:
        yaml_config_path (str): The path to the yaml config file.
        log_output_file_path (str): The relative path to the output log file.

    Returns:
        logging.Logger: The configured logger object.

    Raises:
        ValueError: If neither stream logging nor file logging is enabled.
    """
    try:
        # Load logging configuration from the specified YAML file
        config = load_yaml_config(yaml_config_path)

        stream_handler_config = config["handlers"]["console"]

        # Update the configuration with additional initialization parameters
        if "file" in config["handlers"]:
            file_handler_config = config["handlers"]["file"]

            if "init_kwargs" in file_handler_config:
                # Adjust the args to unpack the dictionary instead
                init_kwargs = file_handler_config.pop("init_kwargs")
                log_directory = init_kwargs["log_directory"]
                assert (
                    log_directory
                ), f"No log_directory found in yaml config ({yaml_config_path})"
                log_directory += "/" + log_output_file_path
                config["handlers"]["file"]["log_directory"] = log_directory

        # Logger must contain either stream or file handler
        assert (
            stream_handler_config or file_handler_config
        ), "Logger setup must setup at least one of stream logging and file logging"

        logging.config.dictConfig(config)

        return logging.getLogger(DOWNLOAD_LOGGER)

    except Exception as e:
        print(f"Error setting up logger. (Error: {e}.)")
        raise e
