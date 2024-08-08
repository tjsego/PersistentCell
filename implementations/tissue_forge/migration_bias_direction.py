import numpy as np
import tissue_forge as tf
from typing import Any, List, Tuple

from model import from_json_data

x_ini = 10.0


class PType(tf.ParticleTypeSpec):
    dynamics = tf.Overdamped


class Sim:

    data_header = [
        'time',
        'com_1',
        'com_2'
    ]

    def __init__(self,
                 dim: Tuple[float, float],
                 model_label: str,
                 model_args: List[Any],
                 sim_time: float,
                 dt: float,
                 damping: float,
                 output_per: float):
        self.dim = dim
        self.model_label = model_label
        self.model_args = model_args
        self.sim_time = sim_time
        self.dt = dt
        self.damping = damping
        self.output_per = output_per

        self.pid = -1
        self.pdata = []
        self.xcom_prev = None
        self.ycom_prev = None
        self.xcom_adjust = 0
        self.ycom_adjust = 0

    def record_data(self):
        if self.pid < 0:
            raise RuntimeError
        ph = tf.ParticleHandle(self.pid)
        pos = ph.position

        xcom, ycom = pos[0], pos[1]
        dimxy = tf.Universe.dim.xy()
        dimx, dimy = dimxy[0], dimxy[1]
        if self.xcom_prev is not None:
            dx, dy = xcom - self.xcom_prev, ycom - self.ycom_prev
        else:
            dx, dy = 0, 0
        if dx < - dimx // 2:
            self.xcom_adjust += dimx
        elif dx > dimx // 2:
            self.xcom_adjust -= dimx
        if dy < - dimy // 2:
            self.ycom_adjust += dimy
        elif dy > dimy // 2:
            self.ycom_adjust -= dimy
        self.xcom_prev, self.ycom_prev = xcom, ycom

        self.pdata.append((tf.Universe.time, xcom + self.xcom_adjust, ycom + self.ycom_adjust))

    def run(self):
        np.random.seed()
        dim2 = min(self.dim)
        cells2 = 3
        tf.Logger.enableConsoleLogging(tf.Logger.ERROR)
        tf.init(dim=[self.dim[0], self.dim[1], dim2],
                cells=[int(self.dim[0] / dim2 * cells2), int(self.dim[1] / dim2 * cells2), cells2],
                dt=self.dt,
                threads=1,
                windowless=True)
        if tf.system.context_has_current():
            tf.system.context_release()

        ph = PType.get()(position=tf.Universe.center)
        ph.mass = self.damping
        self.pid = ph.id

        from_json_data(self.model_label, *self.model_args)
        tf.event.on_time(period=self.output_per, invoke_method=lambda e: self.record_data())

        tf.step(self.sim_time)

        return np.asarray(self.pdata, dtype=float)
