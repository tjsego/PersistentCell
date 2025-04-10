from simservice.PySimService import PySimService
import migration_bias_direction
from typing import Any, List, Tuple


class PersistentCellService(PySimService):

    def __init__(self,
                 dim: Tuple[float, float],
                 model_label: str,
                 model_args: List[Any],
                 sim_time: float,
                 dt: float,
                 damping: float,
                 output_per: float):
        super().__init__(sim_name='PersistentCell')

        self.dim = dim
        self.model_label = model_label
        self.model_args = model_args
        self.sim_time = sim_time
        self.dt = dt
        self.damping = damping
        self.output_per = output_per

        self.pdata = []

    def _run(self):
        pass

    def _init(self) -> bool:
        return True

    def _start(self) -> True:
        sim = migration_bias_direction.Sim(self.dim,
                                           self.model_label,
                                           self.model_args,
                                           self.sim_time,
                                           self.dt,
                                           self.damping,
                                           self.output_per)
        sim.run()
        self.pdata = sim.pdata
        return True

    def _step(self) -> bool:
        return True

    def _finish(self) -> None:
        pass

    def get_data(self):
        return self.pdata

    def get_data_header(self):
        return migration_bias_direction.Sim.data_header
