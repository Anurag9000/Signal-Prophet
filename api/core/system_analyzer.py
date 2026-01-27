"""
System property analyzer for Signals & Systems.
Analyzes: Linearity, Time-Invariance, Causality, Memory, Stability, Invertibility
"""

from api.core.utils import t, n, s, z, w, k, get_shared_modules_dict, clean_output_str
import re
import logging
import traceback
import numpy as np
from sympy import (symbols, sympify, diff, simplify, solve, Abs, DiracDelta, Heaviside, 
                   Function, integrate, Sum, oo, Integral, KroneckerDelta, Add, sin, cos, exp, log, Poly, factorial)
from sympy.parsing.sympy_parser import parse_expr, standard_transformations, implicit_multiplication_application

logger = logging.getLogger(__name__)

def analyze_system(equation: str, domain: str = 'continuous'):
    """
    Analyzes a system equation for all 6 fundamental properties.
    
    Args:
        equation: System equation as string (e.g., "2*x(t)" or "x[n-1]")
        domain: 'continuous' or 'discrete'
    
    Returns:
        dict with analysis results for each property
    """
    # Calculate impulse response for display
    h_expr = calculate_impulse_response(equation, domain)
    h_str = clean_output_str(str(h_expr), domain)
    
    results = {
        'linearity': check_linearity(equation, domain),
        'time_invariance': check_time_invariance(equation, domain),
        'causality': check_causality(equation, domain),
        'memory': check_memory(equation, domain),
        'stability': check_stability_bibo(h_expr, domain),
        'invertibility': check_invertibility(equation, domain),
        'impulse_response': h_str
    }
    
    return results


def check_linearity(eq: str, domain: str):
    """
    Checks if system is linear using symbolic substitution test.
    Tests: S[a*x1 + b*x2] == a*S[x1] + b*S[x2]
    Falls back to regex for complex cases.
    """
    try:
        x_func = Function('x')
        x_sym = symbols('x') # For cases where x is treated as symbol, not function
        
        a, b = symbols('a b', real=True, positive=True)
        var = t if domain == 'continuous' else n
        
        # Parse the system equation
        local_dict = {
            't': t, 'n': n, 'x': x_func,
            'u': Heaviside, 'd': DiracDelta,
            'Heaviside': Heaviside, 'DiracDelta': DiracDelta,
            'sin': sin, 'cos': cos, 'exp': exp, 'log': log, 'Abs': Abs
        }
        transformations = (standard_transformations + (implicit_multiplication_application,))
        
        # Pre-process: Normalize brackets for discrete signals
        clean_eq = eq.replace('^', '**')
        # Selective bracket replacement for signal functions only
        clean_eq = re.sub(r'x\[([^\]]*)\]', r'x(\1)', clean_eq)
        clean_eq = re.sub(r'h\[([^\]]*)\]', r'h(\1)', clean_eq)
        
        # Parse y = S[x]
        sys_expr = parse_expr(clean_eq, local_dict=local_dict, transformations=transformations)
        
        # Create two test inputs
        x1 = Function('x1')
        x2 = Function('x2')
        
        # Define combined input function
        # We need a way to substitute x(...) with a*x1(...) + b*x2(...)
        # SymPy's replace is robust for this
        
        # S[a*x1 + b*x2]
        def x_combined(*args):
             if not args: return a*x1(var) + b*x2(var)
             return a*x1(*args) + b*x2(*args)
             
        combined_input_expr = sys_expr.replace(x_func, x_combined)
        # Also replace bare 'x' if present
        combined_input_expr = combined_input_expr.subs(x_sym, a*x1(var) + b*x2(var))
        
        # a*S[x1] + b*S[x2]
        s_x1 = sys_expr.replace(x_func, x1).subs(x_sym, x1(var))
        s_x2 = sys_expr.replace(x_func, x2).subs(x_sym, x2(var))
        
        superposition = a*s_x1 + b*s_x2
        
        # Check if they're equal
        difference = simplify(combined_input_expr - superposition)
        
        if difference == 0:
            return {'status': 'yes', 'explanation': 'Satisfies superposition (additivity + homogeneity)'}
        else:
            return {'status': 'no', 'explanation': f'Non-linear: Fails superposition test'}
            
    except Exception as e:
        logger.warning(f"Symbolic linearity check failed: {e}. Falling back to regex.")
        # Fall back to regex-based heuristics
        non_linear_patterns = [
            (r'x\([^)]*\)\s*\*\*\s*[2-9]', 'Contains powers of input (x^2, x^3, etc.)'),
            (r'x\[[^\]]*\]\s*\*\*\s*[2-9]', 'Contains powers of input (x^2, x^3, etc.)'),
            (r'sin\(x[\(\[]', 'Contains sin(x(...))'),
            (r'cos\(x[\(\[]', 'Contains cos(x(...))'),
            (r'exp\(x[\(\[]', 'Contains exp(x(...))'),
            (r'log\(x[\(\[]', 'Contains log(x(...))'),
            (r'Abs\(x[\(\[]', 'Contains Abs(x(...))'),
            (r'\|x[\(\[].*\|', 'Contains |x|'),
        ]
        
        for pattern, reason in non_linear_patterns:
            if re.search(pattern, eq):
                return {'status': 'no', 'explanation': f'Non-linear: {reason}'}
        
        # Check for constant offset
        clean_eq_for_offset = re.sub(r'\([^)]*\)', '()', eq)
        clean_eq_for_offset = re.sub(r'\[[^\]]*\]', '[]', clean_eq_for_offset)
        
        # Look for additive constants not attached to x
        # This is hard to perfect with regex, but we try
        if re.search(r'[\+\-]\s*\d+(?!\s*[\*x\w\(\[])', clean_eq_for_offset):
            # Exclude e-10 scientific notation type stuff
            if not re.search(r'e[\+\-]\d+', eq):
                return {'status': 'no', 'explanation': 'Non-linear: Contains constant offset (affine system)'}
        
        return {'status': 'yes', 'explanation': 'Satisfies superposition (additivity + homogeneity)'}


