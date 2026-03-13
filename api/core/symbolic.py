from api.core.utils import t, n, s, z, w, k, get_shared_modules_dict, clean_output_str, VisualDirac
import numpy as np
import sympy
import re
import logging
import traceback
from sympy import (apart, fraction, solve, simplify, collect, Add, Piecewise,
                   Heaviside, DiracDelta, exp, sin, cos, tan, pi, I, oo, sympify, 
                   lambdify, integrate, laplace_transform, fourier_transform, 
                   inverse_laplace_transform, inverse_fourier_transform, Abs, arg, 
                   fourier_series, Integral, Sum, sinc, Max, Min, sinh, cosh, tanh, 
                   asin, acos, atan, log, KroneckerDelta, latex, symbols, Poly, factorial)
from sympy.parsing.sympy_parser import parse_expr, standard_transformations, implicit_multiplication_application

# Setup logger
logger = logging.getLogger(__name__)

# Define custom symbols and functions for parsing
# 'j' is often used in engineering for sqrt(-1)
j = I

def parse_signal(expr_str: str, domain: str = 'continuous'):
    """
    Parses a user input string into a SymPy expression.
    Handles 'u(t)', 'd(t)' substitutions to SymPy equivalents.
    Handles |expr| as Abs(expr) for absolute value notation.
    """
    # Pre-processing: Convert |expr| to Abs(expr)
    # Handle nested cases by replacing innermost first
    
    def convert_abs_notation(s):
        """Convert |expr| to Abs(expr), handling nested cases."""
        max_iterations = 10  # Prevent infinite loops
        iteration = 0
        
        while '|' in s and iteration < max_iterations:
            # Find innermost |expr| (no nested | inside)
            # Pattern: | followed by non-| chars, followed by |
            match = re.search(r'\|([^|]+)\|', s)
            if not match:
                # No valid pair found, break
                break
            
            # Replace with Abs(...)
            s = s[:match.start()] + f'Abs({match.group(1)})' + s[match.end():]
            iteration += 1
        
        return s
    
    expr_str = convert_abs_notation(expr_str)
    
    # Pre-processing: Convert ^ to ** (engineering/math notation for exponentiation)
    # Must be done before any other substitutions to avoid XOR interpretation
    expr_str = expr_str.replace('^', '**')
    
    # Pre-processing for standard engineering notation
    # Replace u(t) with Heaviside(t)
    # Replace d(t) with DiracDelta(t)
    # Handle both () and [] for discrete/continuous convenience
    
    def replace_engineering_aliases(source: str, alias: str, target: str) -> str:
        pattern = rf'\b{alias}\s*([\(\[])\s*([^\)\]]+?)\s*([\)\]])'
        return re.sub(pattern, lambda match: f'{target}({match.group(2)})', source)

    # Normalize engineering aliases while preserving the enclosed argument.
    clean_expr = replace_engineering_aliases(expr_str, 'u', 'Heaviside')
    clean_expr = replace_engineering_aliases(clean_expr, 'd', 'DiracDelta')
    clean_expr = replace_engineering_aliases(clean_expr, 'δ', 'DiracDelta')
    
    # Normalize brackets for discrete compatibility Only for function calls like x[n] -> x(n)
    # This prevents breaking list definitions if they exist
    clean_expr = re.sub(r'([a-zA-Z0-9_])\s*\[([^\]]*)\]', r'\1(\2)', clean_expr)
    # clean_expr = clean_expr.replace('[', '(').replace(']', ')') # OLD UNSAFE
    
    # Replace j or J or i or I that are not part of other words
    clean_expr = re.sub(r'\b[jJiI]\b', 'I', clean_expr)

    # Custom context
    local_dict = {
        't': t, 'n': n, 's': s, 'z': z, 'w': w, 'k': k,
        'j': I, 'exp': exp, 'sin': sin, 'cos': cos, 'tan': tan, 'pi': pi, 'e': sympy.E,
        'Heaviside': Heaviside, 'DiracDelta': DiracDelta,
        'Abs': Abs, 'arg': arg, 'sqrt': sympify('sqrt'), 'sign': sympify('sign'),
        'u': Heaviside, 'd': DiracDelta, # Aliases for direct usage if missed by replace
        'I': I, 'sinc': sinc, 'Max': Max, 'Min': Min,
        'sinh': sinh, 'cosh': cosh, 'tanh': tanh,
        'asin': asin, 'acos': acos, 'atan': atan,
        'ln': log, 'log': log
    }
    
    # Add pulse definitions
    # rect(t) = 1 if |t| < 0.5 else 0
    # tri(t) = max(0, 1 - |t|)
    # We can inject these as lambda functions or expressions
    local_dict['rect'] = lambda x: Heaviside(x + 1/2) * Heaviside(1/2 - x)
    local_dict['tri'] = lambda x: Max(0, 1 - Abs(x))
    
    transformations = (standard_transformations + (implicit_multiplication_application,))
    
    try:
        expr = parse_expr(clean_expr, local_dict=local_dict, transformations=transformations)
        return expr
    except Exception as e:
        raise ValueError(f"Failed to parse expression: {str(e)}")

