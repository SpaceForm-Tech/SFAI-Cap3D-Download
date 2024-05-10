import os
from datetime import datetime

from azure.storage.blob import BlobServiceClient, ContentSettings

CONTAINER_NAME = "logs"
CONNECTION_STRING = os.environ.get("STORAGEACCOUNT_CONNECTION_STRING")
assert (
    CONNECTION_STRING
), "Environment variable STORAGEACCOUNT_CONNECTION_STRING is not set."

# Attempt to create a BlobServiceClient instance
try:
    # Create a BlobServiceClient
    print("Creating blob service client process started.")
    with BlobServiceClient.from_connection_string(
        CONNECTION_STRING
    ) as blob_service_client:
        print("Successfully created blob service client.\n")

        # Attempt to list containers to verify the connection
        containers = blob_service_client.list_containers()
        print(f"Azure Blob Storage containers: {[c.name for c in containers]}.\n")

        # Upload a blob to a folder
        print("Getting blob client process started.")
        blob_client = blob_service_client.get_blob_client(
            container=CONTAINER_NAME,
            blob=f"TestLogs/log-{datetime.now().isoformat()}.log",
        )
        print("Successfully got blob client.\n")

        print("Reading data to upload to blob client process started.")
        with open("example.log", "rb") as data:
            print("Successfully read data to upload to blob client.\n")

            print("Uploading data to blob client process started.")
            blob_client.upload_blob(data)
            print("Successfully uploaded data to blob client.\n")

        blob_client2 = blob_service_client.get_blob_client(
            container=CONTAINER_NAME,
            blob=f"TestLogs/log2-{datetime.now().isoformat()}.log",
        )
        log_message = f"info log ({datetime.now().isoformat()})".encode("utf-8")
        blob_client2.upload_blob(
            log_message,
            overwrite=True,
            content_settings=ContentSettings(content_type="text/plain"),
        )

except Exception as e:
    print("Error interacting with Azure Blob Storage:", e)