def check_time_invariance(eq: str, domain: str):
    """
    Checks if system is time-invariant.
    Red flags: time-dependent coefficients (t*x(t), sin(t)*x(t)), 
    time scaling (x(2t)), or time-dependent offsets.
    """
    var = 't' if domain == 'continuous' else 'n'
    
    # Check for time-dependent coefficients or scaling
    # Mask out the contents of x(...) or x[...]
    masked_eq = re.sub(r'x[\(\[][^\]\)]*[\)\]]', 'x()', eq)
    
    # Now check if 't' or 'n' remains as a variable
    if re.search(rf'(?<![a-zA-Z]){var}(?![a-zA-Z])', masked_eq):
        return {'status': 'no', 'explanation': f'Time-variant: Contains explicit time variable {var} outside of input argument'}
        
    # Check for time scaling inside x(...)
    # x(2t), x(-t), x(t^2)
    # Check for anything multiplying var inside parens
    scaling_patterns = [
        rf'x[\(\[]\s*\d+\s*\*\s*{var}',
        rf'x[\(\[]\s*{var}\s*[\*/]',
        rf'x[\(\[]\s*{var}\s*\*\*',
        rf'x[\(\[]\s*-\s*{var}'
    ]
    for pattern in scaling_patterns:
        if re.search(pattern, eq):
            return {'status': 'no', 'explanation': f'Time-variant: Contains time scaling or reversal x(at)'}

    return {'status': 'yes', 'explanation': 'System behavior does not change over time'}


