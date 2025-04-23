"""
Runs the compare step of the workflow
"""
from itertools import product
import json
import libssr
import logging
import matplotlib as mpl
from matplotlib import pyplot as plt
import numpy as np
import os
import pandas as pd
from typing import Any, Dict, List, Type

from workflow import basic

logger = logging.getLogger(__name__)

for k, v in basic.post_rcparams.items():
    mpl.rcParams[k] = v


def _log_error(msg: str, err_type: Type[BaseException]):
    logger.error(msg)
    raise err_type(msg)


def _compare_reports(_modeler_rep: libssr.EFECTReport,
                     _curator_rep: libssr.EFECTReport,
                     _curator_smp: List[float]):
    err_granular = {name: [] for name in _curator_rep.variable_names}
    for i, name in enumerate(_curator_rep.variable_names):
        for j in range(_curator_rep.simulation_times.shape[0]):
            err_granular[name].append(libssr.ecf_compare(_modeler_rep.ecf_evals[j, i, :, :],
                                                         _curator_rep.ecf_evals[j, i, :, :]))
    err_names = {n: max(v) for n, v in err_granular.items()}
    err_res = max(err_names.values())
    return {
        basic.comparison_key_efect_error: err_res,
        basic.comparison_key_rej_pval: libssr.pval(_curator_smp, err_res),
        basic.comparison_key_named_efect_error: err_names,
        basic.comparison_key_granular_efect_error: err_granular
    }


def _post_summary_name(_data: Dict[str, float],
                       _output_dir: str,
                       _output_fexts: List[str],
                       _dpi: int):

    names = list(_data.keys())
    values = [_data[n] for n in names]
    efect_error = max(values)
    df = pd.DataFrame({'EFECT Error': values}, index=names)

    fig, ax = plt.subplots(1, 1, layout='compressed', figsize=(3, 3))

    df.plot.bar(
        ax=ax,
        color='black'
    )
    ax.legend().set_visible(False)
    ax.set_ylabel('EFECT Error')
    ax.set_ylim(0, 2)
    ax.axhline(y=efect_error, color='black', linestyle='--')
    ax.annotate(f'EFECT Error={efect_error}', xy=(0, efect_error), xytext=(0, efect_error + 0.25),
                arrowprops=dict(facecolor='black', shrink=0.05))

    output_name = 'summary'
    for fext in _output_fexts:
        fig.savefig(os.path.join(_output_dir, output_name + '.' + fext),
                    dpi=_dpi)


def _post_summary_granular(_data: Dict[str, List[float]],
                           _output_dir: str,
                           _output_fexts: List[str],
                           _dpi: int):

    names = _data.keys()

    fig, axs = plt.subplots(len(names), 1,
                            layout='compressed',
                            figsize=(3, 3 * len(names)))

    for n, ax in zip(names, axs):
        values = _data[n]

        ax.plot(list(range(len(values))), values, color='black')
        ax.axhline(max(values), color='black', linestyle='--')

        ax.set_ylim(0, 2)
        ax.set_title(n)
        ax.set_xlabel('Step')
        ax.set_ylabel('EFECT Error')

    output_name = 'granular'
    for fext in _output_fexts:
        fig.savefig(os.path.join(_output_dir, output_name + '.' + fext),
                    dpi=_dpi)


def _post(_experiment_dir: str,
          do_appended=False,
          fig_dpi=basic.post_dpi,
          output_fexts: List[str] = None):
    logger.info(f'Doing compare post: {_experiment_dir}')
    logger.info(f'Appended     : {do_appended}')

    if do_appended:
        target_prefix = basic.prefix_appended
    else:
        target_prefix = ''

    output_dir = os.path.join(_experiment_dir, basic.output_subdir_compare)
    logger.debug(f'Output directory: {output_dir}')

    output_fp = os.path.join(output_dir, target_prefix + basic.comparison_output_name)
    logger.debug(f'Output file: {output_fp}')

    if not os.path.isfile(output_fp):
        logger.debug('No output to process')
        return

    try:
        _output_fexts = basic.check_fexts(output_fexts)
    except Exception as e:
        _output_fexts = []
        _log_error(str(e), type(e))

    with open(output_fp, 'r') as f:
        output_data = json.load(f)

    num_outputs = len(output_data)
    post_dir_root = os.path.join(_experiment_dir, basic.output_subdir_post, basic.output_subdir_compare)
    post_dirs = [os.path.join(post_dir_root, str(i)) for i in range(num_outputs)]
    jobs_to_do = [i for i, d in enumerate(post_dirs) if not os.path.isdir(d) or not os.listdir(d)]

    for job in jobs_to_do:
        output_dir_job = post_dirs[job]

        logger.debug(f'Doing job: {output_dir_job}')

        if not os.path.isdir(output_dir_job):
            os.makedirs(output_dir_job)

        output_data_job = output_data[job]
        _post_summary_name(output_data_job[basic.comparison_key_named_efect_error],
                           output_dir_job,
                           _output_fexts,
                           fig_dpi)
        _post_summary_granular(output_data_job[basic.comparison_key_granular_efect_error],
                               output_dir_job,
                               _output_fexts,
                               fig_dpi)


def do_compare(_experiment_dir: str,
               do_appended=False,
               post_kwargs: Dict[str, Any] = None):
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

    # Do post
    if post_kwargs is None:
        post_kwargs = {}
    _post(_experiment_dir, do_appended=do_appended, **post_kwargs)

    return output_data
