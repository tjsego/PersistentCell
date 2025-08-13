"""
Runs the workflow
"""
# todo: add support for appended data

import logging
import matplotlib as mpl
from matplotlib import pyplot as plt
import multiprocessing as mp
import numpy as np
import os
import sys
import traceback
from typing import Dict, List, Type

from workflow import basic, run_compare, run_derived, run_ssr

sys.path.append(basic.dir_compare)

from ssr.basic import load_results, VAR_TIME

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


def _post_raw(_post_dir: str,
              _impl_data_raw: Dict[str, Dict[str, np.ndarray]],
              _output_fexts: List[str],
              _dpi: int):
    impl_names = list(_impl_data_raw.keys())

    if not os.path.isdir(_post_dir):
        os.makedirs(_post_dir)

    input_args = []
    for i, impl_name in enumerate(impl_names):
        input_args.append((_post_dir, impl_name, _impl_data_raw[impl_name], _output_fexts, _dpi))

    if len(input_args) > 0:
        num_workers = min(len(input_args), mp.cpu_count())
        with mp.Pool(num_workers) as p:
            for res in p.starmap(_post_raw_job, input_args):
                if isinstance(res, str):
                    logger.error(res)
                    raise RuntimeError(res)


def _post_raw_job(_post_dir: str, impl_name, _impl_data_raw, _output_fexts, _dpi):
    try:
        # Plot
        var_names: List[str] = list(_impl_data_raw.keys())
        if VAR_TIME in var_names:
            has_time = True
            var_names.remove(VAR_TIME)
        else:
            has_time = False

        fig, axs = plt.subplots(len(var_names), 1,
                                layout='compressed',
                                figsize=(3, 3 * len(var_names)))
        for var_name, ax in zip(var_names, axs):
            data = _impl_data_raw[var_name]

            if has_time:
                xdata = _impl_data_raw[VAR_TIME]
            else:
                xdata = list(range(data.shape[1]))
            ax.plot(np.tile(xdata, [data.shape[0], 1]).T, data.T, alpha=0.1, color='black')

            ax.set_xlabel('Step')
            ax.set_title(var_name)

        # Save
        output_name = 'raw_' + impl_name
        for fext in _output_fexts:
            fig.savefig(os.path.join(_post_dir, output_name + '.' + fext),
                        dpi=_dpi)
        plt.close(fig)

        return 0

    except Exception as e:
        return '\n'.join(traceback.format_exception(e))


