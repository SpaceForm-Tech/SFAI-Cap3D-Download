"""
Module for unzipping files.

This module provides functionality to unzip files. It includes a function `unzip_file` that takes a zip file path
and an extraction destination path as input, and extracts the contents of the zip file to the specified destination.

Example:
    To unzip a file named 'example.zip' to the directory 'output':
    
    $ python unzip.py example.zip output

"""

import argparse
import logging
import os
import zipfile
from typing import Optional

from create_directory import create_directory
from tqdm import tqdm


def extract_zip_file_recursive(
    zip_file: str,
    extract_to: str,
    track_extraction: Optional[bool] = False,
    max_recursion_depth: Optional[int] = 1,
    current_recursion_depth: Optional[int] = -1,
    logger: Optional[logging.Logger] = None,
    debug_logging: Optional[bool] = False,
) -> None:
    """
    Extracts a zip file to the specified destination directory and recursively extracts nested zip files.

    Args:
        zip_file (str): Path to the zip file to be extracted.
        extract_to (str): Path to the directory where zip file contents will be extracted to.
        track_extraction (Optional[bool]): Flag to toggle zipfile extraction tracking in the console. Default is False.
        max_recursion_depth (Optional[int]): Maximum number of recursions before raising an error. Default is 1.
        current_recursion_depth (Optional[int]): Current recursion depth. Default is 0.
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

        logger = logging.getLogger()  # Get the root logger

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

    create_directory(
        destination=extract_to,
        is_directory=True,
        logger=logger,
        debug_logging=debug_logging,
    )
    absolute_extract_to_path = os.path.abspath(extract_to)
    try:
        with zipfile.ZipFile(absolute_zip_file_path, "r") as zip_ref:
            name_list = zip_ref.namelist()
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

                        extract(
                            zip_ref=zip_ref,
                            file_info=file_info,
                            extract_to=extract_to,
                            current_recursion_depth=current_recursion_depth,
                            max_recursion_depth=max_recursion_depth,
                            debug_logging=(
                                True
                                if current_recursion_depth >= 1 or track_extraction
                                else debug_logging
                            ),
                        )

            else:
                for file_info in zip_ref.infolist():
                    extract(
                        zip_ref=zip_ref,
                        file_info=file_info,
                        extract_to=extract_to,
                        current_recursion_depth=current_recursion_depth,
                        max_recursion_depth=max_recursion_depth,
                        debug_logging=(
                            True if current_recursion_depth >= 1 else debug_logging
                        ),
                    )

    except zipfile.BadZipFile:
        logger.exception("Invalid zip file: '%s'", absolute_zip_file_path)
        raise

    logger.log(
        logging.DEBUG if debug_logging else logging.INFO,
        "Unzipping file process successfully completed with zip file: '%s' extracted to: '%s'",
        absolute_zip_file_path,
        absolute_extract_to_path,
    )


def extract(
    zip_ref: zipfile.ZipFile,
    file_info: zipfile.ZipInfo,
    extract_to: str,
    current_recursion_depth: int,
    max_recursion_depth: int,
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
        debug_logging (bool): Flag to toggle debug logging.
    """
    zip_ref.extract(file_info, extract_to)

    # Extract nested zip files recursively
    for item in zip_ref.namelist():
        item_path = os.path.join(extract_to, item)
        if item.endswith(".zip") and zipfile.is_zipfile(item_path):
            assert (
                current_recursion_depth <= max_recursion_depth
            ), f"Maximum recursion limit reached ({max_recursion_depth})."
            nested_extract_to = os.path.join(extract_to, os.path.splitext(item)[0])
            os.makedirs(nested_extract_to, exist_ok=True)
            extract_zip_file_recursive(
                zip_file=item_path,
                extract_to=nested_extract_to,
                track_extraction=False,
                max_recursion_depth=max_recursion_depth,
                debug_logging=debug_logging,
            )


# def parallel_extract_zip_file(
#     zip_file: str,
#     extract_to: str,
#     track_extraction: bool,
#     max_recursion_depth: int,
#     debug_logging: bool,
# ):
#     """
#     Function to be used with multiprocessing.Pool for parallel extraction.
#     """
#     try:
#         extract_zip_file_recursive(
#             zip_file, extract_to, track_extraction, max_recursion_depth, debug_logging
#         )

#     except Exception as e:
#         logging.error("Error extracting '%s': %s", zip_file, str(e))


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
    debug_logging = args.debug_logging
    # processes = args.processes

    if not os.path.exists(zip_file):
        print(f"Error: Zip file '{zip_file}' not found.")
        return

    extract_zip_file_recursive(
        zip_file=zip_file,
        extract_to=extract_to,
        track_extraction=track_extraction,
        max_recursion_depth=max_recursion_depth,
        debug_logging=debug_logging,
    )


if __name__ == "__main__":
    main()
