import logging
import os
from datetime import datetime

from azure.storage.blob import BlobServiceClient, ContentSettings


class AzureBlobStorageHandler(logging.Handler):
    def __init__(self, connection_string: str, container_name: str, blob_name: str):
        super().__init__()
        self.connection_string = connection_string
        # self.blob_service_client = BlobServiceClient.from_connection_string(
        #     self.connection_string
        # )
        self.container_name = container_name
        self.blob_name = blob_name

    def emit(self, record):
        try:
            with BlobServiceClient.from_connection_string(
                CONNECTION_STRING
            ) as blob_service_client:
                # print("Successfully created blob service client.\n")

                # Attempt to list containers to verify the connection
                containers = blob_service_client.list_containers()
                print(
                    f"Azure Blob Storage containers: {[c.name for c in containers]}.\n"
                )

            # if not hasattr(self, "blob_service_client") or not self.blob_service_client:
            #     print("No blob service client")
            # Lazily initialize blob service client if not already initialized
            self.blob_service_client = BlobServiceClient.from_connection_string(
                self.connection_string
            )
            containers = self.blob_service_client.list_containers()
            print(f"Azure Blob Storage containers: {[c.name for c in containers]}.\n")

            blob_client = self.blob_service_client.get_blob_client(
                container=self.container_name, blob=self.blob_name
            )
            log_message = self.format(record).encode(
                "utf-8"
            )  # Encode log message to bytes
            print(f"log_message: {log_message}")
            blob_client.upload_blob(
                log_message,
                overwrite=True,
                content_settings=ContentSettings(content_type="text/plain"),
            )
        except Exception as e:
            # Handle exceptions here, e.g., log the exception
            logging.error(f"Failed to upload log message to Azure Blob Storage: {e}")


# Usage:
CONTAINER_NAME = "logs"
CONNECTION_STRING = os.environ.get("STORAGEACCOUNT_CONNECTION_STRING")
BLOB_NAME = f"TestLogs/loghandlerlog-{datetime.now().isoformat()}.log"

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.StreamHandler(),
    ],
)
logger = logging.getLogger()
assert logger.hasHandlers(), "Logger has no handlers attached"

azure_handler = AzureBlobStorageHandler(
    connection_string=CONNECTION_STRING,
    container_name=CONTAINER_NAME,
    blob_name=BLOB_NAME,
)
logger.addHandler(azure_handler)
assert len(logger.handlers) > 1, "Azure handler not added"

logger.info(f"info log ({datetime.now().strftime('%Y-%m-%dT%H:%M:%S')})")
# logger.warning(f"warning log ({datetime.now().strftime('%Y-%m-%dT%H:%M:%S')})")
# logger.error(f"error log ({datetime.now().strftime('%Y-%m-%dT%H:%M:%S')})")
