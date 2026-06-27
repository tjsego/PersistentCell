#!/bin/bash

PC_SETUP_THISDIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" ; pwd -P )"

source ${PC_SETUP_THISDIR}/config.sh
source ${PC_CONDAENVSH}

# Ensure clean install
conda env remove -n ${PC_CONDAENVNAME_COMPARE}
conda env remove -n ${PC_CONDAENVNAME_DERIVED}

# Install environments
conda env create -f ${PC_SETUP_THISDIR}/env-compare.yml
conda env create -f ${PC_SETUP_THISDIR}/env-derived.yml

# Get MS fonts if on Linux
if [[ "$(uname)" == "Linux" ]]; then
  conda install -n ${PC_CONDAENVNAME_COMPARE} -c conda-forge -y mscorefonts
  rm ~/.cache/matplotlib -rf
fi