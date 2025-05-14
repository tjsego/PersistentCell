"""
Runs the derived step of the workflow
"""
# todo: add support for appended data
# todo: validate on unix
# todo: forward subprocess streams to logger

import json
import logging
import os
import pandas as pd
import subprocess
import sys
from typing import Tuple, Type

from workflow import basic

logger = logging.getLogger(__name__)

is_win = sys.platform == 'win32'


def _log_error(msg: str, err_type: Type[BaseException]):
    logger.error(msg)
    raise err_type(msg)


def derived_spec_path(_target_dir_abs: str):
    return os.path.join(_target_dir_abs, 'derived.json')


def generate_json(_field_size: Tuple[int, int],
                  _data_fp_abs: str,
                  _target_dir_abs: str):
    output_fp = derived_spec_path(_target_dir_abs)
    if os.path.isfile(output_fp):
        return output_fp

    data = {
      "name": "sample",
      "file": os.path.relpath(_data_fp_abs, _target_dir_abs),
      "fieldSize": [_field_size[0], _field_size[1]],
      "periodicBoundary": True,
      "secondsPerSimulationStep": 1,
      "micronsPerLengthUnit": 1,
      "timeColumn": 1,
      "idColumn": 2,
      "xColumn": 3,
      "yColumn": 4
    }
    with open(output_fp, 'w') as f:
        json.dump({'data': [data]}, f, indent=4)
    return output_fp


def impl_derived_dir(_experiment_dir: str, _impl_name: str):
    return os.path.join(os.path.abspath(_experiment_dir), basic.output_subdir_derived, _impl_name)


def impl_derived_data_fp(_experiment_dir: str, _impl_name: str):
    return os.path.join(_experiment_dir, basic.output_subdir_derived, _impl_name, f'{basic.derived_data_basename}.csv')


def impl_derived_std_data_dir(_experiment_dir: str, _impl_name: str):
    return os.path.join(_experiment_dir, basic.output_subdir_results_appended, _impl_name)


def impl_derived_std_data_fp(_experiment_dir: str, _impl_name: str):
    return os.path.join(impl_derived_std_data_dir(_experiment_dir, _impl_name), f'{basic.derived_data_basename}.csv')


def generate_derived_std(_experiment_dir: str, _impl_name: str):
    target_data_fp = impl_derived_data_fp(_experiment_dir, _impl_name)
    if not os.path.isfile(target_data_fp):
        raise FileNotFoundError(target_data_fp)
    output_data_dir = impl_derived_std_data_dir(_experiment_dir, _impl_name)
    output_data_fp = impl_derived_std_data_fp(_experiment_dir, _impl_name)
    if not os.path.isdir(output_data_dir):
        os.makedirs(output_data_dir)

    target_data = pd.read_csv(target_data_fp)
    target_data.rename(columns={'subtrack.id': 'id'}, inplace=True)
    target_data['id'] += (target_data['track.id'] - 1) * len(target_data['id'].unique()) - 1
    target_data.drop(columns=['track.id', 'dt'], inplace=True)
    target_data['time'] = 0.0
    target_data.to_csv(output_data_fp, index=False, columns=['id', 'time', 'sqDisp', 'acov'])


def exec_script_fp_unix(_experiment_dir: str, _impl_name: str):
    return os.path.join(impl_derived_dir(_experiment_dir, _impl_name), 'derived.sh')


def exec_script_fp_win(_experiment_dir: str, _impl_name: str):
    return os.path.join(impl_derived_dir(_experiment_dir, _impl_name), 'derived.bat')


def exec_script_win(_experiment_dir: str,
                    _impl_name: str):
    script_fp = exec_script_fp_win(_experiment_dir, _impl_name)
    if os.path.isfile(script_fp):
        return script_fp

    edir = impl_derived_dir(_experiment_dir, _impl_name)
    this_dir_rel = os.path.relpath(basic.dir_here, edir)
    derived_dir_rel = os.path.relpath(basic.dir_derived, edir)
    impl_data_rel = os.path.relpath(basic.get_results_raw(_experiment_dir)[_impl_name], edir)
    impl_derived_data_rel = f'{basic.derived_data_basename}.csv'

    script_str = f'''
@echo off

cd {edir}

call {this_dir_rel}/setup/config.bat
call conda activate %PC_CONDAENVNAME_DERIVED%

mkdir data
mkdir plots

Rscript {derived_dir_rel}/scripts/load-and-preprocess-tracks.R derived.json data/comp.rds
Rscript {derived_dir_rel}/scripts/simple-speeds.R data/comp.rds plots/comp.pdf
Rscript {derived_dir_rel}/scripts/msd.R data/comp.rds plots/msd.pdf
Rscript {derived_dir_rel}/scripts/acov.R data/comp.rds 100 plots/acov.pdf
Rscript {derived_dir_rel}/scripts/data-msd-acov.R {impl_data_rel} {impl_derived_data_rel}
'''

    logger.debug(f'Execution script: {script_fp}')
    for line in script_str.splitlines():
        logger.debug('\t' + line)

    with open(script_fp, 'w') as f:
        f.write(script_str)
    return script_fp


