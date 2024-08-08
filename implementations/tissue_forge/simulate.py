import json
import os
from simservice import close_service
from threading import Thread, Lock
from typing import Any, List, Tuple

from PersistentCellFactory import persistent_cell_simservice


def ensure_output_dir(_output_dir: str):
    if not os.path.isdir(_output_dir):
        os.makedirs(_output_dir)


startup_lock = Lock()


def _simulate(output_dir: str,
              output_per: float,
              dim: Tuple[float, float],
              sim_time: float,
              dt: float,
              model_label: str,
              model_args: List[Any],
              damping: float,
              sim_label: int):
    print(f'Simulation {sim_label}')

    startup_lock.acquire()
    tf_sim = persistent_cell_simservice(dim, model_label, model_args, sim_time, dt, damping, output_per)
    startup_lock.release()
    tf_sim.run()
    tf_sim.init()
    tf_sim.start()
    sim_data = tf_sim.get_data()

    data_formatted = {k: [sd[i] for sd in sim_data] for i, k in enumerate(tf_sim.get_data_header())}

    with open(os.path.join(output_dir, f'sim_{sim_label}.json'), 'w') as f:
        json.dump(data_formatted, f, indent=4)

    close_service(tf_sim)


class SimThread(Thread):

    def __init__(self, args):
        super().__init__()
        self.args = args
        self.done = False

    def run(self):
        _simulate(*self.args)
        self.done = True


def simulate(output_dir: str,
             num_sims: int,
             output_per: float,
             dim: Tuple[float, float],
             sim_time: float,
             dt: float,
             model_label: str,
             model_args: List[Any],  # Assumes only one possible model
             damping: float):

    ensure_output_dir(output_dir)

    input_args = []
    for i in range(num_sims):
        input_args.append((output_dir, output_per, dim, sim_time, dt, model_label, model_args, damping, i))

    num_threads = os.cpu_count()
    threads = [SimThread(ia) for ia in input_args]
    active_threads = [threads.pop(0) for _ in range(min(num_threads, num_sims))]
    [t.start() for t in active_threads]
    while active_threads:
        for i in reversed(range(len(active_threads))):
            t = active_threads[i]
            if t.done:
                active_threads.pop(i)
                if threads:
                    active_threads.append(threads.pop(0))
                    active_threads[-1].start()
