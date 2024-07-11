import argparse
import json
import libssr
import os

from ssr.basic import load_results


def compare(efect_rep: libssr.EFECTReport, results):

    err_names = {}
    for i, name in enumerate(efect_rep.variable_names):
        if name not in results.keys():
            continue
        err = 0.0
        for j in range(efect_rep.simulation_times.shape[0]):
            ecf_rep = efect_rep.ecf_evals[j, i, :, :]
            ecf_res = libssr.ecf(results[name][:, j],
                                 libssr.get_eval_info_times(efect_rep.ecf_nval, efect_rep.ecf_tval[j, i]))
            err = max(err, libssr.ecf_compare(ecf_rep, ecf_res))
        err_names[name] = err

    err_res = max(err_names.values())
    pval = libssr.pvals(efect_rep.error_metric_mean, efect_rep.error_metric_stdev, err_res, efect_rep.sample_size)

    return {
        'err_names': err_names,
        'err_max': err_res,
        'pval': pval
    }


class ArgParser(argparse.ArgumentParser):

    def __init__(self):

        super().__init__(description='Compare results to a reproducibility report')

        self.add_argument('-e', '--efect-report',
                          type=str,
                          required=True,
                          dest='efect_rep_fp',
                          help='Absolute path to EFECT report')

        self.add_argument('-r', '--results',
                          type=str,
                          required=True,
                          dest='results_fp',
                          help='Absolute path to compiled results data.')

        self.add_argument('-o', '--output',
                          type=str,
                          required=True,
                          dest='output_fp',
                          help='Absolute path to output')

        self.parsed_args = self.parse_args()

    @property
    def efect_rep_fp(self) -> str:
        return self.parsed_args.efect_rep_fp

    @property
    def results_fp(self) -> str:
        return self.parsed_args.results_fp

    @property
    def output_fp(self) -> str:
        return self.parsed_args.output_fp


if __name__ == '__main__':

    args = ArgParser()

    if not os.path.isfile(args.efect_rep_fp):
        raise NotADirectoryError(f'EFECT Report not found: {args.efect_rep_fp}')
    if not os.path.isfile(args.results_fp):
        raise NotADirectoryError(f'Results not found: {args.results_fp}')
    if not os.path.isdir(os.path.dirname(os.path.abspath(args.output_fp))):
        raise NotADirectoryError(f'No parent directory for output: {args.output_fp}')

    with open(args.efect_rep_fp, 'r') as f:
        efect_rep = libssr.EFECTReport.from_json(json.load(f))

    output_data = compare(efect_rep, load_results(args.results_fp, False))

    with open(args.output_fp, 'w') as f:
        json.dump(output_data, f, indent=4)
