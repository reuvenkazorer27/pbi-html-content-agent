# Capture a screen region repeatedly (to see a short HTML Content entrance animation in Power BI Desktop).
#   powershell -File burst.ps1 -Out frames_dir -X 60 -Y 285 -W 1280 -H 125 -Count 30 -DelayMs 60
param([string]$Out = "burst", [int]$X = 60, [int]$Y = 285, [int]$W = 1280, [int]$H = 125, [int]$Count = 30, [int]$DelayMs = 60)
Add-Type -AssemblyName System.Drawing
New-Item -ItemType Directory -Force $Out | Out-Null
$sw = [Diagnostics.Stopwatch]::StartNew()
for ($i = 0; $i -lt $Count; $i++) {
  $bmp = New-Object Drawing.Bitmap $W, $H
  $g = [Drawing.Graphics]::FromImage($bmp)
  $g.CopyFromScreen($X, $Y, 0, 0, $bmp.Size)
  $bmp.Save((Join-Path $Out ("f{0:D3}_{1}ms.png" -f $i, $sw.ElapsedMilliseconds)), [Drawing.Imaging.ImageFormat]::Png)
  $g.Dispose(); $bmp.Dispose()
  Start-Sleep -Milliseconds $DelayMs
}
"captured $Count frames in $($sw.ElapsedMilliseconds) ms"