# ... (skip generate_plot_data, compute_laplace, compute_fourier) ...

def compute_z(expr_str: str):
    """Computes Z-transform: x[n] -> X(z) using Sum(x[n]*z**-n)"""
    try:
        expr = parse_signal(expr_str, 'discrete')
        from sympy import summation
        # Bilateral Z-transform: sum x[n] * z**-n for n from -oo to oo
        # Many common signals are causal (u[n]), so we try to evaluate the sum
        X = summation(expr * z**(-n), (n, -oo, oo))
        
        from sympy import latex
        return latex(X).replace('**', '^').replace('I', 'j')
    except Exception as e:
        return f"Could not compute Z-Transform: {str(e)}"

def compute_inverse_z(expr_str: str):
    """
    Computes Inverse Z-transform: X(z) -> x[n]
    Uses residue method or transform pairs lookup.
    """
    try:
        expr = parse_signal(expr_str, 'discrete')
        
        # 1. Expand using partial fractions
        try:
            expanded = apart(expr, z)
        except:
            expanded = expr

        def invert_term(term):
            """
            Inverts a single rational term of X(z).
            Handles K / (1 - a*z^-1) which is (K * z) / (z - a)
            And K / (z - a)^m
            """
            num, den = fraction(term)
            poles = solve(den, z)
            
            # Case 1: K * z / (z - a) -> K * a^n * u[n]
            if len(poles) == 1:
                a = poles[0]
                # Try to see if it matches C * z / (z - a)
                C = simplify(term * (z - a) / z)
                if not C.has(z):
                    return C * a**n * Heaviside(n)
                
                # Case 2: K / (z - a) -> K * a^(n-1) * u[n-1]
                C2 = simplify(term * (z - a))
                if not C2.has(z):
                    return C2 * a**(n-1) * Heaviside(n-1)
                
                # Case 3: K * z / (z - a)^m (Repeated poles)
                m = den.as_poly(z).degree()
                if m >= 2:
                    # Heuristic: C * z / (z-a)^2 -> C * n * a^(n-1) * u[n]
                    C3 = simplify(term * (z - a)**2 / z)
                    if not C3.has(z):
                        return C3 * n * a**(n-1) * Heaviside(n)
                    
                    # Heuristic: C / (z-a)^2 -> C * (n-1) * a^(n-2) * u[n-1]
                    C4 = simplify(term * (z - a)**2)
                    if not C4.has(z):
                         return C4 * (n-1) * a**(n-2) * Heaviside(n-1)
            
            # Fallback for simple delays: z^-k -> delta[n-k]
            # Check if term is of form C * z**k
            if term.is_Pow and term.base == z:
                 # z**-k
                 exponent = term.exp
                 if exponent.is_integer:
                     return KroneckerDelta(n, -exponent)
            
            # Check if term is just z
            if term == z:
                return KroneckerDelta(n, -1) # z^1 -> delta[n+1]? standard z trans is sum x[n]z^-n. So delta[n+1] -> z.

            return None

        inv_expr = 0
        failed = False
        
        if isinstance(expanded, Add):
            for arg in expanded.args:
                res = invert_term(arg)
                if res is not None:
                    inv_expr += res
                else:
                    failed = True
                    break
        else:
            res = invert_term(expanded)
            if res is not None:
                inv_expr = res
            else:
                failed = True

        # Second Strategy: Partial Fraction on X(z)/z
        if failed or inv_expr == 0:
             try:
                 expanded_div_z = apart(expr/z, z)
                 inv_expr_2 = 0
                 failed_2 = False
                 
                 def invert_term_div_z(term):
                     # term is K / (z-a)^m
                     # corresponding to X(z) part K*z / (z-a)^m
                     n_t, d_t = fraction(term)
                     poles = solve(d_t, z)
                     if len(poles) == 1:
                         a = poles[0]
                         m = d_t.as_poly(z).degree()
                         K = simplify(term * (z-a)**m)
                         
                         if m == 1:
                             # K/(z-a) -> K*z/(z-a) -> K*a^n * u[n]
                             return K * a**n * Heaviside(n)
                         elif m == 2:
                             # K/(z-a)^2 -> K*z/(z-a)^2 -> K * n * a^(n-1) * u[n]
                             return K * n * a**(n-1) * Heaviside(n)
                     return None

                 if isinstance(expanded_div_z, Add):
                     for arg in expanded_div_z.args:
                         r = invert_term_div_z(arg)
                         if r is not None: inv_expr_2 += r
                         else: failed_2 = True; break
                 else:
                     inv_expr_2 = invert_term_div_z(expanded_div_z)
                     if inv_expr_2 is None: failed_2 = True
                     
                 if not failed_2:
                     inv_expr = inv_expr_2
                     failed = False
             except:
                 pass

        if failed:
            return "Inverse Z-Transform: Form not yet supported symbolically.", None
        
        return clean_output_str(latex(inv_expr), domain='discrete').replace('\\theta', 'u'), inv_expr
    except Exception as e:
        # 2. Handle simple delays/advances that SymPy might struggle with directly
        # Case: z**(-m) -> delta[n-m]
        delay_match = re.match(r'^z\^?\(?(\-?\d+)\)?$', expr_str.strip())
        if delay_match:
            shift = int(delay_match.group(1))
            res_str = f"\\delta[n{'+' if shift >= 0 else ''}{shift}]"
            return res_str, None
            
        return f"Inverse Z-Transform Failed: {str(e)}", None

