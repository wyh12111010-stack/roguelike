# 分析精灵图规格（PowerShell 版本）
param(
    [Parameter(Mandatory=$true)]
    [string]$ImagePath
)

Add-Type -AssemblyName System.Drawing

try {
    $img = [System.Drawing.Image]::FromFile($ImagePath)
    
    Write-Host "📊 图像分析: $ImagePath" -ForegroundColor Cyan
    Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    Write-Host "尺寸: $($img.Width) × $($img.Height) 像素"
    Write-Host "格式: $($img.RawFormat.Guid)"
    
    # 检查透明度
    $hasAlpha = $img.PixelFormat -match "Alpha"
    if ($hasAlpha) {
        Write-Host "透明背景: ✅ 是" -ForegroundColor Green
    } else {
        Write-Host "透明背景: ❌ 否" -ForegroundColor Red
    }
    
    # 假设是 2×2 精灵表
    $frameW = [math]::Floor($img.Width / 2)
    $frameH = [math]::Floor($img.Height / 2)
    Write-Host "`n如果是 2×2 精灵表:"
    Write-Host "  单帧尺寸: $frameW × $frameH 像素"
    
    # 检查是否符合规格
    Write-Host "`n✅ 规格检查:"
    if ($frameH -ge 32 -and $frameH -le 48) {
        Write-Host "  ✅ 高度符合 (32-48px): ${frameH}px" -ForegroundColor Green
    } elseif ($frameH -ge 28 -and $frameH -le 40) {
        Write-Host "  ⚠️  敌人尺寸 (28-40px): ${frameH}px" -ForegroundColor Yellow
    } elseif ($frameH -ge 48 -and $frameH -le 64) {
        Write-Host "  ⚠️  Boss 尺寸 (48-64px): ${frameH}px" -ForegroundColor Yellow
    } else {
        Write-Host "  ❌ 高度不符合: ${frameH}px (需要 32-48px)" -ForegroundColor Red
    }
    
    # 估算像素密度
    if ($frameH -le 48) {
        $pixelBlockSize = $frameH / 8
        Write-Host "  估算像素块: ~$([math]::Round($pixelBlockSize, 1))px/块"
        if ($pixelBlockSize -ge 5 -and $pixelBlockSize -le 8) {
            Write-Host "  ✅ 像素密度合适 (5-8px/块)" -ForegroundColor Green
        } else {
            Write-Host "  ⚠️  像素可能太细或太粗" -ForegroundColor Yellow
        }
    }
    
    Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    
    $img.Dispose()
    
} catch {
    Write-Host "❌ 错误: $_" -ForegroundColor Red
    exit 1
}
