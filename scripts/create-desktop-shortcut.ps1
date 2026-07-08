# Лаунчер: иконка, запуск и ярлык на рабочий стол
$ErrorActionPreference = 'Stop'

Add-Type -AssemblyName System.Drawing

$appDir = Join-Path $env:LOCALAPPDATA 'NeuroAuditor'
if (-not (Test-Path $appDir)) { New-Item -ItemType Directory -Path $appDir -Force | Out-Null }

# Корень проекта — на два уровня выше этого скрипта (scripts/ -> fin-auditor/)
$projectDir = (Resolve-Path (Join-Path $PSScriptRoot '..')).Path
$chrome = 'C:\Program Files\Google\Chrome\Application\chrome.exe'
$appUrl = 'http://localhost:5173'
$icoPath = Join-Path $appDir 'icon.ico'
$batPath = Join-Path $appDir 'launch.bat'
$desktop = [Environment]::GetFolderPath('Desktop')

# Имя приложения кириллицей через коды символов (избегаем проблем с кодировкой в парсере)
$appName = -join @([char]0x41D,[char]0x435,[char]0x439,[char]0x440,[char]0x43E,[char]0x430,[char]0x443,[char]0x434,[char]0x438,[char]0x442,[char]0x43E,[char]0x440)
$lnkPath = Join-Path $desktop ($appName + '.lnk')

# --- 1. Рисуем иконку (.ico) ---
function Draw-Icon {
    param([int]$size)
    $bmp = New-Object System.Drawing.Bitmap($size, $size)
    $g = [System.Drawing.Graphics]::FromImage($bmp)
    $g.SmoothingMode = [System.Drawing.Drawing2D.SmoothingMode]::AntiAlias
    $g.Clear([System.Drawing.Color]::Transparent)

    $m = [int]([double]$size * 0.0625)
    $r = [int]([double]$size * 0.22)
    $rect = New-Object System.Drawing.Rectangle($m, $m, $size - 2*$m, $size - 2*$m)

    $colorA = [System.Drawing.ColorTranslator]::FromHtml('#2563EB')
    $colorB = [System.Drawing.ColorTranslator]::FromHtml('#7C3AED')
    $br = New-Object System.Drawing.Drawing2D.LinearGradientBrush($rect, $colorA, $colorB, [System.Drawing.Drawing2D.LinearGradientMode]::ForwardDiagonal)

    $path = New-Object System.Drawing.Drawing2D.GraphicsPath
    $path.AddArc($rect.X, $rect.Y, $r, $r, 180, 90)
    $path.AddArc($rect.Right - $r, $rect.Y, $r, $r, 270, 90)
    $path.AddArc($rect.Right - $r, $rect.Bottom - $r, $r, $r, 0, 90)
    $path.AddArc($rect.X, $rect.Bottom - $r, $r, $r, 90, 90)
    $path.CloseFigure()
    $g.FillPath($br, $path)

    $penW = [int]([double]$size * 0.065)
    if ($penW -lt 2) { $penW = 2 }
    $pen = New-Object System.Drawing.Pen([System.Drawing.Color]::White, $penW)
    $pen.StartCap = [System.Drawing.Drawing2D.LineCap]::Round
    $pen.EndCap = [System.Drawing.Drawing2D.LineCap]::Round
    $pen.LineJoin = [System.Drawing.Drawing2D.LineJoin]::Round

    $p1 = New-Object System.Drawing.PointF([float]([double]$size*0.31), [float]([double]$size*0.66))
    $p2 = New-Object System.Drawing.PointF([float]([double]$size*0.50), [float]([double]$size*0.34))
    $p3 = New-Object System.Drawing.PointF([float]([double]$size*0.69), [float]([double]$size*0.66))
    $g.DrawLines($pen, @($p1, $p2, $p3))

    $dotR = [int]([double]$size * 0.045)
    if ($dotR -lt 2) { $dotR = 2 }
    $dotX = [int]([double]$size * 0.50)
    $dotY = [int]([double]$size * 0.66)
    $g.FillEllipse([System.Drawing.Brushes]::White, $dotX - $dotR, $dotY - $dotR, 2*$dotR, 2*$dotR)

    $g.Dispose()
    return $bmp
}

$sizes = @(16, 32, 48, 64, 128, 256)
$bitmaps = New-Object System.Collections.ArrayList
foreach ($s in $sizes) {
    [void]$bitmaps.Add((Draw-Icon -size $s))
}

# Собираем много-размерный ICO (PNG-сжатые фреймы)
$pngList = New-Object System.Collections.ArrayList
foreach ($b in $bitmaps) {
    $ms = New-Object System.IO.MemoryStream
    $b.Save($ms, [System.Drawing.Imaging.ImageFormat]::Png)
    [void]$pngList.Add([byte[]]$ms.ToArray())
    $ms.Dispose()
}

$fs = [System.IO.File]::Create($icoPath)
$bw = New-Object System.IO.BinaryWriter $fs
$bw.Write([uint16]0)
$bw.Write([uint16]1)
$bw.Write([uint16]$bitmaps.Count)

$offset = 6 + ($bitmaps.Count * 16)
for ($i = 0; $i -lt $bitmaps.Count; $i++) {
    $s = $sizes[$i]
    if ($s -ge 256) { $bw.Write([byte]0) } else { $bw.Write([byte]$s) }
    if ($s -ge 256) { $bw.Write([byte]0) } else { $bw.Write([byte]$s) }
    $bw.Write([byte]0)
    $bw.Write([byte]0)
    $bw.Write([uint16]1)
    $bw.Write([uint16]32)
    $bw.Write([uint32]$pngList[$i].Length)
    $bw.Write([uint32]$offset)
    $offset += $pngList[$i].Length
}
for ($i = 0; $i -lt $bitmaps.Count; $i++) {
    $bw.Write($pngList[$i])
}
$bw.Flush()
$bw.Dispose()
$fs.Dispose()
foreach ($b in $bitmaps) { $b.Dispose() }
Write-Output ("Icon created: " + $icoPath)

# --- 2. Скрипт запуска (launch.bat) ---
$batLines = @(
    '@echo off',
    ('title ' + $appName),
    ('cd /d "' + $projectDir + '"'),
    'docker compose up -d',
    'ping -n 4 127.0.0.1 >nul',
    ('start "" "' + $chrome + '" --app=' + $appUrl + ' --name="' + $appName + '"')
)
$batContent = ($batLines -join "`r`n") + "`r`n"
# bat в кодировке ANSI (Windows-1251) чтобы кириллица в title/name отображалась в консоли
$enc1251 = [System.Text.Encoding]::GetEncoding(1251)
[System.IO.File]::WriteAllBytes($batPath, $enc1251.GetBytes($batContent))
Write-Output ("Launcher script: " + $batPath)

# --- 3. Ярлык на рабочем столе ---
$shell = New-Object -ComObject WScript.Shell
$lnk = $shell.CreateShortcut($lnkPath)
$lnk.TargetPath = $batPath
$lnk.WorkingDirectory = $appDir
$lnk.IconLocation = $icoPath + ',0'
$lnk.WindowStyle = 7
$lnk.Description = 'Запуск ' + $appName
$lnk.Save()
Write-Output ("Shortcut created: " + $lnkPath)

Write-Output 'Done.'
