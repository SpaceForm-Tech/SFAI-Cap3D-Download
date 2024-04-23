"""
Module for unzipping files.

This module provides functionality to unzip files. It includes a function `unzip_file` that takes a zip file path
and an extraction destination path as input, and extracts the contents of the zip file to the specified destination.

Example:
    To unzip a file named 'example.zip' to the directory 'output':
    
    $ python unzip.py example.zip output

TODO:
    - Implement already extracted logic (see commented code)
"""

import argparse
import concurrent.futures
import logging
import os
import zipfile
from typing import Optional

from tqdm import tqdm

from utils.create_directory import create_directory

from .logger_config import setup_logger


def extract_zip_file_recursive(
    zip_file: str,
    extract_to: str,
    current_recursion_depth: int,
    track_extraction: Optional[bool] = False,
    max_recursion_depth: Optional[int] = 1,
    logger: Optional[logging.Logger] = None,
    debug_logging: Optional[bool] = False,
) -> None:
    """
    Extracts a zip file to the specified destination directory and recursively extracts nested zip files.

    Args:
        zip_file (str): Path to the zip file to be extracted.
        extract_to (str): Path to the directory where zip file contents will be extracted to.
        current_recursion_depth (int): Current recursion depth. A value of -1 should be passed as default.
        track_extraction (Optional[bool]): Flag to toggle zipfile extraction tracking in the console. Default is False.
        max_recursion_depth (Optional[int]): Maximum number of recursions before raising an error. Default is 1.
        logger (Optional[logging.Logger]): Logger instance for logging. If not provided, a new one will be created.
        debug_logging (Optional[bool]): Flag to toggle debug logging. Default is False.

    Raises:
        FileNotFoundError: If the zip file is not found.
        AssertionError: If maximum recursion depth is reached.
    """
    # Increment current recursion depth
    current_recursion_depth += 1

    if not logger or not logger.hasHandlers():
        logging.basicConfig(
            level=logging.INFO,
            format="%(asctime)s - %(levelname)s - %(message)s",
            handlers=[
                logging.StreamHandler(),
            ],
        )

        logger = logging.getLogger(__name__)  # Get the module logger

    absolute_zip_file_path = os.path.abspath(zip_file)
    logger.log(
        logging.DEBUG if debug_logging else logging.INFO,
        "Unzipping file process started with zip file: '%s' (current recursion depth: %s of %s)",
        absolute_zip_file_path,
        current_recursion_depth,
        max_recursion_depth,
    )
    if not os.path.exists(absolute_zip_file_path):
        raise FileNotFoundError(f"Zip file not found: '{absolute_zip_file_path}'")

    directory_created = create_directory(
        destination=extract_to,
        is_directory=True,
        logger=logger,
        debug_logging=debug_logging,
    )
    # already_extracted = False if current_recursion_depth < 1 else not directory_created

    absolute_extract_to_path = os.path.abspath(extract_to)
    try:
        with zipfile.ZipFile(absolute_zip_file_path, "r") as zip_ref:
            name_list = zip_ref.namelist()  # Names of files in zip archive
            total_files = len(name_list)
            logger.log(
                logging.DEBUG if debug_logging else logging.INFO,
                "zipfile extraction of '%s' files has started",
                total_files,
            )

            extracted_files = 0

            if track_extraction:
                # Use tqdm to display progress bar
                with tqdm(total=total_files) as pbar:
                    for file_info in zip_ref.infolist():
                        extracted_files += 1

                        pbar.update(1)

                        # if not already_extracted:
                        extract(
                            zip_ref=zip_ref,
                            file_info=file_info,
                            extract_to=extract_to,
                            current_recursion_depth=current_recursion_depth,
                            max_recursion_depth=max_recursion_depth,
                            logger=logger,
                            debug_logging=(
                                True
                                if current_recursion_depth >= 1 or track_extraction
                                else debug_logging
                            ),
                        )

            else:
                for file_info in zip_ref.infolist():
                    # if not already_extracted:
                    extract(
                        zip_ref=zip_ref,
                        file_info=file_info,
                        extract_to=extract_to,
                        current_recursion_depth=current_recursion_depth,
                        max_recursion_depth=max_recursion_depth,
                        logger=logger,
                        debug_logging=(
                            True if current_recursion_depth >= 1 else debug_logging
                        ),
                    )

    except zipfile.BadZipFile:
        logger.exception("Invalid zip file: '%s'", absolute_zip_file_path)
        raise

    # Delete the zip file after successful extraction
    if current_recursion_depth >= 1:
        os.remove(zip_file)

    logger.log(
        logging.DEBUG if debug_logging else logging.INFO,
        "Zip file extraction and deletion process has successfully completed (zip file: '%s' extracted to: '%s')",
        absolute_zip_file_path,
        absolute_extract_to_path,
    )


