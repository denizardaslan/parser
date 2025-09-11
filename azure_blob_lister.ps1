Import-Module Posh-SSH

# --- Configuration ---
$container = "/historical/2023/WQAR"
$hostname  = "your.sftp.server"
$port      = 22
$username  = "your_username"
$password  = "your_password"
$outputPath = "C:\Temp\sftp_files.csv"   # <-- change to where you want

# --- Connect to SFTP ---
$secpasswd = ConvertTo-SecureString $password -AsPlainText -Force
$cred      = New-Object System.Management.Automation.PSCredential ($username, $secpasswd)
$session   = New-SFTPSession -ComputerName $hostname -Port $port -Credential $cred -AcceptKey

# --- Get file list ---
Write-Host "Fetching file list from: $container ..."
$files = Get-SFTPChildItem -SessionId $session.SessionId -Path $container

Write-Host "Found $($files.Count) files."

# --- Export directly to CSV (streaming) ---
Write-Host "Exporting file details to: $outputPath ..."

$files | ForEach-Object {
    [PSCustomObject]@{
        FileName     = $_.Name
        FilePath     = "$container/$($_.Name)"
        FileSize     = $_.Size
        LastModified = $_.LastWriteTime
    }
} | Export-Csv -Path $outputPath -NoTypeInformation

Write-Host "✅ Export complete. File saved at: $outputPath"

# --- Clean up ---
Remove-SFTPSession -SessionId $session.SessionId


-----

altında kaç sayı var onu hesaplama
-------

Import-Module Posh-SSH

# --- Configuration ---
$container = "/historical/2023/WQAR"
$hostname  = "your.sftp.server"
$port      = 22
$username  = "your_username"
$password  = "your_password"

# --- Connect to SFTP ---
$secpasswd = ConvertTo-SecureString $password -AsPlainText -Force
$cred      = New-Object System.Management.Automation.PSCredential ($username, $secpasswd)
$session   = New-SFTPSession -ComputerName $hostname -Port $port -Credential $cred -AcceptKey

# --- Recursive file counting ---
function Get-TotalFiles {
    param (
        [string]$Path,
        [int]$SessionId
    )

    $total = 0
    $items = Get-SFTPChildItem -SessionId $SessionId -Path $Path

    foreach ($item in $items) {
        if ($item.Attributes.IsDirectory) {
            # Alt klasörü tara
            $total += Get-TotalFiles -Path "$Path/$($item.Name)" -SessionId $SessionId
        } else {
            # Dosya ise say
            $total += 1
        }
    }
    return $total
}

# --- Hesaplama ---
$totalFiles = Get-TotalFiles -Path $container -SessionId $session.SessionId
Write-Host "Total files (including subfolders): $totalFiles"

# --- Clean up ---
Remove-SFTPSession -SessionId $session.SessionId