def compute_inverse_fourier(expr_str: str, domain: str = 'continuous'):
    """
    Computes inverse Fourier transform (CTFT or DTFT).
    For continuous: X(jω) -> x(t)
    For discrete: X(e^jω) -> x[n]
    Uses transform pair lookup for common rational functions.
    """
    try:
        # Replace j/i/I with sympy I
        clean_expr = expr_str
        clean_expr = re.sub(r'\bI\b', 'I', clean_expr)
        clean_expr = re.sub(r'\bi\b', 'I', clean_expr)
        clean_expr = re.sub(r'\bJ\b', 'I', clean_expr)
        clean_expr = re.sub(r'\bj\b', 'I', clean_expr)
        
        if domain == 'continuous':
             expr = parse_signal(clean_expr, 'continuous')
        else:
             expr = parse_signal(clean_expr, 'discrete')
        
        logger.debug(f"[compute_inverse_fourier] Domain: {domain}")
        logger.debug(f"[compute_inverse_fourier] Input: {expr_str}")
        logger.debug(f"[compute_inverse_fourier] Parsed: {expr}")
        
        if domain == 'discrete':
            # DTFT Inverse: X(e^jω) -> x[n]
            # Common form: 1/(1 - a*e^(-jω)) <-> a^n * u[n] for |a| < 1
            # In SymPy: exp(I*w) or exp(-I*w)
            
            # Get Numerator and Denominator
            numer, denom = fraction(expr)
            denom_expanded = simplify(denom)
            
            # Get coefficient of exp(-I*w)
            exp_neg = exp(-I*w)
            exp_pos = exp(I*w)
            
            # Substitute exp(-Iw) with a dummy variable to find its coefficient
            v_dummy = symbols('v_dummy')
            denom_v = denom_expanded.subs(exp_neg, v_dummy)
            coeff_neg = denom_v.coeff(v_dummy, 1) if not denom_v.has(exp_pos) else 0
            
            # Similarly for exp(Iw)
            denom_v_pos = denom_expanded.subs(exp_pos, v_dummy)
            coeff_pos = denom_v_pos.coeff(v_dummy, 1) if not denom_v_pos.has(exp_neg) else 0
            
            
            const = denom_expanded.subs([(exp_neg, 0), (exp_pos, 0)])
            
            logger.debug(f"[compute_inverse_fourier] Coeff of exp(-Iw): {coeff_neg}, Coeff of exp(Iw): {coeff_pos}, Const: {const}")
            
            # Standard form: 1 / (1 - a*exp(-I*w)) where const=1, coeff_neg=-a
            if coeff_neg != 0 and coeff_pos == 0:
                a = -coeff_neg / const
                K = numer / const
                logger.debug(f"[compute_inverse_fourier] Detected a = {a}")
                
                # Transform pair: K / (1 - a*exp(-I*w)) <-> K * a^n * u[n]
                f = K * a**n * Heaviside(n)
                logger.debug(f"[compute_inverse_fourier] Using DTFT pair: {f}")
                
                return clean_output_str(latex(f), domain), f
            else:
                logger.debug(f"[compute_inverse_fourier] Not standard DTFT form, trying numerical/general approach")
                return f"Inverse DTFT: Complex form not yet supported. Use Z-transform for rational forms.", None
        else:  # Continuous
            # CTFT Inverse: X(jω) -> x(t)
            # Standard form: K/(I*w + a) <-> K*e^(-at)*u(t) for a > 0
            
            # Mask 'I*w' as a single variable 'jw' to use apart()
            jw = symbols('jw')
            # Simplify and combine before substitution handles some nested forms
            expr_for_apart = simplify(expr)
            expr_jw = expr_for_apart.subs(I*w, jw)
            if not expr_jw.has(jw) and expr_for_apart.has(w):
                 expr_jw = expr_for_apart.subs(w, jw/I)
            try:
                expanded = apart(expr_jw, jw)
                
                def invert_ct_term(term):
                    n_t, d_t = fraction(term)
                    poles = solve(d_t, jw)
                    if len(poles) == 1:
                        p = poles[0]
                        # K / (jw - p) -> K * exp(p*t) * u(t) if Re(p) < 0
                        K = simplify(term * (jw - p))
                        if not K.has(jw):
                            return K * exp(p * t) * Heaviside(t)
                    
                    # Case: K / (jw - p)^n -> K * t^(n-1)/(n-1)! * exp(p*t) * u(t)
                    # We need to find the degree of (jw - p) in the denominator
                    from sympy import Poly, factorial
                    try:
                        p_obj = Poly(d_t, jw)
                        if p_obj.degree() > 1 and len(poles) == 1:
                            p = poles[0]
                            n_val = p_obj.degree()
                            K = n_t / p_obj.LC()
                            return K * (t**(n_val-1) / factorial(n_val-1)) * exp(p*t) * Heaviside(t)
                    except:
                        pass
                    return None
                
                f = 0
                failed = False
                
                if isinstance(expanded, Add):
                    for arg in expanded.args:
                        term_res = invert_ct_term(arg)
                        if term_res is not None:
                            f += term_res
                        else:
                            failed = True
                else:
                    f = invert_ct_term(expanded)
                    if f is None: failed = True
                
                if failed or f == 0:
                    logger.debug(f"[compute_inverse_fourier] Partial fractions approach incomplete, trying SymPy")
                    # Try direct inverse if it's a simple rational form of w
                    f = inverse_fourier_transform(expr.subs(w, 2*pi*symbols('f')), symbols('f'), t)
            except Exception as e_apart:
                logger.debug(f"[compute_inverse_fourier] apart(jw) failed: {e_apart}, trying SymPy")
                f = inverse_fourier_transform(expr.subs(w, 2*pi*symbols('f')), symbols('f'), t)
        
        # Simplify and format
        f = simplify(f)
        return clean_output_str(latex(f), domain), f
        
    except Exception as e:
        logger.error(f"[compute_inverse_fourier] ERROR: {e}")
        logger.error(traceback.format_exc())
        return f"Inverse Fourier Failed: {str(e)}", None


