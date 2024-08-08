import numpy as np
import tissue_forge as tf


def _do_impl_MODEL004(ptime: float,
                      bias: float,
                      speed: float,
                      bdir: tf.FVector3):
    pr = tf.Universe.dt / ptime if ptime > 0 else 2.0

    for ph in tf.Universe.particles:
        if np.random.uniform() < pr:
            ang = np.random.uniform() * 2.0 * np.pi
            rvec = tf.FVector3(np.cos(ang), np.sin(ang), 0.0)

            mot: tf.FVector3 = rvec * (1.0 - bias) + bdir * bias
            ph.force_init = mot.normalized() * speed


def _impl_MODEL004(ptime: float,
                   bias: float,
                   speed: float,
                   bdirx: float,
                   bdiry: float):
    bdir = tf.FVector3(bdirx, bdiry, 0)
    tf.event.on_time(period=0,
                     invoke_method=lambda e: _do_impl_MODEL004(ptime, bias, speed, bdir))
    _do_impl_MODEL004(ptime, bias, speed, bdir)


model_implementations = {
    'MODEL004': _impl_MODEL004
}


def get_model_implementation(model_label: str):
    try:
        return model_implementations[model_label]
    except KeyError:
        raise KeyError(f'Model with label {model_label} is not currently supported by Tissue Forge')


def from_json_data(model_label, *model_args):

    get_model_implementation(model_label)(*model_args)
