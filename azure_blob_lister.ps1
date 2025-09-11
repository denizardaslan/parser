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
