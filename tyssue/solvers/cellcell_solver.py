from scipy import optimize

import numpy as np

def get_default_settings():
    default_settings = {
        'norm_factor': 1,
        'minimize': {
            'jac': opt_grad,
            'method': 'L-BFGS-B',
            'options': {'disp': False,
                        'ftol': 1e-6,
                        'gtol': 1e-3},
            }
        }
    return default_settings


def find_energy_min(ccmesh, geom, model,
                    pos_idx=None,
                    **settings_kw):

    settings = get_default_settings()
    settings.update(**settings_kw)

    coords = ccmesh.coords
    if pos_idx is None:
        pos0 = ccmesh.cell_df[coords].values.ravel()
        pos_idx = ccmesh.cell_df.index
    else:
        pos0 = ccmesh.cell_df.loc[pos_idx, coords].values.ravel()

    max_length = 2 * ccmesh.cc_df['length'].max()
    bounds = np.vstack([pos0 - max_length,
                        pos0 + max_length]).T
    if settings['minimize']['jac'] is None:
        return
    res = optimize.minimize(opt_energy, pos0,
                            args=(pos_idx, ccmesh, geom, model),
                            bounds=bounds, **settings['minimize'])
    return res


def set_pos(pos, pos_idx, ccmesh):
    ndims = len(ccmesh.coords)
    pos_ = pos.reshape((pos.size//ndims, ndims))
    ccmesh.cell_df.loc[pos_idx, ccmesh.coords] = pos_


def opt_energy(pos, pos_idx, ccmesh, geom, model):
    set_pos(pos, pos_idx, ccmesh)
    geom.update_all(ccmesh)
    return model.compute_energy(ccmesh, full_output=False)


# The unused arguments bellow are legit, need same call sig as above
def opt_grad(pos, pos_idx, ccmesh, geom, model):
    grad_i = model.compute_gradient(ccmesh, components=False)
    return grad_i.values.flatten()


def approx_grad(ccmesh, geom, model):
    pos0 = ccmesh.cell_df[ccmesh.coords].values.ravel()
    pos_idx = ccmesh.cell_idx
    grad = optimize.approx_fprime(pos0,
                                  opt_energy,
                                  1e-9, pos_idx,
                                  ccmesh, geom, model)
    return grad


def check_grad(ccmesh, geom, model):

    pos0 = ccmesh.cell_df[ccmesh.coords].values.ravel()
    pos_idx = ccmesh.cell_idx
    grad_err = optimize.check_grad(opt_energy,
                                   opt_grad,
                                   pos0.flatten(),
                                   pos_idx,
                                   ccmesh, geom, model)
    return grad_err
