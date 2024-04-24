# SFAI-Cap3D-Download

## Overview
[Cap3D](https://cap3d-um.github.io/) provides detailed descriptions of 3D objects by leveraging pretrained models in captioning, alignment, and LLM to consolidate multi-view information.

This repo contains scripts for the downloading and unzipping of the rendered images from the [Cap3D dataset](https://cap3d-um.github.io/). Examples of rendered images are shown below:

![Example captioning results by Cap3D.](https://tiangeluo.github.io/projectpages/imgs/Cap3D/teaser.png)

The dataset is hosted on [Hugging Face](https://huggingface.co/datasets/tiange/Cap3D). Due to its size the rendered images dataset is sharded into ~53 zip files of ~42GB each. Files must be manually downloaded and require ~2.4TB of disk space to store. Files must also be unzipped before use, so will utilise more disk space when uncompressed.

## Functionality
### [download.py](download.py) 
The main module provided by this repo is [download.py](download.py). This module provides functionality for downloading files with a retry mechanism and optionally extracting ZIP files.
Run this module from the command line with appropriate arguments to download files with retry mechanism.
Example:
```bash
python download.py http://example.com/file.zip ./output/file.zip --stream_log --file_log --unzip --track_extraction --chunk_size 8192 --max_retries 5 --retry_delay 30 --timeout 60
```
### [utils](utils)
#### [checksum.py](utils/checksum.py)
Utility module for performing checksum operations and verifying (downloaded) files using SHA-256.

This module can be run to monitor resource usage with the following command:
```bash
python utils/checksum.py download/compressed_imgs_perobj_00.zip https://huggingface.co/datasets/tiange/Cap3D/raw/main/RenderedImage_perobj_zips/compressed_imgs_perobj_00.zip
```

#### [create_directory.py](utils/create_directory.py)
This script creates a directory for the input file if it doesn't already exist.

This module can be run to monitor resource usage with the following command:
```bash
python utils/create_directory.py unzip True --debug_logging
```

#### [logger_config.py](utils/logger_config.py)
This module provides a function `setup_logger` to set up a logger with the specified log_output_file_path.

#### [unzip_file.py](utils/unzip_file.py)
Module for unzipping files and handling nested zip files.

This module can be run to monitor resource usage with the following command:
```bash
python -m utils.unzip_file download/compressed_imgs_perobj_00.zip unzips/compressed_imgs_perobj_00
```

#### [utils.py](utils/utils.py)
This module provides general utility functions including loading configuration data from a YAML file and monitoring system resources such as CPU and memory usage.

This module can be run to monitor resource usage with the following command:
```bash
python utils/utils.py
```

## Setup
Create the conda environment:
```bash
conda env create -f environment.yaml
```

Activate the environment:
```bash
conda activate cap3d_download
```