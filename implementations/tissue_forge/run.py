import argparse
import json
import os
from simulate import simulate


DEF_NUM_SIMS = 1


def run(fp: str, output_dir: str = None):
    with open(fp, 'r') as f:
        config_data = json.load(f)

    model_data: dict = config_data['model']
    center_data: dict = config_data['center-model']  # New entry for conversion to center models
    tf_data: dict = config_data['tissue-forge']

    damping = float(center_data['damping'])
    space_conv = float(center_data['space_conv'])
    time_conv = float(center_data['time_conv'])

    dim = int(model_data['len_1']) * space_conv, int(model_data['len_2']) * space_conv
    sim_time = int(model_data['max_time']) * time_conv

    num_sims = tf_data.get('num_sims', DEF_NUM_SIMS)
    if output_dir is None:
        output_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'results', tf_data['output_name'])
    output_per = int(tf_data['output_per']) * time_conv

    simulate(output_dir=output_dir,
             num_sims=num_sims,
             output_per=output_per,
             dim=dim,
             sim_time=sim_time,
             dt=time_conv,
             model_label=model_data['model'],
             model_args=model_data['model_args'],  # Assumes only one possible model
             damping=damping)


class ArgParser(argparse.ArgumentParser):

    def __init__(self):
        super().__init__(description='Execute specification with Tissue Forge')

        self.add_argument('-f', '--file',
                          type=str,
                          required=True,
                          dest='spec_path',
                          help='Absolute path to specification with implementation specification for Tissue Forge')

        self.parsed_args = self.parse_args()

    @property
    def spec_path(self):
        return self.parsed_args.spec_path


if __name__ == '__main__':
    run(fp=ArgParser().spec_path)
