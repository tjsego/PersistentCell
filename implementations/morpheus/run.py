import argparse
import json

import os
from simulate import simulate

def run(fp: str, plot : bool, output_dir: str = None):
    with open(fp, 'r') as f:
        config_data = json.load(f)

    model_data: dict = config_data['model']
    sim_data: dict = config_data['sim']

    if output_dir is None:
        output_dir = os.path.join(os.getcwd(), sim_data['output_name'])
    
    # transfer all config data to single dataset
    model_data['log_freq'] = sim_data['output_per']
    
    first=True
    morph_voxels=""
    for voxel in sim_data['init_voxels'] :
        if not first :
            morph_voxels += ' ; '
        morph_voxels += '{},{},0'.format(voxel[0],voxel[1])
        first=False
    model_data['init_voxels'] = morph_voxels
    
    simulate(model_data,
             input_dir=os.path.dirname(os.path.abspath(fp)),
             output_dir=output_dir,
             num_sims=int(sim_data['num_sims']),
             plot=plot)


class ArgParser(argparse.ArgumentParser):
    
    def __init__(self):
        super().__init__(description='Execute specification with Morpheus\n (minimum supported version is 2.3.9)')

        self.add_argument('-f', '--file',
                          type=str,
                          required=True,
                          dest='spec_path',
                          help='Absolute path to specification')
        
        self.add_argument('-p', '--plot',
                          required=False,
                          action="store_true",
                          dest='plot',
                          help='Plot DAC and MSD')

        self.parsed_args = self.parse_args()

    @property
    def spec_path(self):
        return self.parsed_args.spec_path
    
    @property
    def plot(self):
        return self.parsed_args.plot


if __name__ == '__main__':
    args = ArgParser()
    run(fp=args.spec_path, plot=args.plot)
