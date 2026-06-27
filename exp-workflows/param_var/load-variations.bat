@echo off

call %~dp0../../workflow/setup/config

call conda activate %PC_CONDAENVNAME_COMPARE%
set PYTHONPATH=%~dp0..;%~dp0../..
python %~dp0load_variations.py %*