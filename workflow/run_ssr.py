"""
Runs the stochastic simulation reproducibility step of the workflow
"""
import json
import logging
import os
import pandas as pd
import sys
from typing import Type

from workflow import basic

sys.path.append(basic.dir_compare)

from ssr.basic import load_results
from ssr.analyze import efect_report

logger = logging.getLogger(__name__)


def _log_error(msg: str, err_type: Type[BaseException]):
    logger.error(msg)
    raise err_type(msg)


def do_ssr(_experiment_dir: str,
           do_appended=False,
           sig_figs=16,
           err_thresh=1E-3,
           **kwargs):
    logger.info(f'Doing compare      : {_experiment_dir}')
    logger.info(f'Appended           : {do_appended}')
    logger.info(f'Significant figures: {sig_figs}')
    logger.info(f'Error threshold    : {err_thresh}')

    if do_appended:
        impl_data_raw = basic.get_results_appended(_experiment_dir)
        output_prefix = basic.prefix_appended
    else:
        impl_data_raw = basic.get_results_raw(_experiment_dir)
        output_prefix = ''

    impl_names = list(impl_data_raw.keys())
    if not impl_names:
        return

    logger.info(f'Implementations: {impl_names}')

    # Ensure output directories exist
    for name in impl_names:
        impl_subdir = os.path.join(_experiment_dir, basic.output_subdir_efect, name)
        if not os.path.isdir(impl_subdir):
            logger.debug(f'Making subdirectory: {impl_subdir}')

            os.makedirs(impl_subdir)

    result = {}

    for name in impl_names:
        logger.info(f'Working: {name}')

        impl_subdir = os.path.join(_experiment_dir, basic.output_subdir_efect, name)
        sdata_output_fp = os.path.join(impl_subdir, output_prefix + basic.efect_report_name)
        esamp_output_fp = os.path.join(impl_subdir, output_prefix + basic.efect_sampling_name)

        # Check whether this step needs executed
        if os.path.isfile(sdata_output_fp) and os.path.isfile(esamp_output_fp):
            logger.info(f'\tResults already exist')
            continue

        # Execute the module
        sdata, err_sampling = efect_report(
            load_results(impl_data_raw[name]),
            sig_figs,
            err_thresh=err_thresh,
            return_sampling=True,
            **kwargs
        )

        logger.info(f'\tOutput EFECT report  : {sdata_output_fp}')
        logger.info(f'\tOutput EFECT sampling: {esamp_output_fp}')

        with open(sdata_output_fp, 'w') as _f:
            json.dump(sdata.to_json(), _f, indent=4)
        pd.Series(err_sampling).to_csv(esamp_output_fp)

        result[name] = sdata_output_fp, esamp_output_fp

    return result
