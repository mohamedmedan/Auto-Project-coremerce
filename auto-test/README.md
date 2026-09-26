# Coremerce Selenium Test Suite

## Setup
    pip install -r requirements.txt

## Run (interactive)
    python run_tests.py

## Run (CLI)
    python run_tests.py --feature login
    python run_tests.py --feature register
    python run_tests.py --feature all
    python run_tests.py --feature login --keys LOGIN_001,LOGIN_007
    python run_tests.py --list

## Test Keys
Login: LOGIN_001 .. LOGIN_020
Register: REGISTER_001 .. REGISTER_005

Configure `config/config.json` before running.
