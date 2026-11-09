param([string]$QueryFile, [string]$OutFile, [int]$Port = 0)
$ErrorActionPreference = 'Stop'
if ($Port -eq 0) {  # newest open Desktop model
  $f = Get-ChildItem "$env:USERPROFILE\Microsoft\Power BI Desktop Store App\AnalysisServicesWorkspaces\*\Data\msmdsrv.port.txt", "$env:LOCALAPPDATA\Microsoft\Power BI Desktop\AnalysisServicesWorkspaces\*\Data\msmdsrv.port.txt" -ErrorAction SilentlyContinue | Sort-Object LastWriteTime -Descending | Select-Object -First 1
  $Port = [int]([IO.File]::ReadAllText($f.FullName, [Text.Encoding]::Unicode).Trim())
}
Add-Type -Path (Join-Path (Split-Path (Get-Process PBIDesktop | Select-Object -First 1).Path) 'Microsoft.PowerBI.AdomdClient.dll')
$conn = New-Object Microsoft.AnalysisServices.AdomdClient.AdomdConnection("Data Source=localhost:$Port")
$conn.Open()
$cmd = $conn.CreateCommand()
$cmd.CommandText = [IO.File]::ReadAllText($QueryFile, [Text.Encoding]::UTF8)
$r = $cmd.ExecuteReader()
$rows = @()
while ($r.Read()) {
  $o = [ordered]@{}
  for ($i = 0; $i -lt $r.FieldCount; $i++) { $o[$r.GetName($i)] = [string]$r.GetValue($i) }
  $rows += [pscustomobject]$o
}
$r.Close(); $conn.Close()
[IO.File]::WriteAllText($OutFile, (ConvertTo-Json -InputObject $rows -Depth 3), (New-Object Text.UTF8Encoding($false)))
"rows: $($rows.Count)"

