from typing import Any, Dict, List


input_spec_name = 'input.json'
var_spec_name = 'param-var.json'
test_dir_name = 'test'
generators_dir_name = 'generators'

output_subdir_data = 'data'
output_subdir_figures = 'figures'

key_path = 'path'
key_values = 'values'

key_curator = 'Curator'
key_efect_error = 'EFECT Error'
key_impl = 'Implementation'
key_label = 'Label'
key_modeler = 'Modeler'
key_pval = 'Rejection p-value'
key_value = 'Value'

label_baseline = 'Baseline'
label_control = 'Control'
label_other = 'Other'
label_variant = 'Variant'

summary_raw_name = 'summary_raw.csv'
summary_appended_name = 'summary_appended.csv'
comparison_raw_name = 'comparison_raw.csv'
comparison_appended_name = 'comparison_appended.csv'


def recursive_dict_get(_dict: Dict[str, Any], _path: List[str]):
    try:
        if len(_path) == 0:
            raise RuntimeError
        elif len(_path) == 1:
            return _dict[_path[0]]
        else:
            return recursive_dict_get(_dict[_path[0]], _path[1:])
    except KeyError:
        raise KeyError(f'Invalid parameter path {_path}')


def recursive_dict_set(_dict: Dict[str, Any], _path: List[str], _value):
    if len(_path) == 0:
        raise RuntimeError
    elif len(_path) == 1:
        _dict[_path[0]] = _value
    else:
        recursive_dict_set(_dict[_path[0]], _path[1:], _value)


def comparison_efect_name(exp_label: str):
    return f'comparison_{exp_label}_efect'


def comparison_pvals_name(exp_label: str):
    return f'comparison_{exp_label}_pvals'
