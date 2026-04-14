#!/usr/bin/env python
"""
Patch Test for Laplace Equation (3D)
"""
import numpy as np

def get_solution(ts, coors, mode=None, **kwargs):
    if mode == 'qp':
        return {'phi': coors[:, 2]}
    else:
        return {'phi': coors[:, 2]}

# 直接定义 regions 字典（使用表达式）
regions = {
    'Omega': 'all',
    'Gamma_Top': ('vertices in (z > 0.999)', 'facet'),
    'Gamma_Bottom': ('vertices in (z < 0.001)', 'facet'),
}

options = {
    'output_dir': './sfepy_output',
    'solution': get_solution,
    'coefs': 'coefs',
}

filename_mesh = 'box.msh'

materials = {
    'coefs': ({'c': 1.0},),
}

fields = {
    'potential': ('real', 1, 'Omega', 1)
}

variables = {
    'phi': ('unknown field', 'potential', 0),
    'v': ('test field', 'potential', 'phi'),
}

equations = {
    'Laplace': """dw_laplace.i.Omega(coefs.c, v, phi) = 0"""
}

ebcs = {
    'fixed_top': ('Gamma_Top', {'phi.0': 1.0}),
    'fixed_bottom': ('Gamma_Bottom', {'phi.0': 0.0}),
}

solvers = {
    'ls': ('ls.scipy_direct', {}),
    'nls': ('nls.newton', {'i_max': 1, 'eps_a': 1e-10}),
}
