param(
    [Parameter(Mandatory=$true)][string]$InputPath,
    [Parameter(Mandatory=$true)][string]$OutputDirectory,
    [int]$MaxSlides = 0
)
# Adopted from the verified workspace fixture renderer; only this deck is opened.
$ErrorActionPreference = 'Stop'
$source = (Resolve-Path -LiteralPath $InputPath).Path
$target = [IO.Path]::GetFullPath($OutputDirectory)
if (Test-Path -LiteralPath $target) { throw "Render target already exists: $target" }
$preexisting = @(Get-Process POWERPNT -ErrorAction SilentlyContinue | Select-Object -ExpandProperty Id)
function Get-SourceHash([string]$Path) {
    $sha = [Security.Cryptography.SHA256]::Create()
    try { return [BitConverter]::ToString($sha.ComputeHash([IO.File]::ReadAllBytes($Path))).Replace('-', '') }
    finally { $sha.Dispose() }
}
$before = Get-SourceHash $source
$app = $null
$deck = $null
try {
    $app = New-Object -ComObject PowerPoint.Application
    $deck = $app.Presentations.Open($source, -1, 0, 0)
    $count = $deck.Slides.Count
    if ($MaxSlides -gt 0) { $count = [Math]::Min($count, $MaxSlides) }
    $height = [int][Math]::Round(1280 * $deck.PageSetup.SlideHeight / $deck.PageSetup.SlideWidth)
    [void][IO.Directory]::CreateDirectory($target)
    for ($index = 1; $index -le $count; $index++) {
        $slide = $deck.Slides.Item($index)
        try { $slide.Export((Join-Path $target ('slide-{0:D3}.png' -f $index)), 'PNG', 1280, $height) }
        finally { [void][Runtime.InteropServices.Marshal]::FinalReleaseComObject($slide) }
    }
    $after = Get-SourceHash $source
    if ($before -ne $after) { throw 'PowerPoint source changed during read-only rendering' }
    [pscustomobject]@{ status='PASS'; renderer='Microsoft PowerPoint'; slides=$count; sourceSha256=$after; sourcePreserved=$true; preexistingPowerPointPids=$preexisting } | ConvertTo-Json -Compress
} finally {
    if ($null -ne $deck) { $deck.Close(); [void][Runtime.InteropServices.Marshal]::FinalReleaseComObject($deck) }
    if ($null -ne $app) {
        if ($preexisting.Count -eq 0) { $app.Quit() }
        [void][Runtime.InteropServices.Marshal]::FinalReleaseComObject($app)
    }
}
