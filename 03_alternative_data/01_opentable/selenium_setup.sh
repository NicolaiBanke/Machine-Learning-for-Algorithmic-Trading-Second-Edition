#!/usr/bin/env bash
# get latest - https://github.com/mozilla/geckodriver/releases
wget https://github.com/mozilla/geckodriver/releases/download/v0.36.0/geckodriver-v0.36.0-linux64.tar.gz
tar -xvzf geckodriver-*
chmod +x geckodriver
sudo mv geckodriver /usr/local/bin/