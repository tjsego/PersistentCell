"""
Runs the compare step of the workflow
"""
from itertools import product
import json
import libssr
import logging
import numpy as np
import os
import pandas as pd
from typing import List, Type

from workflow import basic

logger = logging.getLogger(__name__)


def _log_error(msg: str, err_type: Type[BaseException]):
    logger.error(msg)
    raise err_type(msg)


def _compare_reports(_modeler_rep: libssr.EFECTReport,
                     _curator_rep: libssr.EFECTReport,
                     _curator_smp: List[float]):
    err_names = {}
    for i, name in enumerate(_curator_rep.variable_names):
        err = 0.0
        for j in range(_curator_rep.simulation_times.shape[0]):
            err = max(err, libssr.ecf_compare(_modeler_rep.ecf_evals[j, i, :, :], _curator_rep.ecf_evals[j, i, :, :]))
        err_names[name] = err
    err_res = max(err_names.values())
    return {
        basic.comparison_key_named_efect_error: err_names,
        basic.comparison_key_efect_error: err_res,
        basic.comparison_key_rej_pval: libssr.pval(_curator_smp, err_res)
    }


def do_compare(_experiment_dir: str,
               do_appended=False):
    logger.info(f'Doing compare: {_experiment_dir}')
    logger.info(f'Appended     : {do_appended}')

    if do_appended:
        target_prefix = basic.prefix_appended
    else:
        target_prefix = ''
    target_dir = os.path.join(_experiment_dir, basic.output_subdir_efect)

    logger.debug(f'Target directory: {target_dir}')

    # Confirm existence of output directory
    output_dir = os.path.join(_experiment_dir, basic.output_subdir_compare)
    logger.debug(f'Output directory: {output_dir}')

    if not os.path.isdir(output_dir):
        logger.debug(f'Making output directory')
        os.makedirs(output_dir)

    # Confirm existence of output file
    output_fp = os.path.join(output_dir, target_prefix + basic.comparison_output_name)
    logger.debug(f'Output file: {output_fp}')

    if not os.path.isfile(output_fp):
        logger.debug('Creating output file')

        with open(output_fp, 'w') as f:
            json.dump([], f)

    # Get existing output file data
    with open(output_fp, 'r') as f:
        output_data = json.load(f)

    # Find completed jobs
    jobs_completed = []
    logger.info('Completed jobs:')
    for entry in output_data:
        jobs_completed.append((entry[basic.comparison_key_modeler], entry[basic.comparison_key_curator]))

        logger.debug(f'\t{jobs_completed[-1]}')

    # Find pairs of results for comparison
    impl_names = []
    for impl_name in os.listdir(target_dir):
        impl_dir = os.path.join(target_dir, impl_name)
        if os.path.isfile(
                os.path.join(impl_dir, target_prefix + basic.efect_report_name)
        ) and os.path.isfile(
            os.path.join(impl_dir, target_prefix + basic.efect_sampling_name)
        ):
            impl_names.append(impl_name)

    logger.info(f'Implementation names: {impl_names}')

    # Construct candidate jobs
    jobs = []
    logger.info('Candidate jobs:')
    for modeler_impl, curator_impl in product(impl_names, impl_names):
        if modeler_impl == curator_impl:
            continue
        entry = modeler_impl, curator_impl
        if entry not in jobs_completed:
            logger.info(f'\t{entry}')

            jobs.append(entry)

    # Work jobs
    for modeler_impl, curator_impl in jobs:
        logger.info(f'Working: {modeler_impl}, {curator_impl}')

        modeler_rep_fp = os.path.join(target_dir, modeler_impl, target_prefix + basic.efect_report_name)
        curator_rep_fp = os.path.join(target_dir, curator_impl, target_prefix + basic.efect_report_name)
        curator_smp_fp = os.path.join(target_dir, curator_impl, target_prefix + basic.efect_sampling_name)

        with open(modeler_rep_fp, 'r') as f:
            modeler_rep = libssr.EFECTReport.from_json(json.load(f))
        with open(curator_rep_fp, 'r') as f:
            curator_rep = libssr.EFECTReport.from_json(json.load(f))

        if modeler_rep.sample_size != curator_rep.sample_size:
            logger.error(f'Sample sizes are not equal: {modeler_rep.sample_size, curator_rep.sample_size}')
            continue
        elif modeler_rep.simulation_times.shape != curator_rep.simulation_times.shape:
            msg = 'Number of simulation times are not equal: '
            msg += f'{modeler_rep.simulation_times.shape, curator_rep.simulation_times.shape}'
            logger.error(msg)
            continue
        elif np.any(modeler_rep.simulation_times != curator_rep.simulation_times):
            logger.error('Simulation times are not equal')
            continue
        elif modeler_rep.variable_names != curator_rep.variable_names:
            logger.error(f'Variable names are not equal: {modeler_rep.variable_names}, {curator_rep.variable_names}')
            continue

        curator_smp = pd.read_csv(curator_smp_fp, skiprows=1, header=None).iloc[:, 1].to_list()

        res = _compare_reports(modeler_rep, curator_rep, curator_smp)
        res[basic.comparison_key_modeler] = modeler_impl
        res[basic.comparison_key_curator] = curator_impl
        output_data.append(res)

        # Fin
        with open(output_fp, 'w') as f:
            json.dump(output_data, f, indent=4)

    return output_data
