from argparse import ArgumentParser
import json
import logging
import matplotlib as mpl
from matplotlib import pyplot as plt
import numpy as np
import os
import pandas as pd
import traceback
from typing import Any, Dict, List, Optional

from workflow import basic as wf_basic
from param_var import basic

logger = logging.getLogger(__name__)
logger.addHandler(logging.StreamHandler())


_data_name_map = {
    wf_basic.comparison_key_modeler: basic.key_modeler,
    wf_basic.comparison_key_curator: basic.key_curator,
    wf_basic.comparison_key_efect_error: basic.key_efect_error,
    wf_basic.comparison_key_rej_pval: basic.key_pval
}

for k, v in wf_basic.post_rcparams.items():
    mpl.rcParams[k] = v


def _get_variation_info(_target_dir: str):
    fp = os.path.join(_target_dir, basic.var_spec_name)
    if not os.path.isfile(fp):
        raise FileNotFoundError(fp)
    with open(fp, 'r') as f:
        fdata = json.load(f)
    return fdata[basic.key_path], fdata[basic.key_values]


def _get_colors(num_entries: int = None):
    if num_entries is None or num_entries < 10:
        cs = plt.color_sequences['tab10']
    else:
        cs = plt.color_sequences['tab20']
    return cs


def _extract_parameter_value(_fp: str, _path: List[str]):
    if not os.path.isfile(_fp):
        raise FileNotFoundError(_fp)
    with open(_fp, 'r') as f:
        data = json.load(f)['model']
    return basic.recursive_dict_get(data, _path)


def _parse_comparison_data(_fp: str):
    if not os.path.isfile(_fp):
        raise FileNotFoundError(_fp)
    with open(_fp, 'r') as f:
        cdata = json.load(f)
    result = {v: [] for v in _data_name_map.values()}
    for cd in cdata:
        for k, v in _data_name_map.items():
            result[v].append(cd[k])
    return result


def _parse_comparison_implementations(_comparison_data, _control: str, _variant_names: List[str]):
    result = {
        basic.key_impl: [],
        basic.key_label: []
    }
    suffixes = [f'-{n}' for n in _variant_names]
    implementation_names = list(set(_comparison_data[basic.key_modeler] + _comparison_data[basic.key_curator]))
    implementation_names.sort()
    for n in implementation_names:
        result[basic.key_impl].append(n)
        if n == _control:
            result[basic.key_label].append(basic.label_control)
        elif any([n.endswith(s) for s in suffixes]):
            result[basic.key_label].append(basic.label_variant)
        else:
            result[basic.key_label].append(basic.label_other)
    return result


def _subdir_generators(_target_dir: str):
    result = os.path.join(_target_dir, basic.generators_dir_name)
    if not os.path.isdir(result):
        raise NotADirectoryError(result)
    return result


def _subdir_test(_target_dir: str):
    result = os.path.join(_target_dir, basic.test_dir_name)
    if not os.path.isdir(result):
        raise NotADirectoryError(result)
    return result


def _get_variant_names(_target_dir: str):
    generators_dir = _subdir_generators(_target_dir)
    return [d for d in os.listdir(generators_dir) if os.path.isdir(os.path.join(generators_dir, d))]


def _get_variant_output_name_map(_variant_names: List[str],
                                 _comparison_data: Dict[str, List[Any]],
                                 invert=False):
    suffixes = {n: f'-{n}' for n in _variant_names}
    names_all = set(_comparison_data[basic.key_modeler] + _comparison_data[basic.key_curator])
    result = dict()
    for n in names_all:
        for k, v in suffixes.items():
            if n.endswith(v):
                if invert:
                    result[n] = k
                else:
                    result[k] = n
    return result


def _find_input_variant_value(_target_dir: str, _param_path: List[str]) -> Dict[str, float]:
    result = {basic.label_baseline: _extract_parameter_value(os.path.join(_subdir_test(_target_dir),
                                                                          basic.input_spec_name),
                                                             _param_path)}
    for n in _get_variant_names(_target_dir):
        result[n] = _extract_parameter_value(os.path.join(_subdir_generators(_target_dir), n, basic.input_spec_name),
                                             _param_path)
    return result


def _validate_target(_target_dir: str):
    _subdir_generators(_target_dir)
    _subdir_test(_target_dir)


def _summary_output_raw_fp(_target_dir: str):
    return os.path.join(
        _target_dir, wf_basic.output_subdir_post, basic.output_subdir_data, basic.summary_raw_name
    )


def _summary_output_appended_fp(_target_dir: str):
    return os.path.join(
        _target_dir, wf_basic.output_subdir_post, basic.output_subdir_data, basic.summary_appended_name
    )


def _comparison_output_raw_fp(_target_dir: str):
    return os.path.join(
        _target_dir, wf_basic.output_subdir_post, basic.output_subdir_data, basic.comparison_raw_name
    )


