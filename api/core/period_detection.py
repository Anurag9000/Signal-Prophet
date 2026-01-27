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
        from api.core.symbolic import parse_signal
        expr = parse_signal(signal_eq, 'continuous')
        
        # periodicity(expr, symbol) returns the fundamental period or None
        period_sym = periodicity(expr, t)
        
        if period_sym is None:
            return None, "Signal appears to be aperiodic"
        
        # Only evaluate if it's a pure number (possibly with pi, etc.)
        # SymPy periodicity often returns symbolic expressions.
        if not period_sym.is_number:
             # Try to simplify/evalf and see if it becomes a number
             # This handles 2*pi/1 etc.
             period_sym = period_sym.simplify()
             if not period_sym.is_number:
                  return None, f"Detected symbolic period {period_sym} cannot be evaluated to a constant"

        period_val = float(period_sym.evalf())
        
        if period_val <= 0 or period_val > 5000:
            return None, f"Detected period {period_val} seems excessive or non-positive"
        
        return period_val, f"Detected period T = {period_val:.4f}"
        
    except Exception as e:
        return None, f"Period detection failed: {str(e)}"

def detect_period_dt(signal_eq: str, max_period_search=200, tolerance=1e-5):
    """
    Detect period N for discrete-time signals.
    Returns: (period: int|None, message: str)
    
    Args:
        signal_eq: Signal equation string
        max_period_search: Maximum period to search for (default 200, increased from 100)
        tolerance: Tolerance for period detection (default 1e-5)
    """
    try:
        from api.core.symbolic import parse_signal
        import numpy as np
        from sympy import lambdify
        
        expr = parse_signal(signal_eq, 'discrete')
        
        # Convert to numerical function
        from api.core.utils import get_shared_modules_dict
        m_dict = get_shared_modules_dict('discrete')
        x_func = lambdify(n, expr, modules=m_dict)
        
        # Test for periodicity by checking x[n] == x[n+N]
        # We need enough samples to verify several periods
        sample_len = max_period_search * 3
        n_samples = np.arange(0, sample_len)
        try:
            x_vals = x_func(n_samples)
        except:
             x_vals = np.array([complex(expr.subs(n, nv).evalf()) for nv in n_samples])
             
        if np.isscalar(x_vals):
            x_vals = np.full_like(n_samples, x_vals, dtype=complex)
        
        # Try periods from 1 up to max_period_search
        for N_test in range(1, max_period_search + 1):
            # Check if x[n] ≈ x[n + N_test] for all available samples
            # Use enough points to be confident (e.g. 50 points or remaining range)
            check_len = min(50, len(x_vals) - N_test)
            if check_len < 2: continue
            
            if np.allclose(x_vals[:check_len], x_vals[N_test:N_test+check_len], atol=1e-5):
                return N_test, f"Detected period N = {N_test}"
        
        return None, f"No period detected (up to N={max_period_search})"
        
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
        status = "✓" if (period is None and expected is None) or (period and expected and abs(period - float(expected)) < 0.01) else "✗"
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
