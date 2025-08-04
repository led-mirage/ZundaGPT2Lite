if exist build rmdir /s /q build
python update_version_yaml.py
pyivf-make_version --source-format yaml --metadata-source version.yaml --outfile version.txt
pyinstaller --onefile --noconsole --paths=./app --add-data "./app/html;html" --name ZundaGPT2Lite --icon assets/ZundaGPT2.ico --splash assets/ZundaGPT2_splash.png --version-file=version.txt app/main.py
