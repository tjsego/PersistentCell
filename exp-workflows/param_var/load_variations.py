from argparse import ArgumentParser
import logging
import os
import shutil
import traceback
from typing import Optional, List

from workflow import basic as wf_basic
from param_var import basic

logger = logging.getLogger(__name__)
logger.addHandler(logging.StreamHandler())


def main(target_dir: str,
         prefix: str = None):
    logger.info(target_dir)
    logger.info(prefix)

    test_dp = os.path.join(target_dir, basic.test_dir_name)
    if not os.path.isdir(test_dp):
        raise NotADirectoryError(test_dp)
    generators_dp = os.path.join(target_dir, basic.generators_dir_name)
    if not os.path.isdir(generators_dp):
        raise NotADirectoryError(generators_dp)

    logger.info(test_dp)
    logger.info(generators_dp)

    discovered_variations = [d for d in os.listdir(generators_dp) if os.path.isdir(os.path.join(generators_dp, d))]
    if not discovered_variations:
        return

    logger.info(discovered_variations)

    def _do(_source_fps: List[str], _target_dir: str, _results_name: str):
        logger.info(_target_dir)

        for src_fp in _source_fps:

            tgt_name = _results_name
            if prefix is not None:
                tgt_name = f'{prefix}-{_results_name}'
            tgt_dir = os.path.join(_target_dir, tgt_name)

            logger.info(src_fp)
            logger.info(tgt_dir)

            os.makedirs(tgt_dir, exist_ok=True)
            shutil.copy(src_fp, tgt_dir)

    for d in discovered_variations:
        d_dir = os.path.join(generators_dp, d)

        logger.info(d_dir)

        _do(list(wf_basic.get_results_raw(d_dir).values()),
            os.path.join(test_dp, wf_basic.output_subdir_results_raw),
            d)


class ArgParser(ArgumentParser):

    def __init__(self):

        super().__init__()

        self.add_argument('-d', '--dir',
                          type=str,
                          required=True,
                          dest='target_dir',
                          help='Root directory of experiment')

        self.add_argument('-p', '--prefix',
                          type=str,
                          required=False,
                          default=None,
                          dest='prefix',
                          help='Variation prefix')

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
    def prefix(self) -> Optional[str]:
        return self.parsed_args.prefix

    @property
    def log_level(self) -> Optional[int]:
        return self.parsed_args.log_level

    @property
    def kwargs(self):
        return dict(target_dir=self.target_dir,
                    prefix=self.prefix)


if __name__ == '__main__':
    _ap = ArgParser()
    if _ap.log_level is not None:
        logger.setLevel(_ap.log_level)
    try:
        main(**_ap.kwargs)
    except Exception as e:
        logger.error(traceback.format_exception(e))
        raise e
