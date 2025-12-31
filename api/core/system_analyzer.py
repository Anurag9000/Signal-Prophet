"""
System property analyzer for Signals & Systems.
Analyzes: Linearity, Time-Invariance, Causality, Memory, Stability, Invertibility
"""

import re
from sympy import symbols, sympify, diff, simplify, solve, Abs, DiracDelta, Heaviside, Function, integrate, Sum, oo, Integral
from sympy.parsing.sympy_parser import parse_expr, standard_transformations, implicit_multiplication_application

t, n, x = symbols('t n x', real=True)
w = symbols('w', real=True)

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
    h_str = str(h_expr).replace('**', '^').replace('DiracDelta', 'd').replace('Heaviside', 'u')
    
    if domain == 'discrete':
        h_str = h_str.replace('(', '[').replace(')', ']')
    
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
    Checks if system is linear (superposition: additivity + homogeneity).
    Red flags: squaring, trig functions of input, non-zero constants
    """
    # Check for non-linear operations
    non_linear_patterns = [
        (r'x\([^)]*\)\s*\*\*\s*[2-9]', 'Contains powers of input (x^2, x^3, etc.)'),
        (r'x\[[^\]]*\]\s*\*\*\s*[2-9]', 'Contains powers of input (x^2, x^3, etc.)'),
        (r'sin\(x[\(\[]', 'Contains sin(x(...))'),
        (r'cos\(x[\(\[]', 'Contains cos(x(...))'),
        (r'tan\(x[\(\[]', 'Contains tan(x(...))'),
        (r'exp\(x[\(\[]', 'Contains exp(x(...))'),
        (r'log\(x[\(\[]', 'Contains log(x(...))'),
    ]
    
    for pattern, reason in non_linear_patterns:
        if re.search(pattern, eq):
            return {'status': 'no', 'explanation': f'Non-linear: {reason}'}
    
    # Check for constant offset (affine, not linear)
    # Strategy: Remove all content inside brackets () and [] to avoid matching numbers inside function calls
    # e.g. "x(t-3)" becomes "x()"
    clean_eq_for_offset = re.sub(r'\([^)]*\)', '()', eq)
    clean_eq_for_offset = re.sub(r'\[[^\]]*\]', '[]', clean_eq_for_offset)
    
    # Look for standalone numbers not multiplied by x
    # Regex: + or - followed by digit, NOT followed by * or variable or ( or [
    if re.search(r'[\+\-]\s*\d+(?!\s*[\*x\w\(\[])', clean_eq_for_offset):
        # Double check it's not part of scientific notation like 1e-10
        if not re.search(r'e[\+\-]\d+', eq): 
             return {'status': 'no', 'explanation': 'Non-linear: Contains constant offset (affine system)'}
    
    return {'status': 'yes', 'explanation': 'Satisfies superposition (additivity + homogeneity)'}


def check_time_invariance(eq: str, domain: str):
    """
    Checks if system is time-invariant.
    Red flags: time coefficient (t*x(t)), time scaling (x(2t))
    """
    if domain == 'continuous':
        # Check for t multiplying x
        if re.search(r't\s*\*\s*x\(', eq) or re.search(r'x\([^)]*\)\s*\*\s*t', eq):
            return {'status': 'no', 'explanation': 'Time-variant: Time coefficient multiplies input (t*x(t))'}
        
        # Check for time scaling
        if re.search(r'x\(\s*\d+\s*\*\s*t', eq) or re.search(r'x\(t\s*/\s*\d+', eq):
            return {'status': 'no', 'explanation': 'Time-variant: Time scaling in argument (x(2t) or x(t/2))'}
    
    else:  # discrete
        # Check for n multiplying x
        if re.search(r'n\s*\*\s*x\[', eq) or re.search(r'x\[[^\]]*\]\s*\*\s*n', eq):
            return {'status': 'no', 'explanation': 'Time-variant: Time coefficient multiplies input (n*x[n])'}
        
        # Check for time scaling
        if re.search(r'x\[\s*\d+\s*\*\s*n', eq) or re.search(r'x\[n\s*/\s*\d+', eq):
            return {'status': 'no', 'explanation': 'Time-variant: Time scaling in argument (x[2n])'}
    
    return {'status': 'yes', 'explanation': 'System behavior does not change over time'}


def check_causality(eq: str, domain: str):
    """
    Checks if system is causal (output depends only on present/past input).
    Red flags: future input (x(t+1)), time reversal (x(-t))
    """
    if domain == 'continuous':
        # Check for future input: x(t+...)
        if re.search(r'x\(t\s*\+', eq):
            return {'status': 'no', 'explanation': 'Non-causal: Depends on future input x(t+...)'}
        
        # Check for time reversal: x(-t)
        if re.search(r'x\(\s*-\s*t\s*\)', eq):
            return {'status': 'no', 'explanation': 'Non-causal: Time reversal x(-t)'}
    
    else:  # discrete
        # Check for future input: x[n+...]
        if re.search(r'x\[n\s*\+', eq):
            return {'status': 'no', 'explanation': 'Non-causal: Depends on future input x[n+...]'}
        
        # Check for time reversal: x[-n]
        if re.search(r'x\[\s*-\s*n\s*\]', eq):
            return {'status': 'no', 'explanation': 'Non-causal: Time reversal x[-n]'}
    
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
        
        # Check for delayed input x(t-...)
        if re.search(r'x\(t\s*-', eq):
            return {'status': 'no', 'explanation': 'Has memory: Contains time delay x(t-...)'}
    
    else:  # discrete
        # Check for delayed input x[n-...]
        if re.search(r'x\[n\s*-', eq):
            return {'status': 'no', 'explanation': 'Has memory: Contains delay x[n-k]'}
        
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
        
        # Local dict for parsing
        local_dict = {
            't': t, 'n': n, 'x': x_func,
            'u': Heaviside, 'd': DiracDelta,
            'sin': symbols('sin'), 'cos': symbols('cos'), 'exp': symbols('exp'),
            'Heaviside': Heaviside, 'DiracDelta': DiracDelta
        }
        transformations = (standard_transformations + (implicit_multiplication_application,))
        
        # Parse system equation
        # Pre-process: handle u(t) -> Heaviside(t), etc if string replace needed
        # But here we rely on standard parsing
        clean_eq = eq.replace('^', '**').replace('[', '(').replace(']', ')')
        expr = parse_expr(clean_eq, local_dict=local_dict, transformations=transformations)
        
        # Substitution Logic
        # We need to replace x(arg) with DiracDelta(arg)
        # Using .replace(Function, Substitution)
        
        if domain == 'continuous':
            # Lambda to replace x(args) with DiracDelta(args)
            def sub_impl(*args):
                if not args: return DiracDelta(t)
                return DiracDelta(args[0])
            
            h_expr = expr.replace(x_func, sub_impl)
        else:
             # Lambda to replace x[args] -> DiracDelta(args)
            def sub_impl(*args):
                if not args: return DiracDelta(n)
                return DiracDelta(args[0])
            
            h_expr = expr.replace(x_func, sub_impl)
            
        return h_expr
    except Exception as e:
        print(f"Error calculating impulse response: {e}")
        return None

def check_stability_bibo(h_expr, domain: str):
    """
    Checks BIBO stability by integrating/summing absolute impulse response.
    Stable if Integral |h(t)| dt < infinity
    """
    if h_expr is None:
         return {'status': 'unknown', 'explanation': 'Could not calculate impulse response to check stability'}
         
    try:
        if domain == 'continuous':
            # Heuristic: DiracDelta is stable
            if h_expr.has(DiracDelta) and not h_expr.has(Integral) and not h_expr.has(Heaviside):
                return {'status': 'yes', 'explanation': 'Stable: Impulse response is a Dirac Delta (finite energy)'}

            # Integral |-oo to oo| |h(t)| dt
            # Simplify first to assist SymPy
            abs_h = simplify(Abs(h_expr))
            stability_integral = integrate(abs_h, (t, -oo, oo))
            
            # Further simplify the result
            stability_integral = simplify(stability_integral)
            
            if stability_integral.is_finite:
                 return {'status': 'yes', 'explanation': 'Stable: Integral of |h(t)| is finite (BIBO)'}
            
            if stability_integral == oo:
                 return {'status': 'no', 'explanation': 'Unstable: Integral of |h(t)| is infinite'}
            else:
                 # Sometimes integration fails or returns condition
                 return {'status': 'unknown', 'explanation': 'Stability check inconclusive (complex integral)'}
                 
        else:
            # Sum |-oo to oo| |h[n]|
            abs_h = Abs(h_expr)
            # SymPy summation can be tricky for infinite generic sums
            # Let's try direct summation
            stability_sum = Sum(abs_h, (n, -oo, oo)).doit()
            
            if stability_sum.is_finite:
                 return {'status': 'yes', 'explanation': 'Stable: Sum of |h[n]| is finite (BIBO)'}
            elif stability_sum == oo:
                 return {'status': 'no', 'explanation': 'Unstable: Sum of |h[n]| is infinite'}
            else:
                 return {'status': 'unknown', 'explanation': 'Stability check inconclusive'}
                 
    except Exception as e:
         print(f"Stability check error: {e}")
         return {'status': 'unknown', 'explanation': 'Stability analysis failed'}

def check_stability(eq: str, domain: str):
    # Backward compatibility wrapper if needed, 
    # but we will call check_stability_bibo directly in analyze_system if we calculate h(t) there.
    # For now, let's keep the heuristic as fallback or replace it?
    # User specifically requested integral method.
    
    # Let's calculate h(t) here temporarily? 
    # Better: update analyze_system to pass h_expr or do it all there.
    # To minimize refactor risk, I will implement a Hybrid approach.
    
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
    
    return {'status': 'unknown', 'explanation': 'Invertibility depends on specific system structure'}
