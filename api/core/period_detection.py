"""
Period detection for Fourier Series (CT and DT)
"""
from sympy import symbols, sympify, periodicity, simplify, pi, sin, cos, exp, I
from sympy.parsing.sympy_parser import parse_expr, standard_transformations, implicit_multiplication_application
import re

t, n = symbols('t n')

def detect_period_ct(signal_eq: str):
    """
    Detect period T for continuous-time signals.
    Returns: (period: float|None, message: str)
    """
    try:
        # Parse the signal
        from api.core.symbolic import parse_signal
        expr = parse_signal(signal_eq, 'continuous')
        
        # Use SymPy's periodicity function
        # periodicity(expr, symbol) returns the fundamental period or None
        period_sym = periodicity(expr, t)
        
        if period_sym is None:
            return None, "Signal appears to be aperiodic"
        
        # Evaluate to float
        period_val = float(period_sym.evalf())
        
        # Sanity check
        if period_val <= 0 or period_val > 1000:
            return None, f"Detected period {period_val} seems unreasonable"
        
        return period_val, f"Detected period T = {period_val:.4f}"
        
    except Exception as e:
        return None, f"Period detection failed: {str(e)}"

def detect_period_dt(signal_eq: str, max_N=100):
    """
    Detect period N for discrete-time signals.
    Returns: (period: int|None, message: str)
    """
    try:
        from api.core.symbolic import parse_signal
        import numpy as np
        from sympy import lambdify
        
        expr = parse_signal(signal_eq, 'discrete')
        
        # Convert to numerical function
        x_func = lambdify(n, expr, modules=['numpy'])
        
        # Test for periodicity by checking x[n] == x[n+N] for various N
        # Sample the signal at n = 0 to 99
        n_samples = np.arange(0, max_N)
        x_vals = x_func(n_samples)
        
        # Handle scalar output
        if np.isscalar(x_vals):
            x_vals = np.full_like(n_samples, x_vals, dtype=float)
        
        # Try periods from 1 to max_N/2
        for N_test in range(1, max_N // 2):
            # Check if x[n] ≈ x[n + N_test] for all sampled n
            is_periodic = True
            
            for i in range(len(n_samples) - N_test):
                if not np.isclose(x_vals[i], x_vals[i + N_test], atol=1e-6):
                    is_periodic = False
                    break
            
            if is_periodic:
                return N_test, f"Detected period N = {N_test}"
        
        return None, "No period detected (signal may be aperiodic or period > 50)"
        
    except Exception as e:
        return None, f"Period detection failed: {str(e)}"

# Test the functions
if __name__ == "__main__":
    print("Testing Period Detection\n" + "="*50)
    
    # CT tests
    ct_tests = [
        ("sin(t)", 2*pi),
        ("sin(2*t)", pi),
        ("cos(3*t)", 2*pi/3),
        ("|sin(t)|", pi),  # Absolute value halves the period
        ("exp(t)", None),  # Aperiodic
    ]
    
    print("\nContinuous-Time Tests:")
    for signal, expected in ct_tests:
        period, msg = detect_period_ct(signal)
        status = "✓" if (period is None and expected is None) or (period and expected and abs(period - expected) < 0.01) else "✗"
        print(f"{status} {signal}: {msg}")
    
    # DT tests
    dt_tests = [
        ("cos(2*pi*n/10)", 10),
        ("sin(pi*n/4)", 8),
        ("(-1)**n", 2),
        ("n", None),  # Aperiodic
    ]
    
    print("\nDiscrete-Time Tests:")
    for signal, expected in dt_tests:
        period, msg = detect_period_dt(signal)
        status = "✓" if (period == expected) else "✗"
        print(f"{status} {signal}: {msg}")
