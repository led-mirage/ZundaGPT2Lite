@echo off
setlocal

cd /d %~dp0..

set VENV_PYTHON=venv\Scripts\python.exe
set VENV_PYINSTALLER=venv\Scripts\pyinstaller.exe
set VENV_MAKE_VERSION=venv\Scripts\pyivf-make_version.exe

if exist build rmdir /s /q build

"%VENV_PYTHON%" tools/update_version_yaml.py
"%VENV_PYTHON%" tools/update_app_manifest.py

"%VENV_MAKE_VERSION%" ^
    --source-format yaml ^
    --metadata-source "build_tools/version.yaml" ^
    --outfile "build_tools/version.txt"

"%VENV_PYINSTALLER%" ^
    --onefile ^
    --noconsole ^
    --paths=./app ^
    --add-data "app/html;html" ^
    --name ZundaGPT2Lite ^
    --icon "assets/ZundaGPT2.ico" ^
    --splash "assets/ZundaGPT2_splash.png" ^
    --version-file "build_tools/version.txt" ^
    --manifest "build_tools/app.manifest" ^
    app/main.py
 