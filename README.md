# Azure Blob Storage Script

Simple script to get file names from Azure Blob Storage folders like `2024/PCMCIA`, `2025/PCMCIA`, etc.

## Setup

1. Install the Azure package:
```bash
pip install azure-storage-blob
```

2. Edit the script and update these variables:
- `CONNECTION_STRING` - your Azure Storage connection string
- `CONTAINER_NAME` - your container name  
- `FOLDER_PATH` - the folder you want to list (e.g., "2024/PCMCIA")

3. Run it:
```bash
python azure_blob_manager.py
```

That's it!