def check_causality(eq: str, domain: str):
    """
    Checks if system is causal.
    Red flags: x(t+1), x(2t) for positive t, x(-t) for negative t.
    """
    var = 't' if domain == 'continuous' else 'n'
    
    # 1. Check for explicit future shifts: x(t + k) where k > 0
    # Match x(t + 0.5) or x[n + 1]
    # We look for '+', but need to be careful of x(t + (-1)) which is causal
    if re.search(rf'x[\(\[]\s*{var}\s*\+\s*[\d\.]+', eq):
        return {'status': 'no', 'explanation': f'Non-causal: Depends on future input x({var}+k)'}
        
    # 2. Check for time scaling: x(2t), x(t^2), etc.
    # Most time scaling is non-causal.
    if re.search(rf'x[\(\[]\s*[\d\.]+\s*\*\s*{var}', eq) or re.search(rf'x[\(\[]\s*{var}\s*\*\*', eq):
        return {'status': 'no', 'explanation': f'Non-causal: Time scaling x(at) depends on future for {var}>0'}
        
    # 3. Check for time reversal: x(-t) or x(1-t)
    if re.search(rf'x[\(\[]\s*-\s*{var}', eq) or re.search(rf'x[\(\[]\s*\d+\s*-\s*{var}', eq):
        return {'status': 'no', 'explanation': f'Non-causal: Time reversal/shift x(k-{var}) depends on future for large negative {var}'}

    return {'status': 'yes', 'explanation': 'Output depends only on present and past inputs'}


def check_memory(eq: str, domain: str):
    """
    Checks if system has memory.
    Memoryless: output depends only on current input
    With Memory: depends on past/future (integrals, derivatives, delays)
    """
    if domain == 'continuous':
        # Check for integrals, derivatives, delays
        if 'integrate' in eq.lower() or '∫' in eq:
            return {'status': 'no', 'explanation': 'Has memory: Contains integration'}
        
        if 'diff' in eq.lower() or 'd/dt' in eq or "'" in eq:
            return {'status': 'no', 'explanation': 'Has memory: Contains differentiation'}
        
        # Check for delayed/advanced input x(t-...) or x(t+...)
        # A bit loose regex but covers common cases x(t-1)
        if re.search(r'x\(t\s*[\-\+]', eq):
            return {'status': 'no', 'explanation': 'Has memory: Contains time shift x(t±...)'}
    
    else:  # discrete
        # Check for delayed/advanced input x[n-...] or x[n+...]
        if re.search(r'x\[n\s*[\-\+]', eq):
            return {'status': 'no', 'explanation': 'Has memory: Contains time shift x[n±k]'}
        
        # Check for summation
        if 'sum' in eq.lower() or '∑' in eq:
            return {'status': 'no', 'explanation': 'Has memory: Contains summation'}
    
    return {'status': 'yes', 'explanation': 'Memoryless: Output depends only on current input'}


def calculate_impulse_response(eq: str, domain: str):
    """
    Calculates impulse response h(t) or h[n] by substituting delta function.
    """
    try:
        # Define x as a Function for substitution
        x_func = Function('x')
        x_sym = symbols('x')
        
        # Local dict for parsing
        local_dict = {
            't': t, 'n': n, 'x': x_func,
            'u': Heaviside, 'd': DiracDelta, 'delta': DiracDelta,
            'sin': sin, 'cos': cos, 'exp': exp, 'log': log,
            'Heaviside': Heaviside, 'DiracDelta': DiracDelta, 'KroneckerDelta': KroneckerDelta
        }
        transformations = (standard_transformations + (implicit_multiplication_application,))
        
        # Pre-process: Normalize brackets for discrete signals
        clean_eq = eq.replace('^', '**')
        # Selective bracket replacement for signal functions only
        clean_eq = re.sub(r'x\[([^\]]*)\]', r'x(\1)', clean_eq)
        clean_eq = re.sub(r'h\[([^\]]*)\]', r'h(\1)', clean_eq)
        
        expr = parse_expr(clean_eq, local_dict=local_dict, transformations=transformations)
        
        # Substitution Logic
        if domain == 'continuous':
            # Lambda to replace x(args) with DiracDelta(args)
            def sub_impl(*args):
                if not args: return DiracDelta(t)
                return DiracDelta(args[0])
            
            h_expr = expr.replace(x_func, sub_impl).replace(x_sym, DiracDelta(t))
        else:
             # Lambda to replace x[args] -> KroneckerDelta(args, 0)
            def sub_impl(*args):
                if not args: return KroneckerDelta(n, 0)
                return KroneckerDelta(args[0], 0)
            
            h_expr = expr.replace(x_func, sub_impl).replace(x_sym, KroneckerDelta(n, 0))
            
        return h_expr
    except Exception as e:
        logger.error(f"Error calculating impulse response: {e}")
        logger.error(traceback.format_exc())
        return None

