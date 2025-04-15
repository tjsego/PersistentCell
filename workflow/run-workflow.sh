#!/bin/bash

PC_THISDIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" ; pwd -P )"

cd ${PC_THISDIR}/..

source workflow/setup/config.sh
source ${PC_CONDAENVSH}
conda activate ${PC_CONDAENVNAME_COMPARE}
export PYTHONPATH=${PC_THISDIR}/..

python -m workflow "$@"
