import os
from typing import List

dir_here = os.path.dirname(os.path.abspath(__file__))
dir_root = os.path.dirname(dir_here)
dir_analyses = os.path.join(dir_root, 'analyses')
dir_compare = os.path.join(dir_analyses, 'comparison')
dir_derived = os.path.join(dir_analyses, 'derived')

output_subdir_compare = 'compare'
output_subdir_derived = 'derived'
output_subdir_efect = 'efect'
output_subdir_results_appended = 'results_appended'
output_subdir_results_raw = 'results_raw'
output_subdir_post = 'post'

prefix_appended = 'appended_'

efect_report_name = 'efect_report.json'
efect_sampling_name = 'efect_sampling.csv'

derived_data_basename = 'derived-data'

comparison_output_name = 'comparison.json'

comparison_key_modeler = 'modeler'
comparison_key_curator = 'curator'
comparison_key_efect_error = 'efect_error'
comparison_key_granular_efect_error = 'granular_efect_errors'
comparison_key_named_efect_error = 'named_efect_errors'
comparison_key_rej_pval = 'rejection_p_value'

output_dir_structure = [
    output_subdir_compare,
    output_subdir_derived,
    output_subdir_efect,
    output_subdir_results_appended,
    output_subdir_results_raw
]
output_dir_structure_prereq = [
    output_subdir_results_raw
]

post_dpi = 300
supported_img_fexts = ['png', 'jpg', 'svg']
post_rcparams = {
    'font.family': 'arial'
}

# Workflow specification
workflow_fp = 'workflow.json'
WFKEY_INITSKIP = 'init_skipped'


def start_output_structure(_exp_dir: str):
    for d in output_dir_structure:
        ed = os.path.join(_exp_dir, d)
        if not os.path.isdir(ed):
            os.makedirs(ed)


def get_output_subdirs(_exp_dir):
    return os.listdir(os.path.join(_exp_dir, output_subdir_results_raw))


def get_output_appended_subdirs(_exp_dir):
    return os.listdir(os.path.join(_exp_dir, output_subdir_results_appended))


def get_results_raw(_exp_dir):
    result = {}
    for subdir in get_output_subdirs(_exp_dir):
        csv_data = [f for f in os.listdir(os.path.join(_exp_dir, output_subdir_results_raw, subdir)) if f.endswith('.csv')]
        if not csv_data:
            continue
        # Prefer data is name suffix "-patched", if any
        patched_found = False
        for fn in csv_data:
            if os.path.splitext(fn)[0].endswith('-patched'):
                result[subdir] = os.path.join(_exp_dir, output_subdir_results_raw, subdir, fn)
                patched_found = True
                break
        if not patched_found:
            result[subdir] = os.path.join(_exp_dir, output_subdir_results_raw, subdir, csv_data[0])
    return result


def get_results_appended(_exp_dir):
    result = {}
    for subdir in get_output_appended_subdirs(_exp_dir):
        csv_data = [f for f in os.listdir(os.path.join(_exp_dir, output_subdir_results_appended, subdir)) if f.endswith('.csv')]
        if not csv_data:
            continue
        result[subdir] = os.path.join(_exp_dir, output_subdir_results_appended, subdir, csv_data[0])
    return result


def check_fexts(fexts: List[str] = None):
    if fexts is None:
        fexts = ['png']
    output_fexts = [f for f in fexts]
    for i, v in enumerate(output_fexts):
        if v.startswith('.'):
            output_fexts[i] = v[1:]

    bad_fexts = [f for f in output_fexts if f not in supported_img_fexts]
    if bad_fexts:
        raise ValueError(f'Bad output format(s) requested: {bad_fexts}')

    return output_fexts
