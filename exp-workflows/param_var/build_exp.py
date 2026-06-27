from argparse import ArgumentParser
from copy import deepcopy
import json
import logging
import os
import shutil
import traceback
from typing import Optional

from param_var import basic

logger = logging.getLogger(__name__)
logger.addHandler(logging.StreamHandler())


def main(target_dir: str):
    logger.info(target_dir)

    var_spec_fp = os.path.join(target_dir, basic.var_spec_name)
    if not os.path.isfile(var_spec_fp):
        raise FileNotFoundError(var_spec_fp)
    test_dp = os.path.join(target_dir, basic.test_dir_name)
    if not os.path.isdir(test_dp):
        raise NotADirectoryError(test_dp)
    input_spec_fp = os.path.join(test_dp, basic.input_spec_name)
    if not os.path.isfile(input_spec_fp):
        raise FileNotFoundError(input_spec_fp)

    logger.info(var_spec_fp)
    logger.info(test_dp)
    logger.info(input_spec_fp)

    with open(var_spec_fp, 'r') as f:
        var_spec_data = json.load(f)
    if basic.key_path not in var_spec_data:
        raise ValueError(f'Missing parameter path in variation specification')
    if basic.key_values not in var_spec_data:
        raise ValueError(f'Missing parameter variation values in variation specification')

    param_path = var_spec_data[basic.key_path].split(':')
    param_values = var_spec_data[basic.key_values]

    logger.info(param_path)
    logger.info(param_values)

    with open(input_spec_fp, 'r') as f:
        input_spec_data = json.load(f)

    generators_dp = os.path.join(target_dir, basic.generators_dir_name)
    if os.path.isdir(generators_dp):
        shutil.rmtree(generators_dp)
    os.makedirs(generators_dp)

    logger.info(generators_dp)

    for i, v in enumerate(param_values):
        p_dir = os.path.join(generators_dp, f'p{i+1}')

        logger.info(p_dir)

        os.makedirs(p_dir)

        p_input_data = deepcopy(input_spec_data)
        basic.recursive_dict_set(p_input_data['model'], param_path, v)
        with open(os.path.join(p_dir, basic.input_spec_name), 'w') as f:
            json.dump(p_input_data, f, indent=4)


class ArgParser(ArgumentParser):

    def __init__(self):

        super().__init__()

        self.add_argument('-d', '--dir',
                          type=str,
                          required=True,
                          dest='target_dir',
                          help='Root directory of experiment')

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
    def log_level(self) -> Optional[int]:
        return self.parsed_args.log_level

    @property
    def kwargs(self):
        return dict(target_dir=self.target_dir)


if __name__ == '__main__':
    _ap = ArgParser()
    if _ap.log_level is not None:
        logger.setLevel(_ap.log_level)
    try:
        main(**_ap.kwargs)
    except Exception as e:
        logger.error(traceback.format_exception(e))
        raise e
