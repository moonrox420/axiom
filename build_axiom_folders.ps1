$ErrorActionPreference = "Stop"

$workspaceRoot = "c:\Users\droxa\axiom"
$sourceFile = Join-Path $workspaceRoot "axiom-files.md"

if (-not (Test-Path $sourceFile)) {
    Write-Error "Source file $sourceFile does not exist."
    exit 1
}

$lines = [System.IO.File]::ReadAllLines($sourceFile)

$headers = @()
for ($i = 0; $i -lt $lines.Length; $i++) {
    if ($lines[$i] -match '^```[a-zA-Z0-9_-]*\s+name=([^\r\n]+)') {
        $headers += [PSCustomObject]@{
            Index = $i
            FileName = $matches[1].Trim()
        }
    }
}

Write-Output "Found $($headers.Count) file specifications in axiom-files.md"

$createdFiles = @()

for ($k = 0; $k -lt $headers.Count; $k++) {
    $cur = $headers[$k]
    $nextStart = if ($k -lt $headers.Count - 1) { $headers[$k+1].Index } else { $lines.Length }
    
    $lastFence = -1
    for ($idx = $cur.Index + 1; $idx -lt $nextStart; $idx++) {
        if ($lines[$idx] -match '^```\s*$') {
            $lastFence = $idx
        }
    }
    
    if ($lastFence -eq -1) {
        Write-Error "No closing fence found for $($cur.FileName) at header index $k"
        exit 1
    }
    
    $fileLines = $lines[($cur.Index + 1)..($lastFence - 1)]
    $fileContent = [string]::Join("`n", $fileLines)
    
    # Handle files
    $targetRelPaths = @()
    if ($k -eq 6 -and $cur.FileName -eq "README.md") {
        # MVP README
        $targetRelPaths += "README_MVP.md"
        $targetRelPaths += "app/README.md"
    } elseif ($k -eq 65 -and $cur.FileName -eq "README.md") {
        # Full-stack README
        $targetRelPaths += "README.md"
    } else {
        $targetRelPaths += $cur.FileName
    }
    
    foreach ($relPath in $targetRelPaths) {
        $fullPath = Join-Path $workspaceRoot $relPath
        $dir = Split-Path -Parent $fullPath
        if (-not (Test-Path $dir)) {
            New-Item -ItemType Directory -Path $dir -Force | Out-Null
        }
        
        [System.IO.File]::WriteAllText($fullPath, $fileContent, [System.Text.Encoding]::UTF8)
        $createdFiles += [PSCustomObject]@{
            RelativePath = $relPath
            Lines = $fileLines.Length
            Bytes = (Get-Item $fullPath).Length
        }
    }
}

# Add standard frontend boilerplate files for Vite & Tailwind integration if missing
$frontendIndexHtml = Join-Path $workspaceRoot "frontend/index.html"
if (-not (Test-Path $frontendIndexHtml)) {
    $htmlContent = @"
<!doctype html>
<html lang="en">
  <head>
    <meta charset="UTF-8" />
    <link rel="icon" type="image/svg+xml" href="/vite.svg" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
    <title>Axiom - Operational Platform</title>
  </head>
  <body>
    <div id="root"></div>
    <script type="module" src="/src/main.tsx"></script>
  </body>
</html>
"@
    [System.IO.File]::WriteAllText($frontendIndexHtml, $htmlContent, [System.Text.Encoding]::UTF8)
    $createdFiles += [PSCustomObject]@{
        RelativePath = "frontend/index.html"
        Lines = 12
        Bytes = (Get-Item $frontendIndexHtml).Length
    }
}

$tailwindConfig = Join-Path $workspaceRoot "frontend/tailwind.config.js"
if (-not (Test-Path $tailwindConfig)) {
    $twContent = @"
/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {},
  },
  plugins: [],
}
"@
    [System.IO.File]::WriteAllText($tailwindConfig, $twContent, [System.Text.Encoding]::UTF8)
    $createdFiles += [PSCustomObject]@{
        RelativePath = "frontend/tailwind.config.js"
        Lines = 11
        Bytes = (Get-Item $tailwindConfig).Length
    }
}

$postcssConfig = Join-Path $workspaceRoot "frontend/postcss.config.js"
if (-not (Test-Path $postcssConfig)) {
    $pcContent = @"
export default {
  plugins: {
    tailwindcss: {},
    autoprefixer: {},
  },
}
"@
    [System.IO.File]::WriteAllText($postcssConfig, $pcContent, [System.Text.Encoding]::UTF8)
    $createdFiles += [PSCustomObject]@{
        RelativePath = "frontend/postcss.config.js"
        Lines = 7
        Bytes = (Get-Item $postcssConfig).Length
    }
}

$backendEnv = Join-Path $workspaceRoot "backend/.env"
$backendEnvExample = Join-Path $workspaceRoot "backend/.env.example"
if ((Test-Path $backendEnvExample) -and (-not (Test-Path $backendEnv))) {
    Copy-Item $backendEnvExample $backendEnv
    $createdFiles += [PSCustomObject]@{
        RelativePath = "backend/.env"
        Lines = (Get-Content $backendEnv).Length
        Bytes = (Get-Item $backendEnv).Length
    }
}

Write-Output "Successfully generated $($createdFiles.Count) files."
$createdFiles | Format-Table -Property RelativePath, Lines, Bytes -AutoSize | Out-String | Write-Output
