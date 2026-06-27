import argparse
import json
from model import from_json_data, verify_spec
import os
from simulate import simulate, run_through as sim_run_through
from typing import Any, Dict, List, Optional, Tuple

DEF_NUM_SIMS = 1
DEF_SCREENSHOT_NAME = 'screenshot.json'


def run(fp: str,
        output_dir: str = None,
        output_frequency=0,
        do_viz=False):
    with open(fp, 'r') as f:
        config_data = json.load(f)

    model_data: dict = config_data['model']
    # Support 'sim' key, prefer 'cc3d' key
    cc3d_data = {}
    if 'sim' in config_data:
        cc3d_data.update(config_data['sim'])
    if 'cc3d' in config_data:
        cc3d_data.update(config_data['cc3d'])

    num_sims = cc3d_data.get('num_sims', DEF_NUM_SIMS)
    if output_dir is None:
        output_dir = str(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'results', cc3d_data['output_name']))
    output_per = int(cc3d_data['output_per'])
    screenshot_name = cc3d_data.get('screenshot_name', DEF_SCREENSHOT_NAME)
    
    specs, cell_type_name = from_json_data(model_data)

    init_voxels: List[Tuple[int, int]] = [(int(x[0]), int(x[1])) for x in config_data['sim']['init_voxels']]
    
    simulate(output_dir=output_dir,
             num_sims=num_sims,
             output_per=output_per,
             init_voxels=init_voxels,
             model_name=model_data['model'],
             model_args=model_data['model_args'],
             screenshot_name=screenshot_name,
             specs=specs,
             cell_type_name=cell_type_name,
             max_time=int(model_data['max_time']),
             output_frequency=output_frequency,
             do_viz=do_viz)


def run_through(fp: str,
                output_frequency=0):
    with open(fp, 'r') as f:
        config_data = json.load(f)

    model_data: dict = config_data['model']
    # Support 'sim' key, prefer 'cc3d' key
    cc3d_data = {}
    if 'sim' in config_data:
        cc3d_data.update(config_data['sim'])
    if 'cc3d' in config_data:
        cc3d_data.update(config_data['cc3d'])

    specs, cell_type_name = from_json_data(model_data)

    init_voxels: List[Tuple[int, int]] = [(int(x[0]), int(x[1])) for x in config_data['sim']['init_voxels']]

    sim_run_through(init_voxels=init_voxels,
                    model_name=model_data['model'],
                    model_args=model_data['model_args'],
                    specs=specs,
                    cell_type_name=cell_type_name,
                    max_time=int(model_data['max_time']),
                    output_frequency=output_frequency)


class ArgParser(argparse.ArgumentParser):
    
    def __init__(self):
        super().__init__(description='Execute specification with CompuCell3D')

        self.add_argument('-f', '--file',
                          type=str,
                          required=True,
                          dest='spec_path',
                          help='Absolute path to specification with implementation specification for CompuCell3D')

        self.add_argument('-o', '--output',
                          type=str,
                          default=None,
                          dest='output_dir',
                          help='Output directory. Default is "results" next to this file')

        self.add_argument('-dp', '--data-period',
                          type=int,
                          default=0,
                          dest='output_frequency',
                          help='Period between simulation data dumps. Default is no data dumps.')

        self.add_argument('-v', '--viz',
                          action='store_true',
                          dest='do_viz',
                          help='Generate spatial data visualization')

        self.add_argument('-t', '--test',
                          action='store_true',
                          dest='run_through',
                          help='Run once to verify implementation can execute')

        self.parsed_args = self.parse_args()

    @property
    def spec_path(self):
        return self.parsed_args.spec_path

    @property
    def output_dir(self) -> Optional[str]:
        return self.parsed_args.output_dir

    @property
    def output_frequency(self) -> int:
        return self.parsed_args.output_frequency

    @property
    def do_viz(self) -> bool:
        return self.parsed_args.do_viz

    @property
    def run_through(self) -> bool:
        return self.parsed_args.run_through

    @property
    def kwargs(self) -> Dict[str, Any]:
        return dict(
            fp=self.spec_path,
            output_dir=self.output_dir,
            output_frequency=self.output_frequency,
            do_viz=self.do_viz
        )

    @property
    def run_through_kwargs(self) -> Dict[str, Any]:
        return dict(
            fp=self.spec_path,
            output_frequency=self.output_frequency
        )


if __name__ == '__main__':
    _ap = ArgParser()
    if _ap.run_through:
        run_through(**_ap.run_through_kwargs)
    else:
        run(**_ap.kwargs)
