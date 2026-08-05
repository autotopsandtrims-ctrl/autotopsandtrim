# Extract every image + font from the bundle manifest into real files.
# Photos are named from the descriptive placeholder labels in the page template.
Add-Type -AssemblyName System.Web.Extensions

$scratch = "C:\Users\table\AppData\Local\Temp\claude\c--Claude-Code\940bf43c-9ee6-488f-9331-6e7b2b9261d7\scratchpad"
$repo    = "$scratch\autotopsandtrim"
$bundle  = "$repo\index.html"
$outDir  = "$repo\assets"
$fontDir = "$repo\assets\fonts"

New-Item -ItemType Directory -Force -Path $outDir  | Out-Null
New-Item -ItemType Directory -Force -Path $fontDir | Out-Null

$lines = [System.IO.File]::ReadAllLines($bundle)
$ser = New-Object System.Web.Script.Serialization.JavaScriptSerializer
$ser.MaxJsonLength = [int]::MaxValue

$manifest = $ser.DeserializeObject($lines[369])
$html     = $ser.DeserializeObject($lines[381])

# ---- build uuid -> friendly name map from the image-slot labels ----
$names = @{}
foreach ($m in [regex]::Matches($html, '<image-slot\s+id="([^"]*)"\s+src="([^"]*)"[^>]*placeholder="([^"]*)"')) {
    $id    = $m.Groups[1].Value
    $uuid  = $m.Groups[2].Value
    $label = $m.Groups[3].Value
    if ($names.ContainsKey($uuid)) { continue }   # first (most specific) slot wins

    $slug = $label.ToLower()
    $slug = $slug -replace '[\u2013\u2014]', '-'          # en/em dash
    $slug = $slug -replace '[^a-z0-9]+', '-'
    $slug = $slug.Trim('-')
    if ([string]::IsNullOrWhiteSpace($slug) -or $slug -eq 'post-image' -or $slug -eq 'article-photo') {
        $slug = $id.ToLower() -replace '[^a-z0-9]+','-'
    }
    # prefix gallery items so they sort in order
    if ($id -match '^g\d+$') { $slug = "$id-$slug" }
    $names[$uuid] = $slug
}

function Expand-GzipBytes([byte[]]$bytes) {
    $ms  = New-Object System.IO.MemoryStream(,$bytes)
    $gz  = New-Object System.IO.Compression.GZipStream($ms, [System.IO.Compression.CompressionMode]::Decompress)
    $out = New-Object System.IO.MemoryStream
    $gz.CopyTo($out)
    $gz.Dispose(); $ms.Dispose()
    return $out.ToArray()
}

$ext = @{ 'image/webp'='webp'; 'image/jpeg'='jpg'; 'image/png'='png'; 'font/woff2'='woff2' }
$map = @{}   # uuid -> relative path, for rewriting the HTML later
$n = 0; $skipped = 0

foreach ($uuid in $manifest.Keys) {
    $entry = $manifest[$uuid]
    $mime  = [string]$entry['mime']
    if (-not $ext.ContainsKey($mime)) { $skipped++; continue }   # skip the JS bundles

    $raw = [Convert]::FromBase64String([string]$entry['data'])
    if ($entry['compressed']) { $raw = Expand-GzipBytes $raw }

    $e = $ext[$mime]
    if ($mime -eq 'font/woff2') {
        $file = "font-$($uuid.Substring(0,8)).$e"
        $path = Join-Path $fontDir $file
        $rel  = "assets/fonts/$file"
    } else {
        $base = if ($names.ContainsKey($uuid)) { $names[$uuid] } else { "photo-$($uuid.Substring(0,8))" }
        $file = "$base.$e"
        $path = Join-Path $outDir $file
        # guard against a duplicate filename
        $i = 2
        while (Test-Path $path) { $file = "$base-$i.$e"; $path = Join-Path $outDir $file; $i++ }
        $rel = "assets/$file"
    }

    [System.IO.File]::WriteAllBytes($path, $raw)
    $map[$uuid] = $rel
    $n++
}

$map | Export-Clixml "$scratch\uuid_map.xml"
"Extracted: $n files  (skipped $skipped non-image/font entries)"
"Images: $((Get-ChildItem $outDir -File).Count)   Fonts: $((Get-ChildItem $fontDir -File).Count)"
"Total asset bytes: {0:N0}" -f ((Get-ChildItem $outDir -Recurse -File | Measure-Object Length -Sum).Sum)