def evaluate_frequency_response(expr_str: str, w_min: float = -10, w_max: float = 10, num_points: int = 400, type: str = 'fourier'):
    """
    Evaluates X(w) for plotting frequency domain expressions.
    Consolidated to use parse_signal for consistent alias/imaginary unit handling.
    """
    try:
        # Determine domain for parsing
        parse_domain = 'continuous'
        if 'z' in expr_str.lower():
            parse_domain = 'discrete'
            
        expr = parse_signal(expr_str, parse_domain)
        
        # Determine variable to evaluate against
        var = w
        if expr.has(s): var = s
        elif expr.has(z): var = z
        elif expr.has(w): var = w
        elif expr.has(n): var = n

        # Lambdify for numerical evaluation using shared modules
        m_dict = get_shared_modules_dict(parse_domain)
        f_num = lambdify(var, expr, modules=m_dict)
        w_vals = np.linspace(w_min, w_max, num_points)
        
        try:
            with np.errstate(divide='ignore', invalid='ignore'):
                vals = f_num(w_vals)
                if np.isscalar(vals):
                    vals = np.full_like(w_vals, vals, dtype=complex)
                vals = np.array(vals, dtype=complex)
                vals = np.nan_to_num(vals)
        except:
            # Fallback for complex issues or singularities: eval one by one (slower but safer)
            try:
                # Create a robust checked function
                def safe_eval(v):
                    try:
                        return complex(expr.subs(var, v).evalf())
                    except:
                        return 0j # safe eval failure
                
                vec_eval = np.vectorize(safe_eval)
                vals = vec_eval(w_vals)
            except Exception as e:
                 logger.error(f"Evaluating frequency response fallback failed: {e}")
                 vals = np.zeros_like(w_vals, dtype=complex) # last resort

        mag = np.abs(vals)
        phase = np.angle(vals)
        
        return {
            "magnitude": {"x": w_vals.tolist(), "y": mag.tolist()},
            "phase": {"x": w_vals.tolist(), "y": phase.tolist()}
        }
        
    except Exception as e:
        logger.error(f"[evaluate_frequency_response] Error: {e}")
        return {"magnitude": {"x": [], "y": []}, "phase": {"x": [], "y": []}}

