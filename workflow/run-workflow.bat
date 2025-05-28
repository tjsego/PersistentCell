@echo off

cd %~dp0..

call workflow/setup/config

call conda activate %PC_CONDAENVNAME_COMPARE%
set PYTHONPATH=%~dp0..

python -m workflow %*
