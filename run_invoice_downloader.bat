@echo off
cd /d %~dp0
pipenv run python auto_dl.py
pause