def generate_plot_data(expr_str_or_obj, t_min: float = -5, t_max: float = 5, num_points: int = 500, domain: str = 'continuous'):
    """
    Generates x, y arrays for plotting.
    """
    try:
        if isinstance(expr_str_or_obj, str):
            # Preprocess: convert formatted notation back to parseable format
            expr_str = expr_str_or_obj.replace('^', '**')
            expr = parse_signal(expr_str, domain)
        else:
            expr = expr_str_or_obj
        
        # Visual Proxy for DiracDelta: Replace with VisualDirac for plotting
        from sympy import Function
        VisualDirac = Function('VisualDirac')
        expr_visual = expr.replace(DiracDelta, VisualDirac)
        
        # Use shared modules dict
        modules_dict = get_shared_modules_dict(domain)

        if domain == 'continuous':
            # Create lambda function
            f = lambdify(t, expr_visual, modules=modules_dict)
            # Generate time vector
            t_vals = np.linspace(t_min, t_max, num_points)
            try:
                y_vals = f(t_vals)
                # Handle constant output
                if np.isscalar(y_vals):
                    y_vals = np.full_like(t_vals, y_vals)
            except Exception:
                # Fallback for complex issues or singularities: eval one by one (slower but safer)
                y_vals = np.zeros_like(t_vals)
            
            return t_vals.tolist(), np.real(y_vals).tolist() # Return real part for standard plotting
            
        elif domain == 'discrete':
            f = lambdify(n, expr_visual, modules=modules_dict)
            # Integer samples only for discrete signals
            n_vals = np.arange(int(t_min), int(t_max) + 1)
            try:
                y_vals = f(n_vals)
                if np.isscalar(y_vals):
                    y_vals = np.full_like(n_vals, y_vals, dtype=float)
            except Exception:
                y_vals = np.zeros_like(n_vals, dtype=float)
                
            return n_vals.tolist(), np.real(y_vals).tolist()
            
    except Exception as outer_e:
        logger.error(f"[generate_plot_data] Error: {outer_e}")
        return [], []

def compute_laplace(expr_str: str):
    expr = parse_signal(expr_str, 'continuous')
    # laplace_transform returns (F, a, cond)
    try:
        F, a, cond = laplace_transform(expr, t, s, noconds=False)
        return latex(F)
    except Exception as e:
        return f"Could not compute Laplace Transform: {str(e)}"

def compute_fourier(expr_str: str):
    expr = parse_signal(expr_str, 'continuous')
    from sympy import latex
    try:
        # Engineering standard: X(jw) = int x(t)e^(-jwt) dt
        # SymPy fourier_transform(f, t, w) uses e^(-2pi*i*w*t)
        # So we use w/(2*pi) for the frequency parameter
        F = fourier_transform(expr, t, w / (2 * pi))
        return latex(F)
    except Exception as e:
        return f"Could not compute Fourier Transform: {str(e)}"


def compute_inverse_laplace(expr_str: str):
    try:
        from sympy import inverse_laplace_transform, symbols, Function, latex, sympify
        
        # Parse the expression
        expr = parse_signal(expr_str, 'continuous')
        
        # inverse_laplace_transform(F, s, t)
        f = inverse_laplace_transform(expr, s, t)
        
        # Standardize output notation (\theta -> u)
        res_latex = clean_output_str(latex(f), domain='continuous').replace('\\theta', 'u')
        return res_latex, f
    except Exception as e:
        return f"Inverse Laplace Failed: {str(e)}", None


