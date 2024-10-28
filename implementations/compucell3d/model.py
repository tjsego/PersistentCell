from cc3d import __version__ as cc3d_version
from cc3d import __revision__ as cc3d_revision
from cc3d import __githash__ as cc3d_githash
from cc3d.core import PyCoreSpecs as pcs
import json
from math import sqrt
from typing import Any, List, Optional, Type, Union

cell_type_name = 'Cell'

# Check version-dependent stuff
HAS_SURFACE_NBS = 'neighbor_order' in pcs.SurfacePlugin.check_dict


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
method_implementation = 'CPM'


__registered_types__ = {
    bool.__name__: bool,
    float.__name__: float,
    int.__name__: int,
    str.__name__: str
}


def register_type(_t: Type):
    global __registered_types__
    __registered_types__[_t.__name__] = _t


def to_json(_o):
    if isinstance(_o, (list, tuple)):
        return type(_o).__name__, [type(x).__name__ for x in _o], [x for x in _o]
    else:
        return type(_o).__name__, _o


def from_json(_d):
    d_type = _d[0]
    if d_type in [list.__name__, tuple.__name__]:
        d = []
        e_types, e_vals = _d[1], _d[2]
        for i in range(len(e_types)):
            e_type, e_val = e_types[i], e_vals[i]
            if e_type not in __registered_types__:
                raise TypeError(f'Unknown type name: {e_type}')
            d.append(__registered_types__[e_type](e_val))
        return d if _d[0] == list.__name__ else tuple(d)
    else:
        if d_type not in __registered_types__:
            raise TypeError(f'Unknown type name: {d_type}')
        return __registered_types__[_d[0]](_d[1])


class SpecConstraint:

    def __init__(self,
                 _key: str,
                 output_type: Type = None,
                 supported_input_types: Union[Type, List[Type]] = None,
                 positive: bool = None,
                 non_negative: bool = None,
                 in_list: List[Any] = None,
                 equal_to: Any = None):

        if len([x for x in [positive, non_negative, in_list, equal_to] if x is not None]) > 1:
            raise ValueError('Too many constraints specified.')

        if in_list is not None and len(in_list) == 0:
            raise ValueError(f'List of valid inputs is empty.')

        self.key = _key
        self.output_type = output_type
        self.positive = positive
        self.non_negative = non_negative
        self.in_list: Optional[List[Any]] = in_list
        self.equal_to = equal_to

        if supported_input_types is None:
            self.supported_input_types = output_type if output_type is not None else object
        else:
            self.supported_input_types = supported_input_types

    def to_json(self):
        result = dict(key=self.key)
        if self.output_type is not None:
            result['output_type'] = self.output_type.__name__
        if self.supported_input_types != object:
            if isinstance(self.supported_input_types, list):
                result['supported_input_types'] = [t.__name__ for t in self.supported_input_types]
            else:
                result['supported_input_types'] = self.supported_input_types.__name__
        if self.positive is not None and self.positive:
            result['positive'] = self.positive
        if self.non_negative is not None and self.non_negative:
            result['non_negative'] = self.non_negative
        if self.in_list is not None:
            result['in_list'] = to_json(self.in_list)
        if self.equal_to is not None:
            result['equal_to'] = to_json(self.equal_to)
        return result

    @classmethod
    def from_json(cls, _data: dict):
        args = (_data['key'],)
        kwargs = dict()

        if 'output_type' in _data:
            kwargs['output_type'] = __registered_types__[_data['output_type']]

        if 'supported_input_types' in _data:
            supported_input_types = _data['supported_input_types']
            if isinstance(supported_input_types, list):
                supported_input_types = [__registered_types__[n] for n in supported_input_types]
            else:
                supported_input_types = __registered_types__[supported_input_types]
            kwargs['supported_input_types'] = supported_input_types

        if 'positive' in _data and _data['positive']:
            kwargs['positive'] = True
        if 'non_negative' in _data and _data['non_negative']:
            kwargs['non_negative'] = True
        if 'in_list' in _data:
            kwargs['in_list'] = from_json(_data['in_list'])
        if 'equal_to' in _data:
            kwargs['equal_to'] = from_json(_data['equal_to'])

        return cls(*args, **kwargs)

    @property
    def supported_type_names(self):
        if isinstance(self.supported_input_types, list):
            return ', '.join([s.__name__ for s in self.supported_input_types])
        else:
            return self.supported_input_types.__name__

    def constraint(self, _x):
        if not self.check_type(_x):
            msg = f'Input type {type(_x).__name__} not supported. '
            msg += f'Supported types are {self.supported_type_names}.'
            raise TypeError(msg)
        if self.positive is not None and self.positive:
            return _x > 0.0
        elif self.non_negative is not None and self.non_negative:
            return _x >= 0.0
        elif self.in_list is not None and self.in_list:
            return _x in self.in_list
        elif self.equal_to is not None:
            return _x == self.equal_to
        else:
            return True

    @property
    def constraint_info(self) -> str:
        if self.positive is not None and self.positive:
            return 'Value must be positive'
        elif self.non_negative is not None and self.non_negative:
            return 'Value must be non-negative'
        elif self.in_list is not None and self.in_list:
            return f'Value must be one of {", ".join(self.in_list)}'
        elif self.equal_to is not None:
            return f'Value must be equal to {self.equal_to}'
        else:
            return ''

    def __str__(self):
        result = f'{self.key}'
        if self.supported_input_types != object:
            result += ' ('
            if isinstance(self.supported_input_types, list):
                result += ', '.join([s.__name__ for s in self.supported_input_types])
            else:
                result += self.supported_input_types.__name__
            result += ')'
        if self.output_type is not None:
            result += f' -> {self.output_type.__name__}'
        if self.constraint_info:
            result += f': {self.constraint_info}'
        return result

    def check_type(self, _x):
        if isinstance(self.supported_input_types, list):
            return isinstance(_x, tuple(self.supported_input_types))
        return isinstance(_x, self.supported_input_types)

    def check(self, _x):
        return self.check_type(_x) and self.constraint(_x)

    def verify(self, _x):
        if not self.check(_x):
            raise ValueError(f'Error for provided specification {_x}: {self}')

    def cast(self, _x):
        return self.output_type(_x) if self.output_type is not None else _x


