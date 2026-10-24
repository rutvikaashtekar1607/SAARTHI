# build_m4.ps1 - builds m4_bench.elf (Cortex-M4, Mbed TLS 3.6.7) and copies the run files to C:\SAARTHI_M4
# Run from this folder in the VS Code PowerShell terminal:  .\build_m4.ps1
$ErrorActionPreference = "Stop"
Set-Location $PSScriptRoot
$gcc = "arm-none-eabi-gcc"
& $gcc --version | Select-Object -First 1
$aes = Get-ChildItem "..\02_Crypto_Benchmark\mbedtls-3.6.7" -Recurse -Filter aes.c -ErrorAction SilentlyContinue |
       Where-Object { $_.Directory.Name -eq "library" } | Select-Object -First 1
if (-not $aes) { throw "Mbed TLS source (library\aes.c) not found under 02_Crypto_Benchmark\mbedtls-3.6.7" }
$mbed = $aes.Directory.Parent.FullName
Write-Host "Using Mbed TLS source: $mbed"
$work = "C:\SAARTHI_M4"
New-Item -ItemType Directory -Force $work | Out-Null
$obj = Join-Path $work "obj"
New-Item -ItemType Directory -Force $obj | Out-Null

$cflags = @("-mcpu=cortex-m4", "-mthumb", "-mfloat-abi=soft", "-O2", "-ffunction-sections", "-fdata-sections",
            "-Wall", '-DMBEDTLS_CONFIG_FILE=<config_m4.h>', "-I.", "-I$mbed\include", "-I$mbed\library")

$sources = @(Get-ChildItem "$mbed\library\*.c") + @(Get-Item ".\m4_bench.c", ".\startup.c")
$i = 0
foreach ($s in $sources) {
    $i++
    Write-Host ("[{0}/{1}] {2}" -f $i, $sources.Count, $s.Name)
    & $gcc @cflags -c $s.FullName -o (Join-Path $obj ($s.BaseName + ".o"))
    if ($LASTEXITCODE -ne 0) { throw "compile failed: $($s.Name)" }
}

$objs = Get-ChildItem "$obj\*.o" | ForEach-Object { $_.FullName }
& $gcc "-mcpu=cortex-m4" "-mthumb" "-mfloat-abi=soft" "--specs=nano.specs" "--specs=nosys.specs" "-nostartfiles" `
    "-T" ".\linker.ld" "-Wl,--gc-sections" "-Wl,-Map=$work\m4_bench.map" @objs "-o" "$work\m4_bench.elf"
if ($LASTEXITCODE -ne 0) { throw "link failed" }

Copy-Item ".\run_m4.resc" "$work\run_m4.resc" -Force
& "arm-none-eabi-size" "$work\m4_bench.elf"
Write-Host "Built $work\m4_bench.elf"
