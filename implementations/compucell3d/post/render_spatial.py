import argparse
from cc3d.CompuCellSetup.CC3DRenderer import CC3DBatchRenderer
from cc3d.core.GraphicsUtils.ScreenshotManagerCore import ScreenshotManagerCore
import json
import os
from typing import List


def render(output_data_dir: str, 
           render_dir: str, 
           screenshot_sim_path: str, 
           field_names: List[str] = None):

    print('Output directory             :', output_data_dir)
    print('Render output directory      :', render_dir)
    print('Field names                  :', field_names)
    print('Screenshot specification path:', screenshot_sim_path)
    
    if not os.path.isdir(render_dir):
        os.makedirs(render_dir)

    data_dirs = [f for f in os.listdir(output_data_dir) if f.startswith('sim_')]
    data_nums = [int(n.replace('sim_', '')) for n in data_dirs]
    data_nums.sort()
    data_dir_paths = {data_nums[i]: os.path.join(output_data_dir, data_dirs[i], 'LatticeData') for i in range(len(data_nums))}
    lds_files = [os.path.join(data_dir_paths[n], 'StepLDF.dml') for n in data_nums]

    with open(screenshot_sim_path, 'r') as f:
        screenshot_sim_data = json.load(f)
    screenshot_spec = ScreenshotManagerCore.starting_screenshot_description_data()
    ScreenshotManagerCore.append_screenshot_description_data(screenshot_spec, screenshot_sim_data['cells'])
    if field_names is not None:
        [ScreenshotManagerCore.append_screenshot_description_data(screenshot_spec, screenshot_sim_data['fields'][name]) for name in field_names]

    render_data_dirs = [os.path.join(render_dir, f'sim_{n}') for n in data_nums]

    already_rendered = []
    for i, d in enumerate(render_data_dirs):
        if os.path.isdir(d):
            print('Already found rendered data:', d)
            already_rendered.append(i)
        else:
            os.makedirs(d)
    already_rendered.reverse()
    [lds_files.pop(i) for i in already_rendered]
    [render_data_dirs.pop(i) for i in already_rendered]

    if len(lds_files) > 0:
        print(f'Rendering {len(lds_files)} simulations...')
        renderer = CC3DBatchRenderer(lds_files=lds_files, screenshot_spec=screenshot_spec, output_dirs=render_data_dirs)
        renderer.export_all(num_workers=min(os.cpu_count(), len(render_data_dirs)))
    else:
        print('No data to render')


class ArgParser(argparse.ArgumentParser):
    
    def __init__(self):
        super().__init__(description='Render spatial data')

        self.add_argument('-o', '--output-dir',
                          type=str,
                          required=True,
                          dest='output_data_dir',
                          help='Root directory of results set')

        self.add_argument('-r', '--render-dir',
                          type=str,
                          required=True,
                          dest='render_dir',
                          help='Root directory of rendering output')

        self.add_argument('-f', '--field-names',
                          type=str,
                          required=False,
                          nargs='+', 
                          default=None,
                          dest='field_names', 
                          help='Names of field outputs')

        self.add_argument('-s', '--screenshot-spec',
                          type=str,
                          required=True,
                          dest='screenshot_sim_path',
                          help='Absolute path to simulation screenshot specification output')

        self.parsed_args = self.parse_args()

    @property
    def output_data_dir(self) -> str:
        return self.parsed_args.output_data_dir

    @property
    def render_dir(self) -> str:
        return self.parsed_args.render_dir

    @property
    def field_names(self) -> str:
        return self.parsed_args.field_names

    @property
    def screenshot_sim_path(self) -> str:
        return self.parsed_args.screenshot_sim_path

    def kwargs(self) -> dict:
        return dict(output_data_dir=self.output_data_dir, render_dir=self.render_dir, field_names=self.field_names, screenshot_sim_path=self.screenshot_sim_path)


if __name__ == '__main__':
    render(**ArgParser().kwargs())