class NumberConstraint(SpecConstraint):
    def __init__(self, _key: str, _output_type: Type, **kwargs):
        if 'supported_input_types' not in kwargs:
            kwargs['supported_input_types'] = [float, int]
        super().__init__(_key, _output_type, **kwargs)


class FloatConstraint(NumberConstraint):
    def __init__(self, _key: str, **kwargs):
        super().__init__(_key, float, **kwargs)


class IntegerConstraint(NumberConstraint):
    def __init__(self, _key: str, **kwargs):
        super().__init__(_key, int, **kwargs)


class StringConstraint(SpecConstraint):
    def __init__(self, _key: str, **kwargs):
        super().__init__(_key, str, **kwargs)


__supported_specs__ = [
    FloatConstraint('cpm_area_c', non_negative=True),
    FloatConstraint('cpm_area_v'),
    IntegerConstraint('cpm_nbs_n', positive=True),
    FloatConstraint('cpm_temperature', non_negative=True),
    FloatConstraint('cpm_perim_c', non_negative=True),
    FloatConstraint('cpm_perim_v'),
    IntegerConstraint('len_1', positive=True),
    IntegerConstraint('len_2', positive=True),
    IntegerConstraint('max_time', positive=True),
    StringConstraint('method', equal_to=method_implementation),
    StringConstraint('model', in_list=list(model_implementations.keys())),
    SpecConstraint('model_args')
]
# Implement version-dependent stuff
if HAS_SURFACE_NBS:
    __supported_specs__.append(IntegerConstraint('cpm_surface_nbs_n', positive=True))
else:
    __supported_specs__.append(IntegerConstraint('cpm_surface_nbs_n', equal_to=1))

__supported_specs_map__ = {s.key: s for s in __supported_specs__}


def info_data():
    return dict(
        cc3d_version=cc3d_version,
        cc3d_revision=cc3d_revision,
        cc3d_githash=cc3d_githash,
        specs={k: v.to_json() for k, v in __supported_specs_map__.items()}
    )


