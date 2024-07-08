from cc3d.CompuCellSetup.CC3DCaller import CC3DSimService
from cc3d.core.PySteppables import SteppableBasePy
import json
import multiprocessing as mp
import os
from typing import Optional, List, Tuple


def ensure_output_dir(_output_dir: str):
    if not os.path.isdir(_output_dir):
        os.makedirs(_output_dir)


def unique_data_dir(_output_dir: str, prev_labels: List[int] = None):
    label = 0
    result = f'sim_{label}'
    if prev_labels is None:
        prev_labels = []
    while os.path.isdir(os.path.join(_output_dir, result)) or label in prev_labels:
        label += 1
        result = f'sim_{label}'
    return os.path.join(_output_dir, result), label


class TrackingSteppable(SteppableBasePy):

    def __init__(self, cell_type_name: str, cell_length_target: int):
        
        super().__init__(frequency=1)

        self.cell_type_name = cell_type_name
        self.cell_length_target = cell_length_target

        self.xcom_prev = None
        self.ycom_prev = None
        self.xcom_adjust = 0
        self.ycom_adjust = 0
        self.cell_pos: List[Tuple[int, float, float]] = []
        self.cell_id: Optional[int] = None

    @property
    def cell(self):
        return self.fetch_cell_by_id(self.cell_id) if self.cell_id is not None else None
    
    def start(self):
        start_pos_x = self.dim.x // 2
        start_pos_y = self.dim.y // 2

        cell = self.new_cell(getattr(self.cell_type, self.cell_type_name))
        self.cell_id = cell.id
        for x in range(start_pos_x - self.cell_length_target // 2, start_pos_x + self.cell_length_target // 2):
            for y in range(start_pos_y - self.cell_length_target // 2, start_pos_y + self.cell_length_target // 2):
                self.cell_field[x, y, 0] = cell

    def step(self, mcs):
        cell = self.fetch_cell_by_id(self.cell_id)

        # Check whether the cell crossed a boundary and handle appropriately
        xcom, ycom = cell.xCOM, cell.yCOM
        if self.xcom_prev is not None:
            dx, dy = xcom - self.xcom_prev, ycom - self.ycom_prev
        else:
            dx, dy = 0, 0
        if dx < - self.dim.x // 2:
            self.xcom_adjust += self.dim.x
        elif dx > self.dim.x // 2:
            self.xcom_adjust -= self.dim.x
        if dy < - self.dim.y // 2:
            self.ycom_adjust += self.dim.y
        elif dy > self.dim.y // 2:
            self.ycom_adjust -= self.dim.y
        self.xcom_prev, self.ycom_prev = xcom, ycom

        # Store data
        self.cell_pos.append((mcs, xcom + self.xcom_adjust, ycom + self.ycom_adjust))

    def output_data(self):
        return self.cell_pos


def create_sim(specs, cell_type_name: str, cell_length_target: int, *args, **kwargs):
    steppable = TrackingSteppable(cell_type_name, cell_length_target)
    cc3d_sim = CC3DSimService(*args, **kwargs)
    cc3d_sim.register_specs(specs)
    cc3d_sim.register_steppable(steppable)
    cc3d_sim.run()
    cc3d_sim.init()
    cc3d_sim.start()
    return cc3d_sim, steppable


def generate_screenshot_data(specs, cell_type_name: str, cell_length_target: int, field_names: List[str] = None):
    cc3d_sim = CC3DSimService()
    cc3d_sim.register_specs(specs)
    cc3d_sim.register_steppable(TrackingSteppable(cell_type_name, cell_length_target))
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


def _simulate(specs,
              cell_type_name: str,
              cell_length_target: int,
              output_dir,
              sim_output_dir,
              output_per,
              max_time,
              sim_label):
    print(f'Simulation {sim_label}: {sim_output_dir}')

    cc3d_sim, steppable = create_sim(specs, cell_type_name, cell_length_target,
                                     output_dir=sim_output_dir, output_frequency=output_per)
    while cc3d_sim.current_step < max_time:
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


def simulate(output_dir: str, 
             num_sims: int, 
             output_per: int, 
             screenshot_name: str, 
             specs,
             cell_type_name: str,
             cell_length_target: int,
             max_time: int,
             field_names: List[str] = None):
    output_data_dir = os.path.join(output_dir, 'data')

    ensure_output_dir(output_data_dir)

    input_args = []
    scheduled_labels = []
    
    for i in range(num_sims):

        sim_output_dir, sim_label = unique_data_dir(output_data_dir, scheduled_labels)
        input_args.append((specs, cell_type_name, cell_length_target, output_dir, sim_output_dir, output_per, max_time, sim_label))
        scheduled_labels.append(sim_label)

    with mp.Pool() as p:
        p.starmap(_simulate, input_args)
    
    if not os.path.isfile(os.path.join(output_dir, screenshot_name)):
        with open(os.path.join(output_dir, screenshot_name), 'w') as f:
            json.dump(generate_screenshot_data(specs, cell_type_name, cell_length_target, field_names=field_names), f, indent=4)
