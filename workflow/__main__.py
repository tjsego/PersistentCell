from argparse import ArgumentParser
import logging
from typing import Optional


class ArgParser(ArgumentParser):

    def __init__(self):

        super().__init__()

        self.add_argument('-d', '--dir',
                          type=str,
                          required=True,
                          help='Root directory of experiments',
                          dest='dirpath')

        self.add_argument('-a', '--appended',
                          action='store_true',
                          help='Flag to generate and compare appended data',
                          dest='appended')

        self.add_argument('-ll', '--log-level',
                          type=int,
                          default=None,
                          help='Log level',
                          dest='log_level')

        self.add_argument('-lf', '--log-file',
                          type=str,
                          default=None,
                          help='Log output file',
                          dest='log_file')

        self.add_argument('-nlf', '--new-log-file',
                          action='store_true',
                          help='Flag to output a new log file',
                          dest='new_log_file')

        self.parsed_args = self.parse_args()

    @property
    def dirpath(self) -> str:
        return self.parsed_args.dirpath

    @property
    def appended(self) -> bool:
        return self.parsed_args.appended

    @property
    def log_level(self) -> Optional[int]:
        return self.parsed_args.log_level

    @property
    def log_file(self) -> Optional[str]:
        return self.parsed_args.log_file

    @property
    def new_log_file(self) -> bool:
        return self.parsed_args.new_log_file


_ap = None
if __name__ == '__main__':
    _ap = ArgParser()
    _h = None
    if _ap.log_file:
        _h = logging.FileHandler(filename=_ap.log_file,
                                 mode='w' if _ap.new_log_file else 'a')
        _h.setFormatter(
            logging.Formatter(fmt='{asctime} ; {name} ; {levelname} - {module} ; {lineno} ; {funcName} - {message}',
                              style='{')
        )
    for _lc in [
        'workflow', 'workflow.run_compare', 'workflow.run_derived', 'workflow.run_ssr', 'workflow.run_workflow',
        '__main__'
    ]:
        _l = logging.getLogger(_lc)
        if _ap.log_level is not None:
            _l.setLevel(_ap.log_level)
        if _ap.log_file is not None:
            _l.addHandler(_h)


from workflow.run_workflow import main


if __name__ == '__main__':

    main(_ap.dirpath, appended=_ap.appended)
