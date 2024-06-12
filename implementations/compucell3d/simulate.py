from cc3d.CompuCellSetup.CC3DCaller import CC3DSimService
from cc3d.core.PySteppables import SteppableBasePy
import json
import os
from typing import Optional, List, Tuple, Type


def ensure_output_dir(_output_dir: str):
    if not os.path.isdir(_output_dir):
        os.makedirs(_output_dir)


def unique_data_dir(_output_dir: str):
    label = 0
    result = f'sim_{label}'
    while os.path.isdir(os.path.join(_output_dir, result)):
        label += 1
        result = f'sim_{label}'
    return os.path.join(_output_dir, result), label


class TrackingSteppable(SteppableBasePy):

    def __init__(self, *args, **kwargs):
        
        super().__init__(frequency=1)

        self.cell_pos: List[Tuple[int, int]] = []
        self.cell_id: Optional[int] = None
        self._is_done = False

    @property
    def cell(self):
        return self.fetch_cell_by_id(self.cell_id) if self.cell_id is not None else None

    @classmethod
    def cell_type_name(cls) -> str:
        raise NotImplemented

    @classmethod
    def cell_length_target(cls) -> int:
        raise NotImplemented

    @classmethod
    def buffer(cls) -> int:
        raise NotImplemented
    
    def start(self):
        start_pos_x = self.dim.x // 2
        start_pos_y = self.dim.y // 2

        cell = self.new_cell(getattr(self.cell_type, self.cell_type_name()))
        self.cell_id = cell.id
        cell_length_target = self.cell_length_target()
        for x in range(start_pos_x - cell_length_target // 2, start_pos_x + cell_length_target // 2):
            for y in range(start_pos_y - cell_length_target // 2, start_pos_y + cell_length_target // 2):
                self.cell_field[x, y, 0] = cell

    def step(self, mcs):
        cell = self.fetch_cell_by_id(self.cell_id)
        self.cell_pos.append((mcs, cell.xCOM, cell.yCOM))
        
        buffer = self.buffer()
        if not buffer < cell.xCOM < self.dim.x - buffer or not buffer < cell.yCOM < self.dim.y - buffer:
            self._is_done = True

    def output_data(self):
        return self.cell_pos

    def is_done(self):
        return self._is_done


def create_sim(specs, steppable_type: Type[TrackingSteppable], *args, **kwargs):
    steppable = steppable_type()
    cc3d_sim = CC3DSimService(*args, **kwargs)
    cc3d_sim.register_specs(specs)
    cc3d_sim.register_steppable(steppable)
    cc3d_sim.run()
    cc3d_sim.init()
    cc3d_sim.start()
    return cc3d_sim, steppable


def generate_screenshot_data(specs, steppable_type: Type[TrackingSteppable], field_names: List[str] = None):
    cc3d_sim = CC3DSimService()
    cc3d_sim.register_specs(specs)
    cc3d_sim.register_steppable(steppable_type)
    cc3d_sim.run()
    cc3d_sim.init()
    cc3d_sim.start()
    
    frame_cells = cc3d_sim.visualize()
    field_frames = []
    field_frames_data = {}
    if field_names is None:
        field_names = []
    for name in field_names:
        frame_field = cc3d_sim.visualize()
        frame_field.set_field_name(name)
        frame_field.draw(blocking=True)
        field_frames.append(frame_field)
        field_frames_data[name] = frame_field.get_screenshot_data()
    
    result = dict(cells=frame_cells.get_screenshot_data(), fields=field_frames_data)
    
    cc3d_sim.close_frames()
    field_frames.clear()
    
    return result


def simulate(output_dir: str, 
             num_sims: int, 
             output_per: int, 
             screenshot_name: str, 
             specs, 
             steppable_type: Type[TrackingSteppable], 
             field_names: List[str] = None,
             max_steps: int = None):
    output_data_dir = os.path.join(output_dir, 'data')

    ensure_output_dir(output_data_dir)
    
    for i in range(num_sims):
        print(f'Simulation {i+1} for {num_sims}...')
        
        sim_output_dir, sim_label = unique_data_dir(output_data_dir)
        cc3d_sim, steppable = create_sim(specs, steppable_type, 
                                         output_dir=sim_output_dir, output_frequency=output_per)
        while not steppable.is_done() and (max_steps is None or cc3d_sim.current_step < max_steps):
            cc3d_sim.step()

        sim_data = steppable.output_data()
        with open(os.path.join(output_dir, f'sim_{sim_label}.json'), 'w') as f:
            json.dump(
                dict(
                        time=[sd[0] for sd in sim_data],
                        com_1=[sd[1] for sd in sim_data],
                        com_2=[sd[2] for sd in sim_data]
                    ),
                f,
                indent=4
            )
    
    if not os.path.isdir(os.path.join(output_dir, screenshot_name)):
        with open(os.path.join(output_dir, screenshot_name), 'w') as f:
            json.dump(generate_screenshot_data(specs, steppable_type, field_names=field_names), f, indent=4)
