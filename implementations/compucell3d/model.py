from cc3d.core import PyCoreSpecs as pcs
import json
from math import sqrt

cell_type_name = 'Cell'


def _impl_MODEL000(*args):
    return []


def _impl_MODEL003(*args):
    return [
        pcs.ExternalPotentialPlugin(lambda_x=float(args[0]), lambda_y=float(args[1]))
    ]


model_implementations = {
    'MODEL000': _impl_MODEL000,
    'MODEL003': _impl_MODEL003
}


def get_model_implementation(model_label: str):
    try:
        return model_implementations[model_label]
    except KeyError:
        raise KeyError(f'Model with label {model_label} is not currently supported by CompuCell3D')


def create_specs(dim_1, 
                 dim_2,
                 neighbor_order_potts, 
                 cell_area_target, 
                 cell_area_lm, 
                 cell_perim_target,
                 cell_perim_lm,
                 model_label, 
                 model_args):
    result = [
        pcs.Metadata(num_processors=1),
        pcs.PottsCore(dim_x=dim_1, 
                      dim_y=dim_2,
                      boundary_x=pcs.POTTSBOUNDARYPERIODIC,
                      boundary_y=pcs.POTTSBOUNDARYPERIODIC,
                      neighbor_order=neighbor_order_potts),
        pcs.CellTypePlugin(cell_type_name),
        pcs.VolumePlugin(pcs.VolumeEnergyParameter(cell_type_name, cell_area_target, cell_area_lm)),
        pcs.SurfacePlugin(pcs.SurfaceEnergyParameter(cell_type_name, cell_perim_target, cell_perim_lm)),
        pcs.CenterOfMassPlugin()
    ]
    result.extend(model_implementations[model_label](*model_args))
    return result


def model(cell_area_target, 
          cell_area_lm, 
          dim_1, 
          dim_2,
          neighbor_order_potts,
          cell_perim_target,
          cell_perim_lm,
          model_label,
          model_args):
    return create_specs(dim_1, 
                        dim_2, 
                        neighbor_order_potts,
                        cell_area_target,
                        cell_area_lm,
                        cell_perim_target,
                        cell_perim_lm,
                        model_label,
                        model_args), cell_type_name, int(sqrt(cell_area_target))


def from_json_data(spec_data: dict):
    return model(cell_area_target=int(spec_data['cpm_area_c']),
                 cell_area_lm=int(spec_data['cpm_area_v']),
                 dim_1=int(spec_data['len_1']),
                 dim_2=int(spec_data['len_2']),
                 neighbor_order_potts=int(spec_data['cpm_nbs_n']),
                 cell_perim_target=float(spec_data['cpm_perim_c']),
                 cell_perim_lm=float(spec_data['cpm_perim_v']),
                 model_label=spec_data['model'],
                 model_args=spec_data['model_args'])


def from_spec(fp: str):
    with open(fp, 'r') as f:
        spec_data = json.load(f)

    return from_json_data(spec_data)