def exec_script_unix(_experiment_dir: str,
                     _impl_name: str):
    script_fp = exec_script_fp_unix(_experiment_dir, _impl_name)
    if os.path.isfile(script_fp):
        return script_fp

    edir = impl_derived_dir(_experiment_dir, _impl_name)
    this_dir_rel = os.path.relpath(basic.dir_here, edir)
    derived_dir_rel = os.path.relpath(basic.dir_derived, edir)
    impl_data_rel = os.path.relpath(basic.get_results_raw(_experiment_dir)[_impl_name], edir)
    impl_derived_data_rel = f'{basic.derived_data_basename}.csv'

    script_str = f'''
#!/bin/bash

cd {edir}

source {this_dir_rel}/setup/config.sh
source $PC_CONDAENVSH
conda activate $PC_CONDAENVNAME_DERIVED

mkdir data
mkdir plots

Rscript {derived_dir_rel}/scripts/load-and-preprocess-tracks.R derived.json data/comp.rds
Rscript {derived_dir_rel}/scripts/simple-speeds.R data/comp.rds plots/comp.pdf
Rscript {derived_dir_rel}/scripts/msd.R data/comp.rds plots/msd.pdf
Rscript {derived_dir_rel}/scripts/acov.R data/comp.rds 100 plots/acov.pdf
Rscript {derived_dir_rel}/scripts/data-msd-acov.R {impl_data_rel} {impl_derived_data_rel}
'''

    logger.debug(f'Execution script: {script_fp}')
    for line in script_str.splitlines():
        logger.debug('\t' + line)

    with open(script_fp, 'w') as f:
        f.write(script_str)

    return script_fp


if is_win:
    exec_script = exec_script_win
    exec_script_fp = exec_script_fp_win

else:
    exec_script = exec_script_unix
    exec_script_fp = exec_script_fp_unix


def exec_module(_experiment_dir: str, _impl_name: str):
    return subprocess.Popen([exec_script(_experiment_dir, _impl_name)], cwd=_experiment_dir).wait()


def do_derived(_experiment_dir: str):
    logger.info(f'Doing derived: {_experiment_dir}')

    impl_data_raw = basic.get_results_raw(_experiment_dir)
    impl_names = list(impl_data_raw.keys())

    logger.info(f'Implementation names: {impl_names}')

    if not impl_names:
        return

    # Ensure an input.json is available
    input_fp = os.path.join(_experiment_dir, 'input.json')
    if not os.path.isfile(input_fp):
        _log_error(input_fp, FileNotFoundError)

    logger.debug(f'Input JSON: {input_fp}')

    with open(input_fp, 'r') as f:
        input_data = json.load(f)
    field_size = input_data['model']['len_1'], input_data['model']['len_2']

    logger.debug(f'Field size: {field_size}')

    # Ensure output directories exist
    for name in impl_names:
        impl_subdir = os.path.join(_experiment_dir, basic.output_subdir_derived, name)
        if not os.path.isdir(impl_subdir):
            logger.debug(f'Making subdirectory: {impl_subdir}')

            os.makedirs(impl_subdir)

    result = {}

    for name in impl_names:
        logger.info(f'Doing implementation: {name}')

        impl_subdir = os.path.join(_experiment_dir, basic.output_subdir_derived, name)

        logger.info(f'Subdirectory: {impl_subdir}')

        # Check whether this step needs executed
        if os.path.isfile(os.path.join(impl_subdir, 'data', 'comp.rds')):
            logger.debug('Results already found.')

            continue

        # Check that a JSON exists
        spec_path = derived_spec_path(impl_subdir)
        if not os.path.isfile(spec_path):
            logger.debug(f'Generating spec: {spec_path}')
            logger.debug(f'Targeting data : {impl_data_raw[name]}')

            generate_json(field_size, impl_data_raw[name], impl_subdir)

        # Execute the module
        logger.info('Executing')
        result[name] = exec_module(_experiment_dir, name)

        # Cleanup
        logger.info('Cleaning up')
        if os.path.isfile(spec_path):
            logger.debug(f'Cleaning spec: {spec_path}')

            os.remove(spec_path)

        ex_fp = exec_script_fp(_experiment_dir, name)
        if os.path.isfile(ex_fp):
            logger.debug(f'Cleaning execution script: {ex_fp}')
            os.remove(ex_fp)

    # Generate appended data
    for name in impl_names:
        if not os.path.isfile(impl_derived_std_data_dir(_experiment_dir, name)):
            generate_derived_std(_experiment_dir, name)

    return result
