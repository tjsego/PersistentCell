import argparse
import csv
import json
from matplotlib import pyplot as plt
import numpy as np
import os
from typing import Dict, List, Tuple


DEF_DPI = 300
DEF_FIGSIZE = 6.0, 6.0
DEF_ALPHA = 0.1
DEF_COLOR = 'gray'


def load_results(results_dir: str):
    results_files = [f for f in os.listdir(results_dir) if f.startswith('sim_') and f.endswith('.json')]
    results_nums = [int(f.replace('sim_', '').replace('.json', '')) for f in results_files]
    results_files_map = {results_nums[i]: os.path.join(results_dir, results_files[i]) for i in range(len(results_nums))}
    
    results_data = {}
    for num, fp in results_files_map.items():
        with open(fp, 'r') as f:
            fdata = json.load(f)
            results_data[num] = dict(time=np.asarray(fdata['time'], dtype=int),
                                     com_1=np.asarray(fdata['com_1'], dtype=float),
                                     com_2=np.asarray(fdata['com_2'], dtype=float))

    return results_files_map, results_data


def output_standard(results_data: Dict[int, Dict[str, np.ndarray]], fp: str):
    sample_int = list(results_data.keys())[0]

    min_steps = results_data[sample_int]['time'].shape[0]

    results_names = list(results_data[sample_int])
    results_names.remove('time')
    results_names.insert(0, 'time')

    # 'time', 'id', 'com_1', 'com_2', ...
    column_names = [results_names[0]] + ['id'] + results_names[1:]
    with open(fp, 'w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=column_names)
        writer.writeheader()
        for rep_num, rep_data in results_data.items():
            for i in range(min_steps):
                data = {k: float(rep_data[k][i]) for k in results_names}
                data['id'] = rep_num
                writer.writerow(data)


def generate_plots(results_data: Dict[int, Dict[str, np.ndarray]],
                   output_dir: str,
                   name_prefix: str = None,
                   dpi=DEF_DPI,
                   results_names: List[str] = None,
                   figsize: Tuple[float, float] = None,
                   alpha=DEF_ALPHA,
                   color=DEF_COLOR):
    
    if not os.path.isdir(output_dir):
        raise NotADirectoryError(output_dir)

    if name_prefix is None:
        name_prefix = ''
    
    if results_names is None:
        sample_int = list(results_data.keys())[0]
        results_names = list(results_data[sample_int].keys())
    if 'time' in results_names:
        results_names.remove('time')

    if figsize is None:
        figsize = DEF_FIGSIZE

    figs, axs = {}, {}
    for name in results_names:
        figs[name], axs[name] = plt.subplots(1, 1, layout='compressed', figsize=figsize)

    for v in results_data.values():
        for name in results_names:
            axs[name].plot(v['time'], v[name], alpha=alpha, color=color)

    for name, ax in axs.items():
        ax.set_xlabel('time')
        ax.set_ylabel(name)

    for name, fig in figs.items():
        exported_name = f'{name}.png'
        if name_prefix:
            exported_name = name_prefix + '_' + exported_name
        figpath = os.path.join(output_dir, exported_name)
        print(f'Saving {name}: {figpath}')
        fig.savefig(figpath, dpi=dpi)


def aggregate_stats(results_dir: str,
                    output_dir: str,
                    export_standard: bool,
                    export_figs: bool,
                    dpi=DEF_DPI,
                    rendered_names: List[str] = None,
                    figsize: Tuple[float, float] = None,
                    alpha=DEF_ALPHA,
                    color=DEF_COLOR):
    
    if not os.path.isdir(results_dir):
        raise NotADirectoryError(results_dir)
    if not os.path.isdir(output_dir):
        os.makedirs(output_dir)

    print('Results directory   :', results_dir)
    print('Output directory    :', output_dir)
    print('Export standard data:', export_standard)
    print('Export figures      :', export_figs)

    print('Loading results...')
    results = load_results(results_dir)[1]

    if export_standard:
        print('Exporting standard data...')
        output_fp = os.path.join(output_dir, 'data.csv')
        print(f'\t{output_fp}')
        output_standard(results, output_fp)

    if export_figs:
        print('Exporting rendered data...')
        generate_plots(results, output_dir, name_prefix='raw', dpi=dpi, results_names=rendered_names, figsize=figsize, alpha=alpha, color=color)


class ArgParser(argparse.ArgumentParser):
    
    def __init__(self):
        super().__init__(description='Render spatial data')

        self.add_argument('-r', '--results-dir',
                          type=str,
                          required=True,
                          dest='results_dir',
                          help='Absolute path to results set')
        
        self.add_argument('-o', '--output-dir',
                          type=str,
                          required=True,
                          dest='output_dir',
                          help='Absolute path of output directory')
        
        self.add_argument('-s', '--export-standard',
                          action='store_true',
                          required=False,
                          dest='export_standard',
                          help='Flag to export standard formatted data')
        
        self.add_argument('-f', '--export-figs',
                          action='store_true',
                          required=False,
                          dest='export_figs',
                          help='Flag to export figures')
        
        self.add_argument('-d', '--dpi',
                          type=int,
                          required=False,
                          default=DEF_DPI,
                          dest='dpi',
                          help='DPI for exported figures')

        self.add_argument('-n', '--names',
                          type=str,
                          required=False,
                          nargs='+', 
                          default=None,
                          dest='rendered_names', 
                          help='Names of results outputs during rendering')
        
        self.add_argument('-wh', '--figsize',
                          type=float,
                          nargs=2,
                          required=False,
                          default=DEF_FIGSIZE,
                          dest='figsize',
                          help='Figure size (width, height), in inches')
        
        self.add_argument('-la', '--alpha',
                          type=float,
                          required=False,
                          default=DEF_ALPHA,
                          dest='alpha',
                          help='Alpha value of plotted trajectories')
        
        self.add_argument('-lc', '--color',
                          type=str,
                          required=False,
                          default=DEF_COLOR,
                          dest='color',
                          help='Color of plotted trajectories')

        self.parsed_args = self.parse_args()

    @property
    def results_dir(self):
        return self.parsed_args.results_dir

    @property
    def output_dir(self):
        return self.parsed_args.output_dir

    @property
    def export_standard(self):
        return self.parsed_args.export_standard

    @property
    def export_figs(self):
        return self.parsed_args.export_figs

    @property
    def dpi(self):
        return self.parsed_args.dpi

    @property
    def rendered_names(self):
        return self.parsed_args.rendered_names

    @property
    def figsize(self):
        return self.parsed_args.figsize[0], self.parsed_args.figsize[1]

    @property
    def alpha(self):
        return self.parsed_args.alpha

    @property
    def color(self):
        return self.parsed_args.color

    def kwargs(self) -> dict:
        return dict(results_dir=self.results_dir, 
                    output_dir=self.output_dir, 
                    export_standard=self.export_standard,
                    export_figs=self.export_figs,
                    dpi=self.dpi, 
                    rendered_names=self.rendered_names, 
                    figsize=self.figsize, 
                    alpha=self.alpha, 
                    color=self.color)


if __name__ == '__main__':
    aggregate_stats(**ArgParser().kwargs())
