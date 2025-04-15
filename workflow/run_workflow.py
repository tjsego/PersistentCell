"""
Runs the workflow
"""
# todo: add support for appended data

import logging
import os
from typing import Type

from workflow import run_compare, run_derived, run_ssr

logger = logging.getLogger(__name__)


def _log_error(msg: str, err_type: Type[BaseException]):
    logger.error(msg)
    raise err_type(msg)


def main(_exp_dir: str,
         appended=False):
    logger.info('*****************')
    logger.info('Running workflow')
    logger.info(f'\tExperiment directory: {_exp_dir}')
    logger.info(f'\tAppended            : {appended}')
    logger.info('*****************')

    if appended:
        _log_error('Appended results are currently not supported.', ValueError)

    # Ensure experiment directory exists
    if not os.path.isdir(_exp_dir):
        _log_error(_exp_dir, NotADirectoryError)

    # Ensure an input.json exists
    ip = os.path.join(_exp_dir, 'input.json')
    if not os.path.isfile(ip):
        _log_error(ip, FileNotFoundError)

    # run derived step
    logger.info('Running derived step')
    run_derived.do_derived(_exp_dir)

    # run ssr step
    logger.info('Running ssr step')
    run_ssr.do_ssr(_exp_dir, do_appended=appended)

    # run compare step
    logger.info('Running compare step')
    run_compare.do_compare(_exp_dir, do_appended=appended)