def check_stability_bibo(h_expr, domain: str):
    """
    Checks BIBO stability.
    Stable if Integral/Sum |h| is finite.
    """
    if h_expr is None:
         return {'status': 'unknown', 'explanation': 'Could not calculate impulse response to check stability'}
         
    try:
        # Heuristic for Delta functions (they are stable in SnS context)
        if domain == 'continuous':
            # If h(t) is JUST a sum of deltas, it's stable
            # Remove deltas and check what remains
            terms = Add.make_args(h_expr)
            remains = [t_term for t_term in terms if not t_term.has(DiracDelta)]
            
            if not remains:
                return {'status': 'yes', 'explanation': 'Stable: Impulse response consists only of Dirac Deltas (finite energy)'}
                
            # Otherwise, try to integrate what remains
            remaining_h = sum(remains)
            try:
                abs_h = simplify(Abs(remaining_h))
                # Check directly first
                stability_limit = integrate(abs_h, (t, -oo, oo))
                
                if stability_limit.is_finite:
                    return {'status': 'yes', 'explanation': 'Stable: Integral of |h(t)| is finite'}
                elif stability_limit.has(oo) or stability_limit == oo:
                    return {'status': 'no', 'explanation': 'Unstable: Integral of |h(t)| is infinite'}
            except Exception as e:
                logger.debug(f"Stability check (integral) failed: {e}")

            # Numerical fallback for continuous: Check if it decays at both ends
            try:
                from sympy import lambdify
                h_fn = lambdify(t, remaining_h, modules=['numpy', 'sympy'])
                t_test = np.linspace(-100, 100, 2000)
                h_vals = h_fn(t_test)
                if np.isscalar(h_vals): h_vals = np.full_like(t_test, h_vals)
                
                # Check for NaNs or Infs
                if np.any(np.isinf(h_vals)) or np.any(np.isnan(h_vals)):
                     return {'status': 'no', 'explanation': 'Unstable: Response blows up (NaN/Inf)'}

                h_mag = np.abs(h_vals)
                
                # Check end of response average magnitude vs peak
                mid_idx = len(h_mag) // 2
                peak = np.max(h_mag)
                if peak < 1e-10:
                     return {'status': 'yes', 'explanation': 'Stable: Response is effectively zero'}
                     
                tail_avg = np.mean(h_mag[:100]) + np.mean(h_mag[-100:])
                
                # If tail is significant compared to peak, it's not decaying -> Unstable
                if tail_avg > 0.1 * peak:
                     return {'status': 'no', 'explanation': 'Unstable: Impulse response does not appear to decay (Numerical test)'}
                
                # Also safeguard against growing exponentials
                if h_mag[-1] > h_mag[mid_idx] * 1.5:
                     return {'status': 'no', 'explanation': 'Unstable: Growing response detected'}
                     
                return {'status': 'yes', 'explanation': 'Stable: Impulse response appears to decay (Numerical test)'}
            except Exception as e:
                logger.debug(f"Stability check (numeric) failed: {e}")
                
        else: # Discrete
            terms = Add.make_args(h_expr)
            remains = [term for term in terms if not term.has(KroneckerDelta)]
            
            if not remains:
                return {'status': 'yes', 'explanation': 'Stable: Impulse response consists only of Kronecker Deltas'}
            
            remaining_h = sum(remains)
            # Use a numeric-symbolic hybrid for stability check
            try:
                stability_limit = Sum(Abs(remaining_h), (n, -oo, oo)).doit()
                if stability_limit.is_finite:
                    return {'status': 'yes', 'explanation': 'Stable: Sum of |h[n]| is finite'}
                elif stability_limit == oo:
                    return {'status': 'no', 'explanation': 'Unstable: Sum of |h[n]| is infinite'}
            except Exception as e:
                logger.debug(f"Stability check (discrete sum) failed: {e}")
            
            # Fallback to numerical heuristic for stability
            try:
                from sympy import lambdify
                h_fn = lambdify(n, remaining_h, modules=['numpy', 'sympy'])
                n_test = np.arange(-100, 101)
                h_vals = np.abs(h_fn(n_test))
                
                # Use relative threshold based on peak value
                peak_val = np.max(h_vals)
                sum_val = np.sum(h_vals)
                
                # If peak is very small, system is essentially zero (stable)
                if peak_val < 1e-10:
                    return {'status': 'yes', 'explanation': 'Stable: Response is effectively zero'}
                
                # Check if sum is excessively large relative to number of samples
                # For a stable system, average magnitude should decay
                avg_magnitude = sum_val / len(h_vals)
                if avg_magnitude > peak_val * 0.5:  # If average is too close to peak, not decaying
                     return {'status': 'no', 'explanation': 'Unstable: Sum of |h[n]| is very large (not decaying)'}
                
                if h_vals[-1] > h_vals[len(h_vals)//2] * 2:
                     return {'status': 'no', 'explanation': 'Unstable: Growing response'}
                     
                return {'status': 'yes', 'explanation': 'Stable: Impulse response appears to decay (Numerical test)'}
            except:
                pass
                
        return {'status': 'unknown', 'explanation': 'Stability check inconclusive'}
                 
    except Exception as e:
         return {'status': 'unknown', 'explanation': f'Stability analysis error: {str(e)}'}

def check_stability(eq: str, domain: str):
    # Wrapper for backend compat if needed
    h_expr = calculate_impulse_response(eq, domain)
    return check_stability_bibo(h_expr, domain)


def check_invertibility(eq: str, domain: str):
    """
    Checks if system is invertible (distinct inputs -> distinct outputs).
    Red flags: squaring (loses sign), absolute value
    """
    # Check for operations that lose information
    if re.search(r'x\([^)]*\)\s*\*\*\s*2', eq) or re.search(r'x\[[^\]]*\]\s*\*\*\s*2', eq):
        return {'status': 'no', 'explanation': 'Not invertible: Squaring loses sign information'}
    
    if 'abs' in eq.lower() or '|' in eq:
        return {'status': 'no', 'explanation': 'Not invertible: Absolute value loses sign information'}
    
    # Check for simple scaling (invertible)
    if re.match(r'^\s*[\d.]+\s*\*\s*x[\(\[]', eq):
        return {'status': 'yes', 'explanation': 'Invertible: Simple scaling can be reversed'}
    
    return {'status': 'yes', 'explanation': 'No common non-invertible operations detected'}

def calculate_system_response(equation: str, input_str: str, domain: str):
    """
    Calculates the system response y(t) or y[n] for a given input x(t) or x[n].
    Returns (output_expr_str, output_plot_data)
    """
    from api.core import symbolic
    
    try:
        # 1. Parse Input Expression
        input_expr = symbolic.parse_signal(input_str, domain)
        
        # 2. Parse System Equation
        var = t if domain == 'continuous' else n
        x_func = Function('x')
        x_sym = symbols('x')
        
        # Use symbolic.parse_signal to get the base expression
        expr = symbolic.parse_signal(equation, domain)
        
        # Handle functional 'x(t)' or 'x[n]'
        # We want to replace all occurrences of x(...) with input_expr evaluating its argument
        output_expr = expr.replace(x_func, lambda arg: input_expr.subs(var, arg))
        
        # Handle symbolic 'x' if it was parsed as a symbol
        output_expr = output_expr.subs(x_sym, input_expr)
        
        # 3. Generate Data
        px, py = symbolic.generate_plot_data(output_expr, -5, 10, domain=domain)
        
        # 4. Format output string with proper bracket notation for discrete
        output_str = str(output_expr).replace('**', '^').replace('DiracDelta', 'd').replace('Heaviside', 'u')
        if domain == 'discrete':
            # Use regex for selective bracket replacement
            import re
            output_str = re.sub(r'\((t|n|k)([\+\-]\d+)?\)', r'[\1\2]', output_str)
            
        return output_str, {"x": px, "y": py}
    except Exception as e:
        logger.error(f"Error in calculate_system_response: {e}")
        logger.error(traceback.format_exc())
        return "Error calculating response", {"x": [], "y": []}
