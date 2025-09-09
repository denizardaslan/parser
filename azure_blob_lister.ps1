# Azure Blob Storage File Lister - PowerShell Version
# Bu script Azure'dan dosya listesini alıp Excel'e kaydeder

# CONFIGURATION - UPDATE THESE
$ConnectionString = "your_connection_string_here"
$ContainerName = "your_container_name"
$FolderPath = "2024/PCMCIA"  # Change this to your folder

# Install required modules if not installed
if (!(Get-Module -ListAvailable -Name Az.Storage)) {
    Write-Host "Installing Az.Storage module..."
    Install-Module -Name Az.Storage -Force -AllowClobber
}

if (!(Get-Module -ListAvailable -Name ImportExcel)) {
    Write-Host "Installing ImportExcel module..."
    Install-Module -Name ImportExcel -Force -AllowClobber
}

# Import modules
Import-Module Az.Storage
Import-Module ImportExcel

try {
    # Create storage context from connection string
    $Context = New-AzStorageContext -ConnectionString $ConnectionString
    
    # If container name not set, list all containers
    if ($ContainerName -eq "your_container_name") {
        Write-Host "Available containers:"
        $Containers = Get-AzStorageContainer -Context $Context
        $Containers | ForEach-Object { Write-Host "- $($_.Name)" }
        Write-Host "`nUpdate ContainerName in the script to one of the above containers"
        exit
    }
    
    # Ensure folder path ends with /
    if (-not $FolderPath.EndsWith("/")) {
        $FolderPath += "/"
    }
    
    # Get all blobs in the folder
    Write-Host "Getting files from folder: $FolderPath"
    $Blobs = Get-AzStorageBlob -Container $ContainerName -Context $Context -Prefix $FolderPath
    
    # Filter only files (not folders)
    $Files = $Blobs | Where-Object { -not $_.Name.EndsWith("/") }
    
    # Create data array for Excel
    $Data = @()
    $Counter = 1
    
    foreach ($File in $Files) {
        $FileName = Split-Path $File.Name -Leaf
        $Data += [PSCustomObject]@{
            "No" = $Counter
            "Folder" = $FolderPath
            "Container" = $ContainerName
            "Filename" = $FileName
            "FullPath" = $File.Name
            "Size(KB)" = [math]::Round($File.Length / 1024, 2)
            "LastModified" = $File.LastModified
        }
        $Counter++
    }
    
    # Export to Excel
    $ExcelFileName = "azure_files_${ContainerName}_$($FolderPath.Replace('/', '_')).xlsx"
    $Data | Export-Excel -Path $ExcelFileName -AutoSize -BoldTopRow
    
    Write-Host "Excel file created: $ExcelFileName"
    Write-Host "Total: $($Files.Count) files saved to Excel"
    
} catch {
    Write-Host "Error: $($_.Exception.Message)"
    Write-Host "Make sure to update ConnectionString and ContainerName!"
}


1. PowerShell'i yönetici olarak aç

2. Execution policy ayarla:
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
3. Script'i düzenle:
$ConnectionString - Azure connection string'ini gir
$ContainerName - Container adını gir
$FolderPath - Klasör yolunu gir (örn: "2024/PCMCIA")
4. Çalıştır:
.\azure_blob_lister.ps1