import argparse
import json
import libssr
import numpy as np
import os
from typing import Optional

from ssr.basic import DEF_EVAL_NUM, DEF_NUM_VAR_PERS, VAR_TIME
from ssr.basic import load_results


def efect_report(results,
                 sig_figs: int,
                 num_steps: int = DEF_EVAL_NUM,
                 num_var_pers: int = DEF_NUM_VAR_PERS,
                 **kwargs):

    results_time = results.pop(VAR_TIME)

    results_names = list(results.keys())
    sample_size, num_sim_steps = results[results_names[0]].shape
    num_names = len(results_names)

    f_kwargs = kwargs.copy()
    f_kwargs['num_steps'] = num_steps
    f_kwargs['num_var_pers'] = num_var_pers

    err_sample = libssr.test_reproducibility(results, **f_kwargs)[0]

    ecf_evals = np.ndarray((num_sim_steps, num_names, num_steps, 2), dtype=float)
    ecf_tval = np.ndarray((num_sim_steps, num_names), dtype=float)

    for i in range(num_sim_steps):
        for j, name in enumerate(results_names):
            sample_i = results[name][:sample_size // 2, j]
            ecf_tval[i, j] = libssr.eval_final(sample_i, num_var_pers)
            ecf_evals[i, j, :, :] = libssr.ecf(sample_i, libssr.get_eval_info_times(num_steps, ecf_tval[i, j]))

    return libssr.EFECTReport.create(
        results_names,
        results_time,
        sample_size // 2,
        ecf_evals,
        ecf_tval,
        num_steps,
        np.average(err_sample),
        np.std(err_sample),
        sig_figs
    )


class ArgParser(argparse.ArgumentParser):

    def __init__(self):

        super().__init__(description='Test for reproducibility')

        self.add_argument('-r', '--results',
                          type=str,
                          required=True,
                          dest='results_fp',
                          help='Absolute path to compiled results data.')

        self.add_argument('-o', '--output',
                          type=str,
                          required=True,
                          dest='output_fp',
                          help='Absolute path to output path')

        self.add_argument('-sf', '--sig-figs',
                          type=int,
                          required=True,
                          dest='sig_figs',
                          help='Number of significant figures of data')

        self.add_argument('-en', '--eval-num',
                          type=int,
                          required=False,
                          default=DEF_EVAL_NUM,
                          dest='num_steps',
                          help='Number of ECF transform variable evaluation steps')

        self.add_argument('-np', '--num-var-pers',
                          type=int,
                          required=False,
                          default=DEF_NUM_VAR_PERS,
                          dest='num_var_pers',
                          help='Number of parameterization periods of the ECF')

        self.add_argument('-is', '--incr-sampling',
                          type=int,
                          required=False,
                          default=None,
                          dest='incr_sampling',
                          help='Number of additional trajectories when increasing sample size')

        self.add_argument('-et', '--err-thresh',
                          type=float,
                          required=False,
                          default=None,
                          dest='err_thresh',
                          help='Convergence criterion')

        self.add_argument('-ms', '--max-sampling',
                          type=float,
                          required=False,
                          default=None,
                          dest='max_sampling',
                          help='Maximum error metric sampling')

        self.add_argument('-nw', '--num-workers',
                          type=int,
                          required=False,
                          default=None,
                          dest='num_workers',
                          help='Number of processors')

        self.parsed_args = self.parse_args()

    @property
    def results_fp(self) -> str:
        return self.parsed_args.results_fp

    @property
    def output_fp(self) -> str:
        return self.parsed_args.output_fp

    @property
    def sig_figs(self) -> int:
        return self.parsed_args.sig_figs

    @property
    def num_steps(self) -> int:
        return self.parsed_args.num_steps

    @property
    def num_var_pers(self) -> int:
        return self.parsed_args.num_var_pers

    @property
    def incr_sampling(self) -> Optional[int]:
        return self.parsed_args.incr_sampling

    @property
    def err_thresh(self) -> Optional[float]:
        return self.parsed_args.err_thresh

    @property
    def max_sampling(self) -> Optional[float]:
        return self.parsed_args.max_sampling

    @property
    def num_workers(self) -> Optional[int]:
        return self.parsed_args.num_workers


if __name__ == '__main__':

    args = ArgParser()

    if not os.path.isfile(args.results_fp):
        raise NotADirectoryError(f'Results not found: {args.results_fp}')
    if not os.path.isdir(os.path.dirname(os.path.abspath(args.output_fp))):
        raise NotADirectoryError(f'No parent directory for output: {args.output_fp}')

    _f_kwargs = dict()
    if args.incr_sampling is not None:
        _f_kwargs['incr_sampling'] = args.incr_sampling
    if args.err_thresh is not None:
        _f_kwargs['err_thresh'] = args.err_thresh
    if args.max_sampling is not None:
        _f_kwargs['max_sampling'] = args.max_sampling
    if args.num_workers is not None:
        _f_kwargs['num_workers'] = args.num_workers

    sdata = efect_report(load_results(args.results_fp),
                         args.sig_figs,
                         args.num_steps,
                         args.num_var_pers,
                         **_f_kwargs)

    with open(args.output_fp, 'w') as f:
        json.dump(sdata.to_json(), f, indent=4)
