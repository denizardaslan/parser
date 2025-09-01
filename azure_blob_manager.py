from azure.storage.blob import BlobServiceClient

# CONFIGURATION - UPDATE THESE
CONNECTION_STRING = "your_connection_string_here"
CONTAINER_NAME = "your_container_name"
FOLDER_PATH = "2024/PCMCIA"  # Change this to your folder


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
        files = get_files_in_folder(CONNECTION_STRING, CONTAINER_NAME, FOLDER_PATH)

        print(f"Files in '{FOLDER_PATH}':")
        for i, filename in enumerate(files, 1):
            print(f"{i}. {filename}")

        print(f"\nTotal: {len(files)} files")

    except Exception as e:
        print(f"Error: {e}")
        print("Make sure to update CONNECTION_STRING, CONTAINER_NAME, and FOLDER_PATH!")
