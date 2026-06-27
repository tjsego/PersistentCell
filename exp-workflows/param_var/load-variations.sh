#!/bin/bash

PVEXP_THISDIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" ; pwd -P )"

source ${PVEXP_THISDIR}/../../workflow/setup/config.sh
source ${PC_CONDAENVSH}
conda activate ${PC_CONDAENVNAME_COMPARE}
export PYTHONPATH=${PVEXP_THISDIR}/..:${PVEXP_THISDIR}/../..

python ${PVEXP_THISDIR}/load_variations.py "$@"
