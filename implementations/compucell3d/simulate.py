from cc3d.CompuCellSetup.CC3DCaller import CC3DSimService
from cc3d.core.PySteppables import SteppableBasePy
import json
import multiprocessing as mp
import os
import traceback
from typing import Any, Dict, List, Optional, Tuple, Type


_cdata_lock = mp.Lock()


def get_constants_data():
    with _cdata_lock:
        with open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'constants.json'), 'r') as f:
            return json.load(f)


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


Result = Tuple[int, float, float, float, float]


class TrackingSteppable(SteppableBasePy):

    def __init__(self,
                 cell_type_name: str,
                 init_voxels: List[Tuple[int, int]],
                 output_per: int,
                 model_name: str,
                 model_args: Dict[str, Any] = None):
        
        super().__init__(frequency=1)

        self.cell_type_name = cell_type_name
        self.init_voxels = init_voxels
        self.output_per = output_per
        self.model_name = model_name
        self.model_args = model_args if model_args is not None else {}

        self.xcom_prev = None
        self.ycom_prev = None
        self.xcom_adjust = 0
        self.ycom_adjust = 0
        self.data: List[Result] = []
        self.cell_id: Optional[int] = None

        self.model = get_implementation(model_name)(self)

    @property
    def cell(self):
        return self.fetch_cell_by_id(self.cell_id) if self.cell_id is not None else None

    @property
    def cell_com(self) -> Tuple[int, int]:
        return self.xcom_prev + self.xcom_adjust, self.ycom_prev + self.ycom_adjust

    def start(self):
        cell = self.new_cell(getattr(self.cell_type, self.cell_type_name))
        self.cell_id = cell.id
        for x, y in self.init_voxels:
            self.cell_field[x, y, 0] = cell

        # Mitigating a rare, strange bug
        if cell.volume == 0:
            msg = 'Found zero volume cell'
            msg += f' ({self.cell_id, self.dim.x, self.dim.y, cell.xCOM, cell.yCOM})'
            raise RuntimeError(msg)

        self.xcom_prev = cell.xCOM
        self.ycom_prev = cell.yCOM

        self.model.start(self)

        if self.output_per > 0:
            self.data.append((0, cell.xCOM, cell.yCOM, cell.volume, cell.surface))

    def step(self, mcs):
        cell = self.fetch_cell_by_id(self.cell_id)

        # Prohibit destroying a cell
        if cell.volume == 0:
            raise RuntimeError(f'Found zero volume cell ({mcs})')

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

        self.model.step(self, mcs)

        # Store data
        if self.output_per > 0 and divmod(mcs + 1, self.output_per)[1] == 0:
            self.data.append((mcs + 1, xcom + self.xcom_adjust, ycom + self.ycom_adjust, cell.volume, cell.surface))

    def output_data(self):
        return self.data


class ModelSteppableImplementation:

    def __init__(self, _parent: TrackingSteppable):

        pass

    @classmethod
    def model_name(cls) -> str:
        raise NotImplementedError

    def start(self, _parent: TrackingSteppable):

        pass

    def step(self, _parent: TrackingSteppable, mcs):

        pass


__model_implementations__: Dict[str, Type[ModelSteppableImplementation]] = {}


def register_implementation(_cls: Type[ModelSteppableImplementation]):

    __model_implementations__[_cls.model_name()] = _cls

    return _cls


@register_implementation
class Model008SteppableImplementation(ModelSteppableImplementation):

    def __init__(self, _parent: TrackingSteppable):

        super().__init__(_parent)

        self.source_pos = _parent.model_args['chemo_source_position']
        self.source_rate = _parent.model_args['chemo_production_rate_per_mcs']
        self.field_name = get_constants_data()['MODEL008']['field_name']
        self.field_fetcher = _parent.field

    @property
    def chemo_field(self):
        return getattr(self.field_fetcher, self.field_name)

    def step(self, _parent: TrackingSteppable, mcs):
        self.chemo_field[self.source_pos[0], self.source_pos[1], 0] += self.source_rate

    @classmethod
    def model_name(cls) -> str:
        return 'MODEL008'


def get_implementation(_name: str) -> Type[ModelSteppableImplementation]:
    return __model_implementations__.get(_name, ModelSteppableImplementation)


def create_sim(specs, cell_type_name: str, init_voxels: List[Tuple[int, int]], output_per: int, model_name: str, model_args: Dict[str, Any], *args, **kwargs):
    steppable = TrackingSteppable(cell_type_name, init_voxels, output_per, model_name, model_args=model_args)
    cc3d_sim = CC3DSimService(*args, **kwargs)
    cc3d_sim.register_specs(specs)
    cc3d_sim.register_steppable(steppable)
    cc3d_sim.run()
    cc3d_sim.init()
    cc3d_sim.start()
    return cc3d_sim, steppable