def compute_spectrum(expr_str: str, w_min: float = -10, w_max: float = 10, num_points: int = 500, domain: str = 'continuous'):
    """
    Computes Magnitude and Phase spectrum by directly evaluating X(jω).
    Much simpler than symbolic integration - just substitute ω values!
    """
    try:
        # For CTFT: We already have X(jω) from the Fourier transform
        # We just need to evaluate it at different ω values
        
        # First, get the symbolic Fourier transform
        expr = parse_signal(expr_str, domain)
        
        if domain == 'continuous':
            # Get X(jω) symbolically
            try:
                # Engineering standard: X(jw) = int x(t)e^(-jwt) dt
                # SymPy fourier_transform(f, t, w) uses e^(-2pi*i*w*t)
                # So we use w/(2*pi) to match the angular frequency w
                X_jw = fourier_transform(expr, t, w / (2 * pi))
            except:
                # If symbolic transform fails, try direct integration
                X_jw = integrate(expr * exp(-I * w * t), (t, -oo, oo))
        else:
            # DTFT: X(e^jω) = Σ x[n]e^(-jωn)
            # This is the Z-transform evaluated on the unit circle: z = e^(jω)
            try:
                # Try symbolic sum first
                X_jw = Sum(expr * exp(-I * w * n), (n, -oo, oo)).doit()
                
                # If symbolic sum doesn't simplify, try Z-transform approach
                if isinstance(X_jw, Sum):
                    # Get Z-transform symbolically, then substitute z = e^(jω)
                    from sympy import summation
                    # For common signals like u[n], (a^n)*u[n], we can use Z-transform tables
                    # Then substitute z = exp(I*w)
                    
                    # Try direct numerical evaluation instead
                    # For finite-support or exponentially decaying signals
                    # Evaluate sum numerically for n = -50 to 50 (practical range)
                    logger.debug("DTFT: Using numerical summation approach")
                    
                    # Create a lambda function for x[n]
                    x_n_func = lambdify(n, expr, modules=['numpy'])
                    
                    # For each ω, compute the sum numerically
                    w_vals = np.linspace(w_min, w_max, num_points)
                    X_values = np.zeros(len(w_vals), dtype=complex)
                    
                    n_range = np.arange(-200, 201)  # Larger range for better frequency resolution
                    
                    for i, omega in enumerate(w_vals):
                        x_vals = x_n_func(n_range)
                        if np.isscalar(x_vals):
                            x_vals = np.full_like(n_range, x_vals, dtype=float)
                        
                        # X(e^jω) = Σ x[n] * e^(-jωn)
                        X_values[i] = np.sum(x_vals * np.exp(-1j * omega * n_range))
                    
                    mag_vals = np.abs(X_values)
                    phase_vals = np.angle(X_values)
                    
                    return {
                        "magnitude": {"x": w_vals.tolist(), "y": mag_vals.tolist()},
                        "phase": {"x": w_vals.tolist(), "y": phase_vals.tolist()}
                    }
                    
            except Exception as dtft_error:
                logger.debug(f"DTFT computation failed: {dtft_error}")
                return None
        
        # Now simply evaluate X_jw at different ω values
        # Substitute w with actual numbers
        w_vals = np.linspace(w_min, w_max, num_points)
        
        # Lambdify for fast numerical evaluation
        try:
            X_func = lambdify(w, X_jw, modules=['numpy', {'I': 1j}])
            
            # Evaluate at all ω points
            X_values = X_func(w_vals)
            
            # Handle scalar output
            if np.isscalar(X_values):
                X_values = np.full_like(w_vals, X_values, dtype=complex)
            
            # Convert to complex array
            X_values = np.array(X_values, dtype=complex)
            
            # Compute magnitude and phase
            mag_vals = np.abs(X_values)
            phase_vals = np.angle(X_values)
            
            return {
                "magnitude": {"x": w_vals.tolist(), "y": mag_vals.tolist()},
                "phase": {"x": w_vals.tolist(), "y": phase_vals.tolist()}
            }
        except Exception as eval_error:
            logger.error(f"Evaluation failed: {eval_error}")
            return None
            
    except Exception as e:
        logger.error(f"Spectrum Analysis Failed: {e}")
        logger.error(traceback.format_exc())
        return None

def compute_fourier_series_coeffs(expr_str: str, period_T: float = 6.28, num_coeffs: int = 5):
    """
    Computes Fourier Series coefficients a_k for k = -N to N.
    """
    try:
        expr = parse_signal(expr_str, 'continuous')
        # T is period. SymPy fourier_series expects limits.
        # Assume symmetric interval [-T/2, T/2]
        load = period_T / 2
        
        fs = fourier_series(expr, (t, -load, load))
        
        coeffs = []
        indices = range(-num_coeffs, num_coeffs + 1)
        
        for k_i in indices:
            # This is an approximation/truncation extraction method
            w0 = 2*pi/period_T
            term = expr * exp(-I * k_i * w0 * t)
            ak = (1/period_T) * integrate(term, (t, -load, load))
            ak_num = complex(ak.evalf())
            coeffs.append({
                "k": k_i, 
                "magnitude": abs(ak_num),
                "phase": float(arg(ak_num)),
                "value_str": str(ak).replace('**', '^').replace('I', 'j')
            }) 
            
        return coeffs
    except Exception as e:
        logger.error(f"FS Calculation Failed: {e}")
        return []

