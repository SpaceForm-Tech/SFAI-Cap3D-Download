import logging
import os
from datetime import datetime

from azure.monitor.opentelemetry import configure_azure_monitor

assert os.environ.get("APPLICATIONINSIGHTS_CONNECTION_STRING")

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.StreamHandler(),
    ],
)

# Configure OpenTelemetry to use Azure Monitor with the
# APPLICATIONINSIGHTS_CONNECTION_STRING environment variable.
configure_azure_monitor(
    # Set logger_name to the name of the logger you want to capture logging telemetry with
    logger_name="my_application_logger",
)

# Logging calls with this logger will be tracked
logger = logging.getLogger("my_application_logger")
# logger = logging.getLogger()
assert logger.hasHandlers(), "Logger has no handlers attached"

logger.info(f"info log ({datetime.now().strftime('%Y-%m-%dT%H:%M:%S')})")
logger.warning(f"warning log ({datetime.now().strftime('%Y-%m-%dT%H:%M:%S')})")
logger.error(f"error log ({datetime.now().strftime('%Y-%m-%dT%H:%M:%S')})")
