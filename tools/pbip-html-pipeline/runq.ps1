param([string]$QueryFile, [string]$OutFile, [int]$Port = 0)
# Run a DAX query file against an open Power BI Desktop model and save the rows as JSON.
# -Port 0 (default): try every open Desktop model, newest first, and use the first one where the
# query runs - so an extra empty "Untitled" window or another report does not hijack the run.
$ErrorActionPreference = 'Stop'
$query = [IO.File]::ReadAllText($QueryFile, [Text.Encoding]::UTF8)
Add-Type -Path (Join-Path (Split-Path (Get-Process PBIDesktop | Select-Object -First 1).Path) 'Microsoft.PowerBI.AdomdClient.dll')

if ($Port -ne 0) { $ports = @($Port) } else {
  $ports = Get-ChildItem "$env:USERPROFILE\Microsoft\Power BI Desktop Store App\AnalysisServicesWorkspaces\*\Data\msmdsrv.port.txt", "$env:LOCALAPPDATA\Microsoft\Power BI Desktop\AnalysisServicesWorkspaces\*\Data\msmdsrv.port.txt" -ErrorAction SilentlyContinue |
    Sort-Object LastWriteTime -Descending | ForEach-Object { [int]([IO.File]::ReadAllText($_.FullName, [Text.Encoding]::Unicode).Trim()) } | Select-Object -Unique
}
if (-not $ports) { throw "No open Power BI Desktop model found - open the PBIP in Desktop first." }

$errors = @()
foreach ($p in $ports) {
  $conn = New-Object Microsoft.AnalysisServices.AdomdClient.AdomdConnection("Data Source=localhost:$p")
  try {
    $conn.Open()
    $cmd = $conn.CreateCommand(); $cmd.CommandText = $query
    $r = $cmd.ExecuteReader()
    $rows = @()
    while ($r.Read()) {
      $o = [ordered]@{}
      for ($i = 0; $i -lt $r.FieldCount; $i++) { $o[$r.GetName($i)] = [string]$r.GetValue($i) }
      $rows += [pscustomobject]$o
    }
    $r.Close(); $conn.Close()
    [IO.File]::WriteAllText($OutFile, (ConvertTo-Json -InputObject $rows -Depth 3), (New-Object Text.UTF8Encoding($false)))
    "rows: $($rows.Count) (port $p)"
    exit 0
  } catch {
    $errors += "port ${p}: $($_.Exception.Message.Split([Environment]::NewLine)[0])"
    try { $conn.Close() } catch {}
  }
}
throw ("The query failed on every open Desktop model:`n" + ($errors -join "`n"))
