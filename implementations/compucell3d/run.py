import argparse
import json
from model import from_json_data
import os
from simulate import simulate

DEF_NUM_SIMS = 1
DEF_SCREENSHOT_NAME = 'screenshot.json'


def run(fp: str):
    with open(fp, 'r') as f:
        config_data = json.load(f)

    model_data: dict = config_data['model']
    cc3d_data: dict = config_data['cc3d']

    num_sims = cc3d_data.get('num_sims', DEF_NUM_SIMS)
    output_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'results', cc3d_data['output_name'])
    output_per = int(cc3d_data['output_per'])
    screenshot_name = cc3d_data.get('screenshot_name', DEF_SCREENSHOT_NAME)
    
    specs, steppable_type = from_json_data(model_data)
    
    simulate(output_dir=output_dir,
             num_sims=num_sims,
             output_per=output_per,
             screenshot_name=screenshot_name,
             specs=specs,
             steppable_type=steppable_type,
             max_steps=int(model_data['max_time']))


class ArgParser(argparse.ArgumentParser):
    
    def __init__(self):
        super().__init__(description='Execute specification with CompuCell3D')

        self.add_argument('-f', '--file',
                          type=str,
                          required=True,
                          dest='spec_path',
                          help='Absolute path to specification with implementation specification for CompuCell3D')

        self.parsed_args = self.parse_args()

    @property
    def spec_path(self):
        return self.parsed_args.spec_path


if __name__ == '__main__':
    run(fp=ArgParser().spec_path)