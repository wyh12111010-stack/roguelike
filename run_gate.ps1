param(
    [ValidateSet("quick", "nightly", "audit")]
    [string]$Preset = "quick",
    [ValidateSet("ui_text", "input_flow", "enemy_ai", "economy", "levels", "release")]
    [string]$ChangeType,
    [ValidateSet("combat", "economy", "level", "full")]
    [string]$Scope,
    [Nullable[int]]$Runs = $null,
    [string]$Levels = $null,
    [switch]$DryRun,
    [switch]$List
)

$argsList = @("-m", "tools.regression_gate")

if ($List) {
    $argsList += "--list"
}

if ($Preset) {
    $argsList += @("--preset", $Preset)
}

if ($ChangeType) {
    $argsList += @("--change-type", $ChangeType)
}

if ($Scope) {
    $argsList += @("--scope", $Scope)
}

if ($PSBoundParameters.ContainsKey("Runs") -and $Runs -gt 0) {
    $argsList += @("--runs", "$Runs")
}

if ($PSBoundParameters.ContainsKey("Levels") -and $Levels) {
    $normalizedLevels = @()
    foreach ($part in ($Levels -split ",")) {
        $v = $part.Trim()
        if ($v -ne "") {
            $normalizedLevels += [int]$v
        }
    }
    if ($normalizedLevels.Count -gt 0) {
    $argsList += "--levels"
    foreach ($lv in $normalizedLevels) {
        $argsList += "$lv"
    }
    }
}

if ($DryRun) {
    $argsList += "--dry-run"
}

Write-Host "Running: python $($argsList -join ' ')" -ForegroundColor Cyan
python @argsList
exit $LASTEXITCODE