def _comparison_output_appended_fp(_target_dir: str):
    return os.path.join(
        _target_dir, wf_basic.output_subdir_post, basic.output_subdir_data, basic.comparison_appended_name
    )


def _export_data(_target_dir: str, _control_name: str, _param_path: List[str]):
    data_dir = os.path.join(_target_dir, wf_basic.output_subdir_post, basic.output_subdir_data)

    variant_names = _get_variant_names(_target_dir)

    logger.info(data_dir)
    logger.info(variant_names)

    # Export comparison results

    comparison_data_r = _parse_comparison_data(os.path.join(_subdir_test(_target_dir),
                                                            wf_basic.output_subdir_compare,
                                                            wf_basic.comparison_output_name))
    comparison_data_a = _parse_comparison_data(os.path.join(_subdir_test(_target_dir),
                                                            wf_basic.prefix_appended + wf_basic.output_subdir_compare,
                                                            wf_basic.comparison_output_name))

    os.makedirs(data_dir, exist_ok=True)

    pd.DataFrame(comparison_data_r).to_csv(_comparison_output_raw_fp(_target_dir))
    pd.DataFrame(comparison_data_a).to_csv(_comparison_output_appended_fp(_target_dir))

    # Export summary of implementations and values

    summary_impl_r = _parse_comparison_implementations(comparison_data_r, _control_name, variant_names)
    summary_impl_a = _parse_comparison_implementations(comparison_data_a, _control_name, variant_names)
    input_values = _find_input_variant_value(_target_dir, _param_path)
    variant_name_mapi_r = _get_variant_output_name_map(variant_names, comparison_data_r, invert=True)
    variant_name_mapi_a = _get_variant_output_name_map(variant_names, comparison_data_a, invert=True)
    summary_impl_r[basic.key_value] = []
    summary_impl_a[basic.key_value] = []
    for impl, lab in zip(summary_impl_r[basic.key_impl], summary_impl_r[basic.key_label]):
        logger.info(impl)
        if lab in [basic.label_control, basic.label_other]:
            logger.info(lab)

            summary_impl_r[basic.key_value].append(input_values[basic.label_baseline])
        else:
            logger.info(lab)

            summary_impl_r[basic.key_value].append(input_values[variant_name_mapi_r[impl]])
    for impl, lab in zip(summary_impl_a[basic.key_impl], summary_impl_a[basic.key_label]):
        logger.info(impl)
        if lab in [basic.label_control, basic.label_other]:
            logger.info(lab)

            summary_impl_a[basic.key_value].append(input_values[basic.label_baseline])
        else:
            logger.info(lab)

            summary_impl_a[basic.key_value].append(input_values[variant_name_mapi_a[impl]])

    pd.DataFrame(summary_impl_r).to_csv(_summary_output_raw_fp(_target_dir))
    pd.DataFrame(summary_impl_a).to_csv(_summary_output_appended_fp(_target_dir))


