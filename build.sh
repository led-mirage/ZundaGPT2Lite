set -e
rm -rf build dist
pyinstaller --onefile --noconsole --paths=./app --add-data "./app/html:html" --add-data "assets/ZundaGPT2Lite-Icon.png:assets" --name ZundaGPT2Lite --splash assets/ZundaGPT2_splash.png app/main.py