def extract(
    zip_ref: zipfile.ZipFile,
    file_info: zipfile.ZipInfo,
    extract_to: str,
    current_recursion_depth: int,
    max_recursion_depth: int,
    logger: logging.Logger,
    debug_logging: bool,
) -> None:
    """
    Extracts a file from a zip archive.

    Args:
        zip_ref (zipfile.ZipFile): ZipFile object representing the zip archive.
        file_info (zipfile.ZipInfo): Information about the file to be extracted.
        extract_to (str): Path to the directory where the file will be extracted to.
        current_recursion_depth (int): Current recursion depth.
        max_recursion_depth (int): Maximum recursion depth.
        logger (logging.Logger): Logger instance for logging.
        debug_logging (bool): Flag to toggle debug logging.
    """
    zip_ref.extract(file_info, extract_to)

    # Extract nested zip files concurrently and recursively
    with concurrent.futures.ThreadPoolExecutor() as executor:
        futures = []
        for item in zip_ref.namelist():
            item_path = os.path.join(extract_to, item)
            if item.endswith(".zip") and zipfile.is_zipfile(item_path):
                assert (
                    current_recursion_depth <= max_recursion_depth
                ), f"Maximum recursion limit reached ({max_recursion_depth})."

                nested_extract_to = os.path.join(extract_to, os.path.splitext(item)[0])
                os.makedirs(nested_extract_to, exist_ok=True)

                futures.append(
                    executor.submit(
                        extract_zip_file_recursive,
                        item_path,
                        nested_extract_to,
                        current_recursion_depth + 1,
                        False,
                        max_recursion_depth,
                        logger,
                        debug_logging,
                    )
                )

        # Wait for all tasks to complete
        for future in concurrent.futures.as_completed(futures):
            try:
                future.result()
            except Exception as e:
                logger.error("Error occurred: %s", e)


def main() -> None:
    """
    Example usage:
    ```bash
    python utils/unzip_file.py RenderedImage_perobj_zips/compressed_imgs_perobj_00.zip RenderedImage_perobj_zips/compressed_imgs_perobj_00
    ```
    """
    parser = argparse.ArgumentParser(
        description="Creates directory for input file if it doesn't exist."
    )
    parser.add_argument("zip_file", type=str, help="Path to zip file to be extracted.")
    parser.add_argument(
        "extract_to",
        type=str,
        help="Path to the directory where zip file contents will be extracted to.",
    )
    parser.add_argument(
        "--track_extraction",
        type=bool,
        default=True,
        help="Flag to toggle zipfile extraction tracking in the console.",
    )
    parser.add_argument(
        "--max_recursion_depth",
        type=int,
        default=1,
        help="Maximum number of recursions before raising an error.",
    )
    parser.add_argument(
        "--yaml_config_path",
        type=str,
        default=None,
        help="Path to yaml_config_path for logger.",
    )
    parser.add_argument(
        "--debug_logging",
        type=bool,
        default=False,
        help="Flag to toggle debug logging.",
    )

    args = parser.parse_args()

    zip_file = args.zip_file
    extract_to = args.extract_to
    track_extraction = args.track_extraction
    max_recursion_depth = args.max_recursion_depth
    yaml_config_path = args.yaml_config_path
    debug_logging = args.debug_logging

    # Set up logging
    logger: logging.Logger = setup_logger(
        yaml_config_path=yaml_config_path,
        log_output_file_path=zip_file,
    )

    extract_zip_file_recursive(
        zip_file=zip_file,
        extract_to=extract_to,
        current_recursion_depth=-1,
        track_extraction=track_extraction,
        max_recursion_depth=max_recursion_depth,
        logger=logger,
        debug_logging=debug_logging,
    )


if __name__ == "__main__":
    main()
