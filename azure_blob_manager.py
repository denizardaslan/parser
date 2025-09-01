from azure.storage.blob import BlobServiceClient
import pandas as pd

# CONFIGURATION - UPDATE THESE
CONNECTION_STRING = "your_connection_string_here"
CONTAINER_NAME = "your_container_name"  # Set this if you know it, or leave empty to list all containers
FOLDER_PATH = "2024/PCMCIA"  # Change this to your folder


def list_containers(connection_string):
    """List all containers in the storage account"""
    blob_service = BlobServiceClient.from_connection_string(connection_string)
    containers = blob_service.list_containers()

    container_names = []
    for container in containers:
        container_names.append(container.name)

    return container_names


def get_files_in_folder(connection_string, container_name, folder_path):
    """Get all file names from a specific folder in Azure Blob Storage"""

    # Connect to Azure
    blob_service = BlobServiceClient.from_connection_string(connection_string)
    container_client = blob_service.get_container_client(container_name)

    # Make sure folder path ends with /
    if not folder_path.endswith("/"):
        folder_path += "/"

    # Get all files in the folder
    blobs = container_client.list_blobs(name_starts_with=folder_path)

    files = []
    for blob in blobs:
        if not blob.name.endswith("/"):  # Skip folders
            filename = blob.name.split("/")[-1]  # Get just the filename
            files.append(filename)

    return files


if __name__ == "__main__":
    try:
        # If no container name specified, list all containers first
        if CONTAINER_NAME == "your_container_name":
            print("Available containers:")
            containers = list_containers(CONNECTION_STRING)
            for i, container in enumerate(containers, 1):
                print(f"{i}. {container}")

            if containers:
                print(
                    f"\nUpdate CONTAINER_NAME in the script to one of the above containers"
                )
            exit()

        files = get_files_in_folder(CONNECTION_STRING, CONTAINER_NAME, FOLDER_PATH)

        # Create DataFrame and save to Excel
        data = []
        for i, filename in enumerate(files, 1):
            data.append(
                {
                    "No": i,
                    "Folder": FOLDER_PATH,
                    "Container": CONTAINER_NAME,
                    "Filename": filename,
                }
            )

        df = pd.DataFrame(data)
        excel_filename = (
            f"azure_files_{CONTAINER_NAME}_{FOLDER_PATH.replace('/', '_')}.xlsx"
        )
        df.to_excel(excel_filename, index=False)

        print(f"Excel file created: {excel_filename}")
        print(f"Total: {len(files)} files saved to Excel")

    except Exception as e:
        print(f"Error: {e}")
        print("Make sure to update CONNECTION_STRING first!")