def parse_transfer_function(expr_str: str, variable: str = 's'):
    """
    Consolidated transfer function parser. Returns poles/zeros.
    """
    return extract_poles_zeros(expr_str, variable)

# --- Convolution Logic (Ported from convolution.py) ---

def estimate_support(fn, lo=-20, hi=20, N=1000, tol=1e-3):
    grid = np.linspace(lo, hi, N)
    try:
        vals = fn(grid)
        if np.isscalar(vals): vals = np.full_like(grid, vals)
        idx = np.where(np.abs(vals) > tol)[0]
        if idx.size == 0: return None
        return grid[idx[0]], grid[idx[-1]]
    except:
        return None

def estimate_support_discrete(fn, lo=-20, hi=20):
    grid = np.arange(lo, hi + 1)
    try:
        vals = fn(grid)
        if np.isscalar(vals): vals = np.full_like(grid, vals)
        idx = np.where(np.abs(vals) > 1e-3)[0]
        if idx.size == 0: return None
        return grid[idx[0]], grid[idx[-1]]
    except:
        return None

def compute_convolution(x_str: str, h_str: str, domain: str = 'continuous'):
    """
    Computes convolution y(t) = x(t) * h(t) [or y[n] * h[n]] and generates animation frames.
    Handles distributions like DiracDelta and KroneckerDelta via visual proxies.
    """
    try:
        # Define visual modules (same as generate_plot_data)
        from api.core.utils import VisualDirac
        
        modules_dict = [
            'numpy',
            {'Heaviside': lambda x: np.where(x >= 0, 1.0, 0.0),
             'DiracDelta': VisualDirac('continuous'),
             'VisualDirac': VisualDirac('continuous'),
             'KroneckerDelta': VisualDirac('discrete'),
             'rect': lambda x: np.where(np.abs(x) <= 0.5, 1.0, 0.0),
             'tri': lambda x: np.maximum(0, 1 - np.abs(x)),
             'sinc': np.sinc,
             'Max': np.maximum,
             'Min': np.minimum}
        ]

        if domain == 'continuous':
            x_expr = parse_signal(x_str, 'continuous')
            h_expr = parse_signal(h_str, 'continuous')
            
            # Use visual proxies for evaluating distributions
            # Create a single VisualDirac instance for continuous domain
            visual_dirac_continuous = VisualDirac('continuous')
            x_vis = x_expr.replace(DiracDelta, lambda x: visual_dirac_continuous(x))
            h_vis = h_expr.replace(DiracDelta, lambda x: visual_dirac_continuous(x))
            
            x_fn = lambdify(t, x_vis, modules=modules_dict)
            h_fn = lambdify(t, h_vis, modules=modules_dict)
            
            # Auto-range
            sx = estimate_support(x_fn)
            sh = estimate_support(h_fn)
            
            ax, bx = sx if sx else (-2, 2)
            ah, bh = sh if sh else (-2, 2)
            
            tau_min, tau_max = min(ax, ah) - 2, max(bx, bh) + 2
            t_min, t_max = (ax + ah) - 2, (bx + bh) + 2
            
            num_frames = 60
            num_tau = 400 # More points for smoother integration
            
            t_vals = np.linspace(t_min, t_max, num_frames)
            tau_vals = np.linspace(tau_min, tau_max, num_tau)
            
            try:
                X_tau = x_fn(tau_vals)
            except:
                X_tau = np.array([float(x_fn(v)) for v in tau_vals])
            if np.isscalar(X_tau): X_tau = np.full_like(tau_vals, X_tau)
            
            y_vals = []
            frames = []
            
            for ti in t_vals:
                try:
                    H_shifted = h_fn(ti - tau_vals)
                except:
                    H_shifted = np.array([float(h_fn(ti - v)) for v in tau_vals])
                if np.isscalar(H_shifted): H_shifted = np.full_like(tau_vals, H_shifted)
                
                # Numerical integration across NumPy versions.
                product = X_tau * H_shifted
                integrator = getattr(np, 'trapezoid', None) or getattr(np, 'trapz')
                val = integrator(product, tau_vals)
                y_vals.append(val)
                
                frames.append({
                    "t": float(ti),
                    "h_shifted": H_shifted.tolist(), 
                    "current_y_real": float(np.real(val)),
                    "current_y_imag": float(np.imag(val)),
                    "current_y": float(np.real(val)) # for compat
                })
                
            return {
                "t": t_vals.tolist(),
                "y": np.real(y_vals).tolist(),
                "tau": tau_vals.tolist(),
                "x_tau": np.real(X_tau).tolist(),
                "frames": frames
            }
            
        else: # Discrete
            x_expr = parse_signal(x_str, 'discrete')
            h_expr = parse_signal(h_str, 'discrete')
            
            # For discrete, use KroneckerDelta visual proxy
            visual_dirac_discrete = VisualDirac('discrete')
            x_vis = x_expr.replace(KroneckerDelta, lambda *args: visual_dirac_discrete(args[0] if args else 0))
            h_vis = h_expr.replace(KroneckerDelta, lambda *args: visual_dirac_discrete(args[0] if args else 0))
            
            x_fn = lambdify(n, x_vis, modules=modules_dict)
            h_fn = lambdify(n, h_vis, modules=modules_dict)

            sx = estimate_support_discrete(x_fn)
            sh = estimate_support_discrete(h_fn)

            ax, bx = sx if sx else (-5, 5)
            ah, bh = sh if sh else (-5, 5)
            
            k_min, k_max = min(ax, ah) - 5, max(bx, bh) + 5
            n_min, n_max = (ax + ah) - 5, (bx + bh) + 5
            
            n_vals = np.arange(n_min, n_max + 1)
            k_vals = np.arange(k_min, k_max + 1)
            
            try:
                X_k = x_fn(k_vals)
            except:
                X_k = np.array([float(x_fn(v)) for v in k_vals])
            if np.isscalar(X_k): X_k = np.full_like(k_vals, X_k)
            
            y_vals = []
            frames = []
            
            for ni in n_vals:
                try:
                    H_shifted = h_fn(ni - k_vals)
                except:
                    H_shifted = np.array([float(h_fn(ni - v)) for v in k_vals])
                if np.isscalar(H_shifted): H_shifted = np.full_like(k_vals, H_shifted)
                
                val = np.sum(X_k * H_shifted)
                y_vals.append(val)
                
                frames.append({
                    "t": float(ni), # use 't' key for generic frontend compat
                    "h_shifted": H_shifted.tolist(), 
                    "current_y_real": float(np.real(val)),
                    "current_y_imag": float(np.imag(val)),
                    "current_y": float(np.real(val))
                })
                
            return {
                "t": n_vals.tolist(),
                "y": np.real(y_vals).tolist(),
                "tau": k_vals.tolist(), # 'tau' for generic compat (actually k)
                "x_tau": np.real(X_k).tolist(),
                "frames": frames
            }

    except Exception as e:
        logger.error(f"Convolution Failed: {e}")
        logger.error(traceback.format_exc())
        return None



