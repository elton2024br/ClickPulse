@echo off
chcp 65001 >nul 2>&1
title ClickPulse - Instalador
color 0A

echo.
echo  ╔══════════════════════════════════════════════╗
echo  ║         ClickPulse - Instalador v1.0         ║
echo  ╚══════════════════════════════════════════════╝
echo.

:: Verificar Python
echo  [1/4] Verificando Python...
python --version >nul 2>&1
if errorlevel 1 (
    echo.
    echo  [ERRO] Python nao encontrado!
    echo  Baixe em: https://www.python.org/downloads/
    echo  IMPORTANTE: Marque "Add Python to PATH" durante a instalacao.
    echo.
    pause
    exit /b 1
)
for /f "tokens=2" %%i in ('python --version 2^>^&1') do echo  Python %%i encontrado!

:: Criar ambiente virtual
echo.
echo  [2/4] Criando ambiente virtual...
if not exist "venv" (
    python -m venv venv
    echo  Ambiente virtual criado!
) else (
    echo  Ambiente virtual ja existe.
)

:: Instalar dependencias
echo.
echo  [3/4] Instalando dependencias...
call venv\Scripts\activate.bat
pip install -r requirements.txt --quiet
echo  Dependencias instaladas!

:: Gerar executavel
echo.
echo  [4/4] Gerando executavel ClickPulse.exe...
pip install pyinstaller --quiet
pyinstaller --onefile --windowed --icon=assets\icon.png --name=ClickPulse --add-data="assets;assets" main.py --noconfirm --clean >nul 2>&1

if exist "dist\ClickPulse.exe" (
    echo.
    echo  ╔══════════════════════════════════════════════╗
    echo  ║          INSTALACAO CONCLUIDA!                ║
    echo  ╚══════════════════════════════════════════════╝
    echo.
    echo  O executavel foi gerado em: dist\ClickPulse.exe
    echo.
    echo  Voce pode:
    echo    1. Executar dist\ClickPulse.exe diretamente
    echo    2. Criar um atalho na area de trabalho
    echo    3. Copiar para qualquer pasta
    echo.
    
    :: Criar atalho na area de trabalho
    set /p criar_atalho="  Deseja criar atalho na area de trabalho? (S/N): "
    if /i "%criar_atalho%"=="S" (
        powershell -Command "$ws = New-Object -ComObject WScript.Shell; $s = $ws.CreateShortcut([IO.Path]::Combine([Environment]::GetFolderPath('Desktop'), 'ClickPulse.lnk')); $s.TargetPath = '%~dp0dist\ClickPulse.exe'; $s.WorkingDirectory = '%~dp0dist'; $s.IconLocation = '%~dp0dist\ClickPulse.exe'; $s.Description = 'Monitor de atividade do mouse'; $s.Save()"
        echo  Atalho criado na area de trabalho!
    )
) else (
    echo.
    echo  [AVISO] Nao foi possivel gerar o .exe automaticamente.
    echo  Voce pode usar o ClickPulse.bat para iniciar o app.
)

echo.
echo  Pressione qualquer tecla para fechar...
pause >nul
