# Script PowerShell para instalar dependências do Whisper no Windows

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "INSTALACAO DE DEPENDENCIAS DO WHISPER" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Verificar se pip está disponível
Write-Host "[1/3] Verificando pip..." -ForegroundColor Yellow
try {
    $pipVersion = python -m pip --version 2>&1
    Write-Host "    OK: pip disponivel" -ForegroundColor Green
} catch {
    Write-Host "    ERRO: pip nao encontrado. Instale Python primeiro." -ForegroundColor Red
    exit 1
}

# Instalar openai-whisper
Write-Host ""
Write-Host "[2/3] Instalando openai-whisper..." -ForegroundColor Yellow
Write-Host "    (Isso pode demorar alguns minutos...)" -ForegroundColor Gray
python -m pip install openai-whisper torch

if ($LASTEXITCODE -eq 0) {
    Write-Host "    OK: openai-whisper instalado com sucesso!" -ForegroundColor Green
} else {
    Write-Host "    ERRO: Falha ao instalar openai-whisper" -ForegroundColor Red
    exit 1
}

# Verificar FFmpeg
Write-Host ""
Write-Host "[3/3] Verificando FFmpeg..." -ForegroundColor Yellow

# Verificar se FFmpeg já está instalado
$ffmpegPath = Get-Command ffmpeg -ErrorAction SilentlyContinue

if ($ffmpegPath) {
    Write-Host "    OK: FFmpeg ja esta instalado!" -ForegroundColor Green
    Write-Host "    Caminho: $($ffmpegPath.Source)" -ForegroundColor Gray
} else {
    Write-Host "    AVISO: FFmpeg nao encontrado no sistema" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "    Para instalar FFmpeg no Windows, voce tem 3 opcoes:" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "    OPCAO 1 - Usando winget (recomendado):" -ForegroundColor Yellow
    Write-Host "        winget install FFmpeg" -ForegroundColor White
    Write-Host ""
    Write-Host "    OPCAO 2 - Usando Chocolatey:" -ForegroundColor Yellow
    Write-Host "        choco install ffmpeg" -ForegroundColor White
    Write-Host ""
    Write-Host "    OPCAO 3 - Download manual:" -ForegroundColor Yellow
    Write-Host "        1. Acesse: https://ffmpeg.org/download.html" -ForegroundColor White
    Write-Host "        2. Baixe a versao para Windows" -ForegroundColor White
    Write-Host "        3. Extraia e adicione a pasta 'bin' ao PATH do sistema" -ForegroundColor White
    Write-Host ""
    Write-Host "    IMPORTANTE: Apos instalar, reinicie o terminal ou o servidor Flask!" -ForegroundColor Red
}

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "INSTALACAO CONCLUIDA!" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Proximos passos:" -ForegroundColor Yellow
Write-Host "1. Se FFmpeg foi instalado agora, reinicie o terminal" -ForegroundColor White
Write-Host "2. Execute: python check_whisper_deps.py para verificar" -ForegroundColor White
Write-Host "3. Reinicie o servidor Flask" -ForegroundColor White

