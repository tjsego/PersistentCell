import csv
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
        reader = csv.DictReader(f)

        track_ids_all = [int(row['id']) for row in reader]
        track_ids = list(set(track_ids_all))
        track_ids.sort()
        min_steps = min([track_ids_all.count(tid) for tid in track_ids])

        data_names = list(reader.fieldnames)
        data_names.remove('time')
        data_names.remove('id')

        result = {k: np.zeros((len(track_ids), min_steps), dtype=float) for k in data_names}

        fdata = {tid: {n: [] for n in data_names + ['time']} for tid in track_ids}
        f.seek(0)
        next(reader)
        for row in reader:
            row: dict
            tid = int(row['id'])
            for name in data_names + ['time']:
                fdata[tid][name].append(float(row[name]))

        for tid, tdata in fdata.items():
            ttimes = {t: i for i, t in enumerate(tdata['time'])}
            ttimes_values = list(ttimes.keys())
            ttimes_values.sort()

            if include_time and tid == track_ids[0]:
                result[VAR_TIME] = np.asarray(ttimes_values[:min_steps], dtype=float)

            tsort_indices = [ttimes[t] for t in ttimes_values]
            for name, values in tdata.items():
                if name == 'time':
                    continue
                tdata[name] = [values[i] for i in tsort_indices]

        for name in data_names:
            for i, tid in enumerate(track_ids):
                result[name][i, :] = fdata[tid][name][:min_steps]

    return result
