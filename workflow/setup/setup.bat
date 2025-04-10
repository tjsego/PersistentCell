@echo off

call %~dp0config

@rem Ensure clean install
call conda env remove -n %PC_CONDAENVNAME_COMPARE%
call conda env remove -n %PC_CONDAENVNAME_DERIVED%

@rem Install environments
call conda env create -f %~dp0env-compare.yml
call conda env create -f %~dp0env-derived.yml
call conda activate %PC_CONDAENVNAME_DERIVED%
Rscript -e "install.packages('celltrackR', repos='https://CRAN.R-project.org')"
conda deactivate