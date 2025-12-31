import numpy as np
from sympy import symbols, lambdify, Heaviside

n = symbols('n')
expr = Heaviside(n)

modules_dict = [
    {
        'Heaviside': lambda x: np.where(x >= 0, 1.0, 0.0),
    },
    'numpy'
]

f = lambdify(n, expr, modules=modules_dict)
n_vals = np.array([-1, 0, 1])
y_vals = f(n_vals)
print(f"n_vals: {n_vals}")
print(f"y_vals: {y_vals}")
