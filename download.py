"""
This module provides functionality for downloading files with a retry mechanism and optionally extracting ZIP files.

It includes a function `download_file_with_retry` for downloading a file from a given URL with a retry mechanism,
and a `main` function for handling command line arguments and starting the download process.

Usage:
    Run this module from the command line with appropriate arguments to download files with retry mechanism.
    Example:
        python download.py http://example.com/file.zip ./output/file.zip --stream_log --file_log --unzip --track_extraction --chunk_size 8192 --max_retries 5 --retry_delay 30 --timeout 60
"""

import argparse
import logging
import os
import sys
import time
import traceback
from typing import Dict

import requests
from tqdm import tqdm

sys.path.append(os.getcwd())


from utils.checksum import perform_checksum
from utils.logger_config import setup_logger
from utils.unzip_file import extract_zip_file_recursive


def download_file_with_retry(
    logger: logging.Logger,
    url: str,
    destination: str,
    chunk_size: int = 1024,
    max_retries: int = int(1e6),
    retry_delay: int = 60,
    timeout: int = 60,
) -> bool:
    """
    Download a file from a given URL with retry mechanism.

    Args:
        logger (logging.Logger): Logger object for logging.
        url (str): The URL of the file to download.
        destination (str): The path where the downloaded file will be saved.
        chunk_size (int, optional): Size of each chunk to download in bytes. Default is 1024.
        max_retries (int, optional): Maximum number of retry attempts upon failure. Default is 15.
        retry_delay (int, optional): Delay between retry attempts in seconds. Default is 60.
        timeout (int, optional): Maximum waiting time for server response in seconds. Default is 60.

    Returns:
        bool: True if the download is successful or already completed, False otherwise.
    """
    logger.info(
        "Download file process initiated (url: '%s', destination: '%s')",
        url,
        destination,
    )

    retry_count: int = 0
    resume_header: Dict[str, str] = {}
    downloaded_bytes: int = 0  # Track downloaded bytes across retries

    if os.path.exists(destination):
        downloaded_bytes = os.path.getsize(destination)
        resume_header["Range"] = f"bytes={downloaded_bytes}-"

    while retry_count < max_retries:
        try:
            with requests.get(
                url, stream=True, headers=resume_header, timeout=timeout
            ) as response:
                # Raise exception if status code is anything other than 200
                response.raise_for_status()

                file_size: int = int(response.headers.get("content-length", 0))

                # Write to file in "append binary" mode ("ab")
                with open(destination, "ab") as file, tqdm(
                    total=file_size,
                    initial=downloaded_bytes,  # Set initial value for progress bar
                    unit="B",
                    unit_scale=True,
                    unit_divisor=1024,
                    desc=os.path.basename(destination),
                ) as progress_bar:
                    for chunk in response.iter_content(chunk_size=chunk_size):
                        if chunk:
                            file.write(chunk)
                            chunk_length: int = len(chunk)
                            progress_bar.update(chunk_length)
                            downloaded_bytes += chunk_length
                        else:
                            logger.warning("Empty chunk")

            logger.info(
                "Download file process successfully completed (url: '%s', destination: '%s')",
                url,
                os.path.abspath(destination),
            )

            return True

        except requests.exceptions.HTTPError as http_e:
            if response.status_code == 416:
                logger.info(
                    "(416 Range Not Satisfiable) The file has already been fully downloaded. (Error: %s)",
                    http_e,
                )

                return True

            else:
                raise

        except requests.exceptions.RequestException as e:
            logger.error(
                "An error occurred during the download file process: %s (url: '%s', destination: '%s')",
                e,
                url,
                destination,
            )

            retry_count += 1
            logger.warning(
                "retry_count: %s, max_retries: %s.", retry_count, max_retries
            )

            if retry_count < max_retries:
                logger.warning("Retrying download in %s seconds...", retry_delay)
                time.sleep(retry_delay)

            # Calculate resume_header for the next retry attempt
            if os.path.exists(destination):
                downloaded_bytes = os.path.getsize(destination)
                resume_header["Range"] = f"bytes={downloaded_bytes}-"

    logger.warning("Max retries (%s) reached. Download terminated.", max_retries)

    return False


def main():
    try:
        parser = argparse.ArgumentParser(
            description="Download a file with retry mechanism."
        )
        parser.add_argument("url", type=str, help="URL of the file to download")
        parser.add_argument(
            "destination", type=str, help="Destination path to save the file"
        )
        parser.add_argument(
            "--chunk_size",
            type=int,
            default=8192,
            help="Size of each download chunk in bytes",
        )
        parser.add_argument(
            "--max_retries",
            type=int,
            default=int(1e6),
            help="Maximum number of retry attempts upon failure",
        )
        parser.add_argument(
            "--retry_delay",
            type=int,
            default=10,
            help="Delay between retry attempts in seconds",
        )
        parser.add_argument(
            "--timeout",
            type=int,
            default=60,
            help="Maximum waiting time for server response in seconds",
        )
        parser.add_argument(
            "--stream_log",
            action="store_true",
            help="Stream log outputs to console",
        )
        parser.add_argument(
            "--file_log",
            action="store_true",
            help="Log outputs to file",
        )
        parser.add_argument(
            "--unzip",
            action="store_true",
            help="Unzip file after download",
        )
        parser.add_argument(
            "--track_extraction",
            action="store_true",
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
            action="store_true",
            help="Flag to toggle debug logging.",
        )

        args: argparse.Namespace = parser.parse_args()
        print(f"args: {args}")

        url: str = args.url
        destination: str = args.destination
        chunk_size: int = args.chunk_size
        max_retries: int = args.max_retries
        retry_delay: int = args.retry_delay
        timeout: int = args.timeout
        stream_log: bool = args.stream_log
        file_log: bool = args.file_log
        unzip: bool = args.unzip
        track_extraction: bool = args.track_extraction
        max_recursion_depth: int = args.max_recursion_depth
        debug_logging: int = args.debug_logging

        pointer_file_url: str = url.replace("resolve", "raw").split("?")[0]

        # Set up logging
        logger: logging.Logger = setup_logger(
            destination=destination,
            log_to_stream=stream_log,
            log_to_file=file_log,
        )

        download_succeeded: bool = download_file_with_retry(
            logger=logger,
            url=url,
            destination=destination,
            chunk_size=chunk_size,
            max_retries=max_retries,
            retry_delay=retry_delay,
            timeout=timeout,
        )

        if download_succeeded:
            logger.info("Checksum process initiated for file: '%s'", destination)
            if perform_checksum(
                file_path=destination, pointer_file_url=pointer_file_url, logger=logger
            ):
                logger.info(
                    "Checksum process successfully completed for file: '%s'",
                    destination,
                )

            else:
                raise Exception("Checksum process failed for file: '%s'", destination)

            if unzip:
                extract_zip_file_recursive(
                    zip_file=destination,
                    extract_to=destination.replace(".zip", ""),
                    current_recursion_depth=-1,
                    track_extraction=track_extraction,
                    max_recursion_depth=max_recursion_depth,
                    logger=logger,
                    debug_logging=debug_logging,
                )

    except KeyboardInterrupt:
        logger.warning("Keyboard interrupt received. Exiting gracefully.")

    except Exception as e:
        # Log the exception traceback
        traceback_str = traceback.format_exc()
        logger.error("An unexpected error occurred: %s", e)
        logger.error("Traceback: %s", traceback_str)

        # Gracefully exit with an appropriate error message
        sys.exit("Exiting due to an unexpected error.")


if __name__ == "__main__":
    main()
