
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
        # For continuous, we want a high spike. For discrete, exactly 1 at 0.
        height = 5.0 if self.domain == 'continuous' else 1.0
        return np.where(np.abs(x) < tolerance, height, 0.0)

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
    """
    Standardize symbolic output for display (remove unnecessary decimals, simplify expressions).
    """
    if not isinstance(s, str):
        s = str(s)

    # Basic cleanup
    res = s.replace('**', '^').replace('*', '')

    # Engineering notation: replace DiracDelta with delta, Heaviside with u
    res = res.replace('DiracDelta', r'\delta').replace('Heaviside', 'u')
    res = res.replace('KroneckerDelta', r'\delta')  # For discrete
    res = res.replace('theta', 'u') # SymPy sometimes outputs \theta for Heaviside

    if domain == 'discrete':
        # Replace only parentheses around variables, including shifted ones
        # Capture variables: n, k, nv, m
        res = re.sub(r'\((n|k|nv|m|i|j)([\+\-]\d+)?\)', r'[\1\2]', res)
    
    # Final strip of any double backslashes that might have been escaped
    res = res.replace('\\\\', '\\')
    
    return res