def generate_screenshot_data(specs, cell_type_name: str, init_voxels: List[Tuple[int, int]], output_per: int, model_name: str, model_args: Dict[str, Any], field_names: List[str] = None):
    cc3d_sim = CC3DSimService()
    cc3d_sim.register_specs(specs)
    cc3d_sim.register_steppable(TrackingSteppable(cell_type_name, init_voxels, output_per, model_name, model_args=model_args))
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
              init_voxels: List[Tuple[int, int]],
              output_dir,
              sim_output_dir,
              output_per,
              model_name: str,
              model_args: Dict[str, Any],
              max_time,
              sim_label,
              output_frequency: int):
    result = False

    try:
        print(f'Simulation {sim_label}: {sim_output_dir}')

        kwargs = {}
        if output_frequency > 0:
            kwargs['output_dir'] = sim_output_dir
            kwargs['output_frequency'] = output_frequency
        cc3d_sim, steppable = create_sim(specs,
                                         cell_type_name,
                                         init_voxels,
                                         output_per,
                                         model_name,
                                         model_args,
                                         **kwargs)
        while cc3d_sim.current_step < max_time:
            cc3d_sim.step()

        sim_data = steppable.output_data()
        with open(os.path.join(output_dir, f'sim_{sim_label}.json'), 'w') as f:
            json.dump(
                dict(
                    time=[sd[0] for sd in sim_data],
                    com_1=[sd[1] for sd in sim_data],
                    com_2=[sd[2] for sd in sim_data],
                    area=[sd[3] for sd in sim_data],
                    surface=[sd[4] for sd in sim_data]
                ),
                f,
                indent=4
            )

        result = True

    except Exception as e:
        if not os.path.isdir(output_dir):
            os.makedirs(output_dir)
        with open(os.path.join(output_dir, 'error.txt'), 'w') as f:
            f.write('\n'.join(traceback.format_exception(e)))

    return result, output_dir


def simulate(output_dir: str, 
             num_sims: int, 
             output_per: int,
             model_name: str,
             model_args: Dict[str, Any],
             screenshot_name: str, 
             specs,
             cell_type_name: str,
             init_voxels: List[Tuple[int, int]],
             max_time: int,
             field_names: List[str] = None,
             output_frequency=0):
    output_data_dir = os.path.join(output_dir, 'data')

    ensure_output_dir(output_data_dir)

    input_args = []
    scheduled_labels = []
    
    for i in range(num_sims):

        sim_output_dir, sim_label = unique_data_dir(output_data_dir, scheduled_labels)
        input_args.append((specs, cell_type_name, init_voxels, output_dir, sim_output_dir, output_per, model_name, model_args, max_time, sim_label, output_frequency))
        scheduled_labels.append(sim_label)

    # Ensure clean memory space per batch. This is analogous to simservice features but with reduced overhead.
    while input_args:
        num_jobs = min(mp.cpu_count(), len(input_args))
        jobs = [input_args.pop(0) for _ in range(num_jobs)]
        with mp.Pool(num_jobs, maxtasksperchild=1) as p:
            print(f'Launching {num_jobs} jobs ({len(input_args)})')
            for res, res_dir in p.starmap(_simulate, jobs):
                if not res:
                    raise RuntimeError(f'Received error flag during execution for target: {res_dir}')
    
    if not os.path.isfile(os.path.join(output_dir, screenshot_name)):
        with open(os.path.join(output_dir, screenshot_name), 'w') as f:
            json.dump(generate_screenshot_data(specs, cell_type_name, init_voxels, output_per, model_name, model_args, field_names=field_names), f, indent=4)


def run_through(model_name: str,
                model_args: Dict[str, Any],
                specs,
                cell_type_name: str,
                init_voxels: List[Tuple[int, int]],
                max_time: int,
                output_frequency=0):
    try:
        cc3d_sim, steppable = create_sim(specs,
                                         cell_type_name,
                                         init_voxels,
                                         output_frequency,
                                         model_name,
                                         model_args)
        while cc3d_sim.current_step < max_time:
            cc3d_sim.step()

        sim_data = steppable.output_data()
        output_data = dict(
            time=[sd[0] for sd in sim_data],
            com_1=[sd[1] for sd in sim_data],
            com_2=[sd[2] for sd in sim_data],
            area=[sd[3] for sd in sim_data],
            surface=[sd[4] for sd in sim_data]
        )
        return output_data
    except Exception as e:
        print(''.join(traceback.format_exception(e)))
        return None
