import json
from libssr.consts import DEF_EVAL_NUM, DEF_NUM_VAR_PERS
import numpy as np
import os

DEF_RESULTS_KEYS = {
    'com_1': float,
    'com_2': float,
    'time': float
}
VAR_TIME = 'time'


def load_results(fp: str, include_time=True):
    if not os.path.isfile(fp):
        raise FileNotFoundError(fp)

    with open(fp, 'r') as f:
        fdata = json.load(f)

    result = {k: np.asarray(v, dtype=float) for k, v in fdata['results'].items()}
    if include_time:
        result[VAR_TIME] = np.asarray(fdata['times'], dtype=float)
    return result
