$exclude = @("venv", "estudos.zip")
$files = Get-ChildItem -Path . -Exclude $exclude
Compress-Archive -Path $files -DestinationPath "estudos.zip" -Force