def _post_dists(_post_dir: str,
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

    cs = _get_colors(len(impl_names))
    dist_indices = np.asarray(list(range(num_times)), dtype=int)[::(num_times - 1) // (num_dists - 1)].tolist()
    for ind in dist_indices:
        # Plot distributions
        fig, axs = plt.subplots(len(var_names), 1,
                                layout='compressed',
                                figsize=(3, 3 * len(var_names)))
        for var_name, ax in zip(var_names, axs):
            for i, impl_name in enumerate(impl_names):
                try:
                    data = _impl_data_raw[impl_name][var_name][:, ind]
                except (IndexError, KeyError):
                    logger.error(f'Missing variable {var_name} for implementation {impl_name}')
                    continue

                ax.hist(data, density=True, alpha=0.25, color=cs[i % len(cs)], label=impl_name)

            ax.set_xlabel(f'Step {ind}')
            ax.set_title(var_name)
            ax.legend()

        # Save
        output_name = f'dist_{ind}'
        for fext in _output_fexts:
            fig.savefig(os.path.join(_post_dir, output_name + '.' + fext),
                        dpi=_dpi)
        plt.close(fig)


def _post_summary(_post_dir: str,
                  _impl_data_raw: Dict[str, Dict[str, np.ndarray]],
                  _output_fexts: List[str],
                  _dpi: int,
                  ci_int: float = 0.95,
                  num_stdevs: int = None):
    impl_names = list(_impl_data_raw.keys())
    var_names: List[str] = list(_impl_data_raw[impl_names[0]].keys())
    if VAR_TIME in var_names:
        has_time = True
        var_names.remove(VAR_TIME)
    else:
        has_time = False

    fig, axs = plt.subplots(len(var_names), 1,
                            layout='compressed',
                            figsize=(3, 3 * len(var_names)))
    cs = _get_colors(len(impl_names))
    # Plot medians
    for var_name, ax in zip(var_names, axs):
        for i, impl_name in enumerate(impl_names):
            try:
                data = _impl_data_raw[impl_name][var_name]
            except KeyError:
                logger.error(f'Missing variable {var_name} for implementation {impl_name}')
                continue

            if has_time:
                xdata = _impl_data_raw[impl_name][VAR_TIME]
            else:
                xdata = list(range(data.shape[1]))
            ax.plot(xdata, np.median(data, axis=0), color=cs[i % len(cs)], label=impl_name)

        ax.set_xlabel('Step')
        ax.set_title(var_name)

    # Shade
    if num_stdevs is not None:
        def _shader(_vals: np.ndarray):
            m = np.median(_vals, axis=0)
            s = np.std(_vals, axis=0) * num_stdevs
            return m - s, m + s
    else:
        ci_inc = (1.0 - ci_int) / 2

        def _shader(_vals: np.ndarray):
            return np.quantile(_vals, [ci_inc, 1.0 - ci_inc], axis=0)

    for var_name, ax in zip(var_names, axs):
        for i, impl_name in enumerate(impl_names):
            try:
                data = _impl_data_raw[impl_name][var_name]
            except KeyError:
                logger.error(f'Missing variable {var_name} for implementation {impl_name}')
                continue

            if has_time:
                xdata = _impl_data_raw[impl_name][VAR_TIME]
            else:
                xdata = list(range(data.shape[1]))
            ax.fill_between(xdata,
                            *_shader(data),
                            alpha=0.25,
                            color=cs[i % len(cs)])

    # Save
    if not os.path.isdir(_post_dir):
        os.makedirs(_post_dir)

    output_name = 'summary_no_legend'
    for fext in _output_fexts:
        fig.savefig(os.path.join(_post_dir, output_name + '.' + fext),
                    dpi=_dpi)

    handles, labels = axs[0].get_legend_handles_labels()
    axs[0].legend(handles[:len(impl_names)], labels[:len(impl_names)])

    output_name = 'summary'
    for fext in _output_fexts:
        fig.savefig(os.path.join(_post_dir, output_name + '.' + fext),
                    dpi=_dpi)
    plt.close(fig)


def _post(_experiment_dir: str,
          do_appended=False,
          output_fexts: List[str] = None,
          dpi: int = basic.post_dpi,
          ci_int: float = 0.95,
          num_stdevs: int = None):
    logger.info(f'Doing starting post: {_experiment_dir}')

    if do_appended:
        results_dir = os.path.join(_experiment_dir, basic.output_subdir_results_appended)
        post_dir = os.path.join(_experiment_dir, basic.output_subdir_post, basic.output_subdir_results_appended)
        get_results = basic.get_results_appended
    else:
        results_dir = os.path.join(_experiment_dir, basic.output_subdir_results_raw)
        post_dir = os.path.join(_experiment_dir, basic.output_subdir_post, basic.output_subdir_results_raw)
        get_results = basic.get_results_raw

    try:
        _output_fexts = basic.check_fexts(output_fexts)
    except Exception as e:
        _output_fexts = []
        _log_error(str(e), type(e))

    impl_data: Dict[str, Dict[str, np.ndarray]] = {n: load_results(fp)
                                                   for n, fp in get_results(_experiment_dir).items()}
    if not os.path.isdir(results_dir) or not impl_data:
        logger.debug('No results found')
        return

    if not os.path.isdir(post_dir):
        os.makedirs(post_dir)

    _post_raw(post_dir, impl_data, _output_fexts, dpi)
    _post_summary(post_dir, impl_data, _output_fexts, dpi,
                  ci_int=ci_int,
                  num_stdevs=num_stdevs)
    _post_dists(post_dir, impl_data, _output_fexts, dpi)


def main(_exp_dir: str,
         appended=False):
    logger.info('*****************')
    logger.info('Running workflow')
    logger.info(f'\tExperiment directory: {_exp_dir}')
    logger.info(f'\tAppended            : {appended}')
    logger.info('*****************')

    # Ensure experiment directory exists
    if not os.path.isdir(_exp_dir):
        _log_error(_exp_dir, NotADirectoryError)

    # Ensure an input.json exists
    ip = os.path.join(_exp_dir, 'input.json')
    if not os.path.isfile(ip):
        _log_error(ip, FileNotFoundError)

    # todo: add support for rendering options
    _post(_exp_dir, do_appended=appended)

    # run derived step
    logger.info('Running derived step')
    run_derived.do_derived(_exp_dir)

    # run ssr step
    logger.info('Running ssr step')
    run_ssr.do_ssr(_exp_dir)
    if appended:
        run_ssr.do_ssr(_exp_dir, do_appended=True)

    # run compare step
    logger.info('Running compare step')
    run_compare.do_compare(_exp_dir)
    if appended:
        run_compare.do_compare(_exp_dir, do_appended=True)
