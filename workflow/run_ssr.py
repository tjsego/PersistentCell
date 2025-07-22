"""
Runs the stochastic simulation reproducibility step of the workflow
"""
import json
import libssr
import logging
import matplotlib as mpl
from matplotlib import pyplot as plt
import multiprocessing as mp
import numpy as np
import os
import pandas as pd
import sys
import traceback
from typing import Dict, List, Tuple, Type

from workflow import basic

sys.path.append(basic.dir_compare)

from ssr.basic import load_results, VAR_TIME
from ssr.analyze import efect_report

logger = logging.getLogger(__name__)

for k, v in basic.post_rcparams.items():
    mpl.rcParams[k] = v


def _log_error(msg: str, err_type: Type[BaseException]):
    logger.error(msg)
    raise err_type(msg)


def _get_colors(num_entries: int = None):
    if num_entries is None or num_entries < 10:
        cs = plt.color_sequences['tab10']
    else:
        cs = plt.color_sequences['tab20']
    return cs


def _post_ecfs(_post_dir: str,
               _impl_data_raw: Dict[str, Dict[str, np.ndarray]],
               _output_fexts: List[str],
               _dpi: int,
               num_dists=11):
    impl_names = list(_impl_data_raw.keys())
    var_names: List[str] = list(_impl_data_raw[impl_names[0]].keys())
    num_times = _impl_data_raw[impl_names[0]][var_names[0]].shape[1]
    if VAR_TIME in var_names:
        var_names.remove(VAR_TIME)

    if not os.path.isdir(_post_dir):
        os.makedirs(_post_dir)

    dist_indices = np.asarray(list(range(1, num_times)), dtype=int)[::(num_times - 2) // (num_dists - 1)].tolist()
    input_args = []
    for ind in dist_indices:
        input_args.append((_post_dir, var_names, impl_names, _impl_data_raw, ind, _output_fexts, _dpi))

    if len(input_args) > 0:
        num_workers = min(len(input_args), mp.cpu_count())
        with mp.Pool(num_workers) as p:
            for res in p.starmap(_post_ecfs_job, input_args):
                if isinstance(res, str):
                    logger.error(res)
                    raise RuntimeError(res)


def _post_ecfs_job(_post_dir: str, var_names, impl_names, _impl_data_raw, ind, _output_fexts, _dpi):
    try:
        # Plot ECFs
        cs = _get_colors(len(impl_names))
        fig, axs = plt.subplots(len(var_names), 2,
                                layout='compressed',
                                figsize=(6, 3 * len(var_names)))
        for var_name, ax in zip(var_names, axs):
            eval_t = None

            for i, impl_name in enumerate(impl_names):
                try:
                    data = _impl_data_raw[impl_name][var_name][:, ind]
                except KeyError:
                    logger.error(f'Missing variable {var_name} for implementation {impl_name}')
                    continue

                if i == 0:
                    eval_t = libssr.get_eval_info_times(100, libssr.eval_final(data))
                ecf = libssr.ecf(data, eval_t)
                [ax[j].plot(eval_t, ecf[:, j], color=cs[i % len(cs)], label=impl_name) for j in range(2)]

            for j in range(2):
                ax[j].set_xlabel(f'Step {ind}')
                ax[j].set_title(var_name)
                ax[j].set_ylim(-1, 1)
                ax[j].legend()

        # Save
        output_name = f'ecf_{ind}'
        for fext in _output_fexts:
            fig.savefig(os.path.join(_post_dir, output_name + '.' + fext),
                        dpi=_dpi)
        plt.close(fig)

        return 0

    except Exception as e:
        return '\n'.join(traceback.format_exception(e))


def _post_summary(_post_dir: str,
                  _sampling_data: Dict[str, Tuple[float, float]],
                  _output_fexts: List[str],
                  _dpi: int):
    names = list(_sampling_data.keys())
    values = [_sampling_data[n] for n in names]

    fig, ax = plt.subplots(1, 1, layout='compressed', figsize=(3, 3))

    ax.bar(names, [v[0] for v in values], yerr=[v[1] for v in values], color='black', error_kw={'ecolor': 'gray'})
    ax.set_xticklabels(names, rotation=90, fontsize=10)
    ax.set_ylabel('EFECT Error')
    ax.set_ylim(0, 2)

    output_name = 'summary'
    for fext in _output_fexts:
        fig.savefig(os.path.join(_post_dir, output_name + '.' + fext),
                    dpi=_dpi)
    plt.close(fig)


def _post(_experiment_dir: str,
          do_appended=False,
          fig_dpi=basic.post_dpi,
          output_fexts: List[str] = None):
    logger.info(f'Doing ssr post: {_experiment_dir}')

    if do_appended:
        get_results = basic.get_results_appended
        output_subdir_efect = basic.prefix_appended + basic.output_subdir_efect
    else:
        get_results = basic.get_results_raw
        output_subdir_efect = basic.output_subdir_efect

    try:
        _output_fexts = basic.check_fexts(output_fexts)
    except Exception as e:
        _output_fexts = []
        _log_error(str(e), type(e))

    impl_data: Dict[str, Dict[str, np.ndarray]] = {n: load_results(fp)
                                                   for n, fp in get_results(_experiment_dir).items()}
    efect_reports = {}
    for n in impl_data:
        fp = os.path.join(_experiment_dir, output_subdir_efect, n, basic.efect_report_name)
        if os.path.isfile(fp):
            with open(fp, 'r') as f:
                efect_reports[n] = libssr.EFECTReport.from_json(json.load(f))
    impl_names = list(set(efect_reports.keys()).intersection(impl_data.keys()))
    if not impl_names:
        logger.debug('No results found')
        return

    post_dir = os.path.join(_experiment_dir, basic.output_subdir_post, output_subdir_efect)
    if not os.path.isdir(post_dir):
        os.makedirs(post_dir)

    _post_ecfs(post_dir,
               {n: impl_data[n] for n in impl_names},
               _output_fexts,
               fig_dpi)
    _post_summary(post_dir,
                  {n: (efect_reports[n].error_metric_mean, efect_reports[n].error_metric_stdev) for n in impl_names},
                  _output_fexts,
                  fig_dpi)


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
        impl_data = basic.get_results_appended(_experiment_dir)
        output_subdir_efect = basic.prefix_appended + basic.output_subdir_efect
    else:
        impl_data = basic.get_results_raw(_experiment_dir)
        output_subdir_efect = basic.output_subdir_efect

    impl_names = list(impl_data.keys())
    if not impl_names:
        return

    logger.info(f'Implementations: {impl_names}')

    # Ensure output directories exist
    for name in impl_names:
        impl_subdir = os.path.join(_experiment_dir, output_subdir_efect, name)
        if not os.path.isdir(impl_subdir):
            logger.debug(f'Making subdirectory: {impl_subdir}')

            os.makedirs(impl_subdir)

    result = {}

    for name in impl_names:
        logger.info(f'Working: {name}')

        impl_subdir = os.path.join(_experiment_dir, output_subdir_efect, name)
        sdata_output_fp = os.path.join(impl_subdir, basic.efect_report_name)
        esamp_output_fp = os.path.join(impl_subdir, basic.efect_sampling_name)

        # Check whether this step needs executed
        if os.path.isfile(sdata_output_fp) and os.path.isfile(esamp_output_fp):
            logger.info(f'\tResults already exist')
            continue

        # Execute the module
        sdata, err_sampling = efect_report(
            load_results(impl_data[name]),
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

    # todo: add support for rendering options
    _post(_experiment_dir,
          do_appended=do_appended)

    return result
