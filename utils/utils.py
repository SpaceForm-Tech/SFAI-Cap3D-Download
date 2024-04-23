"""TODO: Module docstring"""

import os

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
