
import numpy as np
import sympy
import re
from sympy import symbols, Heaviside, DiracDelta, Max, Min, Abs, KroneckerDelta

# Global symbols
t, n, s, z, w, k = symbols('t n s z w k')

class VisualDirac:
    """Numerical proxy for DiracDelta and KroneckerDelta for plotting."""
    def __init__(self, domain='continuous'):
        self.domain = domain
    def __call__(self, x):
        tolerance = 0.05 if self.domain == 'continuous' else 0.1
        # For continuous, we want a spike. For discrete, exactly 1 at 0.
        return np.where(np.abs(x) < tolerance, 1.0, 0.0)

def get_shared_modules_dict(domain='continuous'):
    """Shared lambdify modules dictionary."""
    v_dirac = VisualDirac(domain)
    return [
        {
            'Heaviside': lambda x, *args: np.where(x >= 0, 1.0, 0.0),
            'DiracDelta': v_dirac,
            'VisualDirac': v_dirac,
            'KroneckerDelta': v_dirac,
            'rect': lambda x: np.where(np.abs(x) <= 0.5, 1.0, 0.0),
            'tri': lambda x: np.maximum(0, 1 - np.abs(x)),
            'sinc': np.sinc,
            'Max': np.maximum,
            'Min': np.minimum,
            'Abs': np.abs
        },
        'numpy'
    ]

def clean_output_str(s: str, domain: str = 'continuous'):
    """Standardizes symbolic output strings for SnS notation."""
    res = s.replace('**', '^').replace('DiracDelta', 'd').replace('Heaviside', 'u').replace('KroneckerDelta', 'd').replace('I', 'j')
    if domain == 'discrete':
        # Use regex to replace only parentheses around variables, not all parentheses
        res = re.sub(r'\((n|k|nv)\)', r'[\1]', res)
    return res