def _export_figure(_target_dir: str,
                   _raw: bool,
                   _dpi: int,
                   _output_fexts: List[str],
                   _normalize: bool,
                   _param_label: str,
                   _sig_level: float):
    figs_dir = os.path.join(_target_dir, wf_basic.output_subdir_post, basic.output_subdir_figures)

    os.makedirs(figs_dir, exist_ok=True)

    logger.info(figs_dir)
    logger.info(_raw)

    if _raw:
        comparison_data = pd.read_csv(_comparison_output_raw_fp(_target_dir), index_col=0)
        summary_impl = pd.read_csv(_summary_output_raw_fp(_target_dir), index_col=0)
        exp_label = 'raw'
    else:
        comparison_data = pd.read_csv(_comparison_output_appended_fp(_target_dir), index_col=0)
        summary_impl = pd.read_csv(_summary_output_appended_fp(_target_dir), index_col=0)
        exp_label = 'appended'

    control_name = summary_impl[summary_impl[basic.key_label] == basic.label_control][
        basic.key_impl].to_numpy().tolist()[0]
    non_variant_names = [control_name] + summary_impl[summary_impl[basic.key_label] == basic.label_other][
        basic.key_impl].to_numpy().tolist()
    values_by_impl = {rec[basic.key_impl]: rec[basic.key_value] for rec in summary_impl.to_dict(orient='records')}

    # something like this:
    data_by_impl_efect = {}
    data_by_impl_pvals = {}
    for name in non_variant_names:
        df = comparison_data[comparison_data[basic.key_curator] == name]
        xy_efect = []
        xy_pvals = []
        for rec in df.to_dict(orient='records'):
            x = values_by_impl[rec[basic.key_modeler]]
            xy_efect.append((x, rec[basic.key_efect_error]))
            xy_pvals.append((x, rec[basic.key_pval]))
        data_by_impl_efect[name] = np.asarray(sorted(xy_efect, key=lambda t: t[0]), dtype=float)
        data_by_impl_pvals[name] = np.asarray(sorted(xy_pvals, key=lambda t: t[0]), dtype=float)

    # Make comparison for each baseline implementation

    fig_kwargs = dict(layout='compressed', figsize=(4, 4))
    fig_efect, ax_efect = plt.subplots(1, 1, **fig_kwargs)
    fig_pvals, ax_pvals = plt.subplots(1, 1, **fig_kwargs)
    cs = _get_colors(len(non_variant_names))

    for i, name in enumerate(non_variant_names):
        label_str = f'*{name}' if name == control_name else name

        logger.info(name)
        logger.info(label_str)

        xy = data_by_impl_efect[name]
        if _normalize:
            xy[:, 0] /= values_by_impl[name]
        ax_efect.plot(xy[:, 0], xy[:, 1], marker='o', color=cs[i % len(cs)], label=label_str)

        xy = data_by_impl_pvals[name]
        if _normalize:
            xy[:, 0] /= values_by_impl[name]
        ax_pvals.plot(xy[:, 0], xy[:, 1], marker='o', color=cs[i % len(cs)], label=label_str)

    if _normalize:
        ax_efect.axvline(1.0, linestyle='--', color='black')
        ax_pvals.axvline(1.0, linestyle='--', color='black')
    else:
        ax_efect.axvline(values_by_impl[control_name], linestyle='--', color='black')
        ax_pvals.axvline(values_by_impl[control_name], linestyle='--', color='black')
    ax_pvals.axhline(_sig_level, linestyle='--', color='black')

    ax_efect.set_ylim(-0.05, 2.05)
    ax_pvals.set_ylim(1E-3, 1.1)
    ax_pvals.set_yscale('log')
    ax_efect.set_ylabel(basic.key_efect_error)
    ax_pvals.set_ylabel(basic.key_pval)
    for ax in [ax_efect, ax_pvals]:
        ax.set_xlabel(_param_label)
        ax.grid(True)
        ax.legend()

    for fext in _output_fexts:
        logger.info(fext)

        fig_efect.savefig(os.path.join(figs_dir, basic.comparison_efect_name(exp_label) + '.' + fext), dpi=_dpi)
        fig_pvals.savefig(os.path.join(figs_dir, basic.comparison_pvals_name(exp_label) + '.' + fext), dpi=_dpi)
    plt.close(fig_efect)
    plt.close(fig_pvals)


def _export_figures(_target_dir: str,
                    _dpi: int,
                    _output_fexts: List[str],
                    _normalize: bool,
                    _param_label: str,
                    _sig_level: float):
    _export_figure(_target_dir, True, _dpi, _output_fexts, _normalize, _param_label, _sig_level)
    _export_figure(_target_dir, False, _dpi, _output_fexts, _normalize, _param_label, _sig_level)


def main(target_dir: str,
         control_name: str,
         normalize: bool,
         output_fexts: List[str] = None,
         dpi=300,
         sig_level=0.05):
    logger.info(target_dir)
    logger.info(control_name)
    logger.info(normalize)
    logger.info(output_fexts)

    test_dp = os.path.join(target_dir, basic.test_dir_name)
    if not os.path.isdir(test_dp):
        raise NotADirectoryError(test_dp)
    if output_fexts is None:
        output_fexts = wf_basic.supported_img_fexts
    param_path = _get_variation_info(target_dir)[0].split(':')

    logger.info(param_path)

    _export_data(target_dir, control_name, param_path)
    _export_figures(target_dir, dpi, output_fexts, normalize, ':'.join(param_path), sig_level)


class ArgParser(ArgumentParser):

    def __init__(self):

        super().__init__()

        self.add_argument('-d', '--dir',
                          type=str,
                          required=True,
                          dest='target_dir',
                          help='Root directory of experiment')

        self.add_argument('-c', '--control',
                          type=str,
                          required=True,
                          dest='control_name',
                          help='Name of control implementation')

        self.add_argument('-n', '--normalize',
                          action='store_true',
                          dest='normalize',
                          help='Normalize parameters by control value in figures')

        self.add_argument('-ll', '--log-level',
                          type=int,
                          default=None,
                          help='Log level',
                          dest='log_level')

        self.parsed_args = self.parse_args()

    @property
    def target_dir(self) -> str:
        return self.parsed_args.target_dir

    @property
    def control_name(self) -> str:
        return self.parsed_args.control_name

    @property
    def normalize(self) -> bool:
        return self.parsed_args.normalize

    @property
    def log_level(self) -> Optional[int]:
        return self.parsed_args.log_level

    @property
    def kwargs(self):
        return dict(target_dir=self.target_dir,
                    control_name=self.control_name,
                    normalize=self.normalize)


if __name__ == '__main__':
    _ap = ArgParser()
    if _ap.log_level is not None:
        logger.setLevel(_ap.log_level)
    try:
        main(**_ap.kwargs)
    except Exception as e:
        logger.error(traceback.format_exception(e))
        raise e