def info_str():
    msg = [
        f'CompuCell3D version     : {cc3d_version}',
        f'CompuCell3D revision    : {cc3d_revision}',
        f'CompuCell3D git hash    : {cc3d_githash}',
        f'Supported specifications:'
    ]
    msg.extend([f'\t{s}' for s in __supported_specs__])
    return '\n'.join(msg)


def verify_spec(spec_data: dict):
    """
    Tests whether all expected specification data is provided and all requested details are supported
    and produces a copy with correctly typed data.

    :param spec_data: imported spec data
    :return: formatted spec data
    """

    spec_data_formatted = {k: v for k, v in spec_data.items()}

    missing_names = [x for x in __supported_specs_map__.keys() if x not in spec_data_formatted.keys()]
    if missing_names:
        raise ValueError(f'Missing specification inputs: {missing_names}')
    for k, v in spec_data_formatted.items():
        if k in __supported_specs_map__:
            s = __supported_specs_map__[k]
            s.verify(v)
            spec_data_formatted[k] = s.cast(v)
    return spec_data_formatted


def get_model_implementation(model_label: str):
    try:
        return model_implementations[model_label]
    except KeyError:
        raise KeyError(f'Model with label {model_label} is not currently supported by CompuCell3D')


def create_specs(dim_1, 
                 dim_2,
                 fluctuation_amplitude,
                 neighbor_order_potts,
                 neighbor_order_surface,
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
                      fluctuation_amplitude=fluctuation_amplitude,
                      boundary_x=pcs.POTTSBOUNDARYPERIODIC,
                      boundary_y=pcs.POTTSBOUNDARYPERIODIC,
                      neighbor_order=neighbor_order_potts),
        pcs.CellTypePlugin(cell_type_name),
        pcs.VolumePlugin(pcs.VolumeEnergyParameter(cell_type_name, cell_area_target, cell_area_lm)),
        pcs.CenterOfMassPlugin()
    ]
    if HAS_SURFACE_NBS:
        result.append(
            pcs.SurfacePlugin(neighbor_order_surface,
                              None,
                              pcs.SurfaceEnergyParameter(cell_type_name, cell_perim_target, cell_perim_lm))
        )
    else:
        result.append(
            pcs.SurfacePlugin(pcs.SurfaceEnergyParameter(cell_type_name, cell_perim_target, cell_perim_lm))
        )
    result.extend(model_implementations[model_label](*model_args))
    return result


def model(cell_area_target, 
          cell_area_lm, 
          dim_1, 
          dim_2,
          fluctuation_amplitude,
          neighbor_order_potts,
          neighbor_order_surface,
          cell_perim_target,
          cell_perim_lm,
          model_label,
          model_args):
    return create_specs(dim_1, 
                        dim_2,
                        fluctuation_amplitude,
                        neighbor_order_potts,
                        neighbor_order_surface,
                        cell_area_target,
                        cell_area_lm,
                        cell_perim_target,
                        cell_perim_lm,
                        model_label,
                        model_args), cell_type_name, int(sqrt(cell_area_target))


def from_json_data(spec_data: dict):
    spec_data_formatted = verify_spec(spec_data)
    return model(cell_area_target=spec_data_formatted['cpm_area_c'],
                 cell_area_lm=spec_data_formatted['cpm_area_v'],
                 dim_1=spec_data_formatted['len_1'],
                 dim_2=spec_data_formatted['len_2'],
                 fluctuation_amplitude=spec_data_formatted['cpm_temperature'],
                 neighbor_order_potts=spec_data_formatted['cpm_nbs_n'],
                 neighbor_order_surface=spec_data_formatted['cpm_surface_nbs_n'],
                 cell_perim_target=spec_data_formatted['cpm_perim_c'],
                 cell_perim_lm=spec_data_formatted['cpm_perim_v'],
                 model_label=spec_data_formatted['model'],
                 model_args=spec_data_formatted['model_args'])


def from_spec(fp: str):
    with open(fp, 'r') as f:
        spec_data = json.load(f)

    return from_json_data(spec_data)
