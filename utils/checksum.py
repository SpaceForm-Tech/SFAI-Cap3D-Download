"""Utility functions for performing checksum operations."""

import hashlib
import logging
from typing import List, Optional

import requests


def sha256_hash(data: bytes):
    """
    Compute the SHA-256 hash of the given data.

    Args:
        data (bytes): The input data to be hashed.

    Returns:
        str: The hexadecimal representation of the SHA-256 hash.
    """
    sha256: hashlib.sha256 = hashlib.sha256()
    sha256.update(data)

    return sha256.hexdigest()


def extract_sha256_from_pointer_file(bytes_data: bytes) -> str or None:
    """
    Extract the SHA256 hash from a bytes string.

    Args:
        bytes_data (bytes): The bytes string containing the data.

    Returns:
        str or None: The extracted SHA256 hash if found, otherwise None.
    """
    # Decode bytes to string
    data_str: str = bytes_data.decode("utf-8")

    # Split the string into lines
    lines: List[str] = data_str.split("\n")

    # Find the line containing the SHA256 hash
    sha256_line: str = next(
        (line for line in lines if line.startswith("oid sha256:")), None
    )

    # Extract the SHA256 hash value
    if sha256_line:
        file_hash: str = sha256_line.split("sha256:")[1]
        return file_hash


def calculate_file_hash(file_path: str) -> str:
    """
    Calculate the SHA256 hash of a file.

    Args:
        file_path (str): The path to the file.

    Returns:
        str: The hexadecimal representation of the SHA256 hash.
    """
    # Read the file's bytes
    with open(file_path, "rb") as file:
        file_bytes: bytes = file.read()

    # Calculate the SHA256 hash of the file's bytes
    file_hash: str = sha256_hash(file_bytes)

    return file_hash


def perform_checksum(
    file_path: str, pointer_file_url: str, logger: Optional[logging.Logger] = None
) -> bool:
    """
    Perform checksum verification of a file against a pointer file.

    Args:
        file_path (str): The path to the file.
        pointer_file_url (str): The URL of the pointer file.
        logger (Optional[logging.Logger]): Logger instance for logging. If not provided, a new one will be created.

    Returns:
        bool: True if the file's checksum matches the expected checksum from the pointer file, False otherwise.
    """
    if not logger or not logger.hasHandlers():
        logging.basicConfig(
            level=logging.INFO,
            format="%(asctime)s - %(levelname)s - %(message)s",
            handlers=[
                logging.StreamHandler(),
            ],
        )

        logger = logging.getLogger()  # Get the root logger

    logger.info("Calculate file hash process started for file: '%s'", file_path)
    file_hash: str = calculate_file_hash(file_path=file_path)
    logger.info(
        "Calculate file hash process successfully completed for file: '%s' (file hash: '%s')",
        file_path,
        file_hash,
    )

    logger.info("Requesting pointer file from url: '%s'", pointer_file_url)
    response: requests.Response = requests.get(pointer_file_url, timeout=10)
    response.raise_for_status()
    logger.info("Received pointer file from url: '%s'", pointer_file_url)

    pointer_file: bytes = response.content

    logger.info("Extracting expected file hash from pointer file process started")
    expected_hash: str = extract_sha256_from_pointer_file(bytes_data=pointer_file)
    logger.info(
        "Extracting expected file hash from pointer file process successfully completed (pointer file hash: '%s')",
        expected_hash,
    )

    return file_hash == expected_hash
