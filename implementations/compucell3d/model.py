from cc3d.core import PyCoreSpecs as pcs
import json
from math import sqrt
from simulate import TrackingSteppable

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
                 contact_lm, 
                 contact_nbs_order,
                 model_label, 
                 model_args):
    result = [
        pcs.PottsCore(dim_x=dim_1, 
                      dim_y=dim_2, 
                      neighbor_order=neighbor_order_potts),
        pcs.CellTypePlugin(cell_type_name),
        pcs.VolumePlugin(pcs.VolumeEnergyParameter(cell_type_name, cell_area_target, cell_area_lm)),
        pcs.ContactPlugin(contact_nbs_order, pcs.ContactEnergyParameter('Medium', cell_type_name, contact_lm)),
        pcs.CenterOfMassPlugin()
    ]
    result.extend(model_implementations[model_label](*model_args))
    return result


class SimTrackingSteppable(TrackingSteppable):
    
    _cell_type_name = cell_type_name
    _cell_length_target = 0
    _buffer = 0

    @classmethod
    def cell_type_name(cls) -> str:
        return cls._cell_type_name

    @classmethod
    def cell_length_target(cls) -> int:
        return cls._cell_length_target

    @classmethod
    def buffer(cls) -> int:
        return cls._buffer


def model(cell_area_target, 
          cell_area_lm, 
          dim_1, 
          dim_2, 
          buffer, 
          neighbor_order_potts, 
          contact_lm,
          contact_nbs_order,
          model_label,
          model_args):
    SimTrackingSteppable._cell_length_target = int(sqrt(cell_area_target))
    SimTrackingSteppable._buffer = buffer
    return create_specs(dim_1, 
                        dim_2, 
                        neighbor_order_potts,
                        cell_area_target,
                        cell_area_lm,
                        contact_lm,
                        contact_nbs_order,
                        model_label,
                        model_args), SimTrackingSteppable


def from_json_data(spec_data: dict):
    return model(cell_area_target=int(spec_data['cpm_area_c']),
                 cell_area_lm=int(spec_data['cpm_area_v']),
                 dim_1=int(spec_data['len_1']),
                 dim_2=int(spec_data['len_2']),
                 buffer=int(spec_data['buffer']),
                 neighbor_order_potts=int(spec_data['cpm_nbs_n']),
                 contact_lm=float(spec_data['cpm_contact_c']),
                 contact_nbs_order=int(spec_data['cpm_contact_n']),
                 model_label=spec_data['model'],
                 model_args=spec_data['model_args'])


def from_spec(fp: str):
    with open(fp, 'r') as f:
        spec_data = json.load(f)

    return from_json_data(spec_data)
