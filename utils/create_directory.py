"""
This script creates a directory for the input file if it doesn't already exist.

It takes a destination path as input and checks if the directory needed for the file exists. 
If the directory doesn't exist, it creates it.

Example:
    To create a directory for a file named 'output/myfile.txt':
    
    $ python create_directory.py output/myfile.txt

"""

import argparse
import logging
import os
from typing import Optional


def create_directory(
    destination: str,
    is_directory: Optional[bool] = False,
    logger: Optional[logging.Logger] = None,
    debug_logging: Optional[bool] = False,
) -> None:
    """
    Create directory for the given file or directory path if it doesn't exist.

    Args:
        destination (str): The path for which the directory needs to be created.
        is_directory (Optional[bool]): Flag to indicate wether destination is file path or directory path.
        logger (Optional[logging.Logger]): Logger instance for logging. If not provided, a new one will be created.
        debug_logging (Optional[bool]): Flag to toggle debug logging. Default is False.
    """
    if not logger or not logger.hasHandlers():
        logging.basicConfig(
            level=logging.DEBUG if debug_logging else logging.INFO,
            format="%(asctime)s - %(levelname)s - %(message)s",
            handlers=[
                logging.StreamHandler(),
            ],
        )

        logger = logging.getLogger()  # Get the root logger

    try:
        absolute_path = os.path.abspath(destination)
        logger.log(
            logging.DEBUG if debug_logging else logging.INFO,
            "Creating directory for file process started with file: '%s'",
            absolute_path,
        )

        directory = absolute_path if is_directory else os.path.dirname(absolute_path)

        if not os.path.exists(directory):
            logger.debug("Creating directory: %s", directory)
            os.makedirs(directory)
            logger.debug("Created directory: %s", directory)

        else:
            logger.debug("Directory already exists: %s", directory)

        logger.log(
            logging.DEBUG if debug_logging else logging.INFO,
            "Creating directory for file process successfuly completed with file: '%s'",
            absolute_path,
        )

    except Exception as e:
        logger.exception(
            "Error while creating directory for file '%s': %s", absolute_path, str(e)
        )
        raise


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Creates directory for input file if it doesn't exist."
    )
    parser.add_argument(
        "destination", type=str, help="Path to file to create directory for."
    )
    parser.add_argument(
        "--debug_logging",
        type=bool,
        default=False,
        help="Flag to toggle debug logging.",
    )

    args = parser.parse_args()

    create_directory(args.destination, args.debug_logging)


if __name__ == "__main__":
    main()