def extract_poles_zeros(expr_str: str, variable: str):
    """
    Parses H(s) or H(z) and extracts numerical poles and zeros.
    Returns:
        poles: list of {r, i} dicts
        zeros: list of {r, i} dicts
    """
    try:
        var_sym = symbols(variable)
        expr = parse_signal(expr_str, 'continuous') # reuse engineering parser
        if variable == 'z':
            # ensure z is the variable if we parsed with t/n
            expr = expr.subs(n, var_sym).subs(t, var_sym)
        elif variable == 's':
             expr = expr.subs(t, var_sym)

        
        # Simplify to rational form P/Q
        rational_expr = expr.simplify()
        
        numer, denom = rational_expr.as_numer_denom()
        
        # Find roots
        # Use roots() to get multiplicity for repeated poles/zeros
        from sympy import roots
        
        # Helper to get roots safely (fallback to solve if roots fails)
        def get_all_roots(poly_expr, sym):
            try:
                # Try roots()
                r_dict = roots(poly_expr, sym)
                # Flatten the dict: {root: count} -> [root, root, ...]
                all_roots = []
                for r, count in r_dict.items():
                    all_roots.extend([r] * count)
                return all_roots
            except:
                # Fallback to solve
                from sympy import solve
                return solve(poly_expr, sym)
        
        zeros_roots = get_all_roots(numer, var_sym)
        poles_roots = get_all_roots(denom, var_sym)
        
        # Helper to format complex number
        def format_root(r):
            val = complex(r) # evaluate to complex float
            return {"r": val.real, "i": val.imag}
            
        zeros_list = [format_root(z) for z in zeros_roots]
        poles_list = [format_root(p) for p in poles_roots]
        
        # Sort for consistency
        zeros_list.sort(key=lambda x: (x['r'], x['i']))
        poles_list.sort(key=lambda x: (x['r'], x['i']))
        
        return {"poles": poles_list, "zeros": zeros_list}
        
    except Exception as e:
        print(f"Error extracting poles/zeros: {e}")
        return {"error": str(e)}
