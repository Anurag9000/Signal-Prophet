from sympy import symbols, Heaviside, DiracDelta, exp, sin, cos, pi, I, oo, sympify, lambdify, integrate, laplace_transform, fourier_transform, inverse_laplace_transform, inverse_fourier_transform, Abs, arg, fourier_series, Integral, Sum
from sympy.parsing.sympy_parser import parse_expr, standard_transformations, implicit_multiplication_application
from sympy.abc import t, n, s, z, w
import numpy as np

# Define custom symbols and functions for parsing
# 'j' is often used in engineering for sqrt(-1)
j = I

def parse_signal(expr_str: str, domain: str = 'continuous'):
    """
    Parses a user input string into a SymPy expression.
    Handles 'u(t)', 'd(t)' substitutions to SymPy equivalents.
    """
    # Pre-processing for standard engineering notation
    # Replace u(t) with Heaviside(t)
    # Replace d(t) with DiracDelta(t)
    # Handle both () and [] for discrete/continuous convenience
    
    clean_expr = expr_str.replace('u(', 'Heaviside(').replace('u[', 'Heaviside(')
    clean_expr = clean_expr.replace('d(', 'DiracDelta(').replace('d[', 'DiracDelta(')
    clean_expr = clean_expr.replace('δ(', 'DiracDelta(').replace('δ[', 'DiracDelta(')
    clean_expr = clean_expr.replace(']', ')') # normalize brackets
    
    # Handle 'j' as imaginary unit 'I' IF it's likely being used as a number
    # Simple regex or replace 'j' with 'I' carefully? 
    # Safest is to just replace 'j' if it's not part of a word. 
    # But user might type "1+j*w". 
    # Let's simple replace 'j' and 'J' with 'I' but watch out for 'sin' 'adj' etc.
    # Given the context, we can check for word boundaries or assume users don't use variables starting with j.
    # Actually, simplest implementation for now:
    import re
    # Replace j or J that are not preceded by a letter (to avoid replacing 'adj' or 'obj')
    # and not followed by a letter (so we don't break 'jupiter')
    # Use simple replace for " j " "J" etc?
    # User requested "I interchangable with i or J or j"
    # We will assume 'j' is 'I' unless it's in a known function name.
    
    # Primitive approach for now:
    # 1. Replace known keywords to placeholders? No.
    # 2. Just do simple replacement of "j" -> "I" where safe?
    # Let's just blindly replace j with I and see if it breaks anything common. 'j' is rare in Python/SymPy func names used here.
    # 'conjugate' has j. 'adj' has j.
    # Let's replace only 'j' surrounded by non-alpha or start/end.
    clean_expr = re.sub(r'(?<![a-zA-Z])j(?![a-zA-Z])', 'I', clean_expr)
    clean_expr = re.sub(r'(?<![a-zA-Z])J(?![a-zA-Z])', 'I', clean_expr)
    
    # Also 'i' ? SymPy uses 'I'. Python uses '1j'.
    # If user types '3i', we want '3*I'.
    clean_expr = re.sub(r'(?<![a-zA-Z])i(?![a-zA-Z])', 'I', clean_expr)

    # Custom context
    local_dict = {
        't': t, 'n': n, 's': s, 'z': z, 'w': w,
        'j': I, 'exp': exp, 'sin': sin, 'cos': cos, 'pi': pi,
        'Heaviside': Heaviside, 'DiracDelta': DiracDelta,
        'Abs': Abs, 'arg': arg, 'sqrt': sympify('sqrt'), 'sign': sympify('sign'),
        'u': Heaviside, 'd': DiracDelta, # Aliases for direct usage if missed by replace
        'I': I
    }
    
    transformations = (standard_transformations + (implicit_multiplication_application,))
    
    try:
        expr = parse_expr(clean_expr, local_dict=local_dict, transformations=transformations)
        return expr
    except Exception as e:
        raise ValueError(f"Failed to parse expression: {str(e)}")

# ... (skip generate_plot_data, compute_laplace, compute_fourier) ...

def compute_inverse_fourier(expr_str: str, domain: str = 'continuous'):
    """
    Computes inverse Fourier transform (CTFT or DTFT).
    For continuous: X(jω) -> x(t)
    For discrete: X(e^jω) -> x[n]
    Uses transform pair lookup for common rational functions.
    """
    try:
        import re
        from sympy import fraction, solve, simplify, collect, Abs
        
        # Replace j/i/I with sympy I
        clean_expr = expr_str
        clean_expr = re.sub(r'\bI\b', 'I', clean_expr)
        clean_expr = re.sub(r'\bi\b', 'I', clean_expr)
        clean_expr = re.sub(r'\bJ\b', 'I', clean_expr)
        clean_expr = re.sub(r'\bj\b', 'I', clean_expr)
        
        expr = parse_signal(clean_expr, domain)
        
        print(f"[compute_inverse_fourier] Domain: {domain}")
        print(f"[compute_inverse_fourier] Input: {expr_str}")
        print(f"[compute_inverse_fourier] Parsed: {expr}")
        
        if domain == 'discrete':
            # DTFT Inverse: X(e^jω) -> x[n]
            # Common form: 1/(1 - a*e^(-jω)) <-> a^n * u[n] for |a| < 1
            # In SymPy: exp(I*w) or exp(-I*w)
            
            numer, denom = fraction(expr)
            print(f"[compute_inverse_fourier] Numerator: {numer}, Denominator: {denom}")
            
            # Check if denom has form: 1 - a*exp(-I*w) or similar
            # Expand and collect terms
            denom_expanded = denom.expand()
            
            # Try to match pattern: c0 + c1*exp(I*w) or c0 + c1*exp(-I*w)
            # For 1/(1 - 0.8*exp(-I*w)), denom = 1 - 0.8*exp(-I*w) = -0.8*exp(-I*w) + 1
            
            # Get coefficient of exp(-I*w)
            exp_neg = exp(-I*w)
            exp_pos = exp(I*w)
            
            coeff_neg = denom_expanded.coeff(exp_neg, 1)
            coeff_pos = denom_expanded.coeff(exp_pos, 1)
            const = denom_expanded.as_coeff_Add()[0] if not denom_expanded.has(exp_neg, exp_pos) else denom_expanded.subs([(exp_neg, 0), (exp_pos, 0)])
            
            print(f"[compute_inverse_fourier] Coeff of exp(-Iw): {coeff_neg}, Coeff of exp(Iw): {coeff_pos}, Const: {const}")
            
            # Standard form: 1 - a*exp(-I*w) where const=1, coeff_neg=-a
            if const == 1 and coeff_neg != 0 and coeff_pos == 0:
                a = -coeff_neg
                print(f"[compute_inverse_fourier] Detected a = {a}")
                
                # Check if |a| < 1 for stability
                if Abs(a) < 1:
                    # Transform pair: numer/(1 - a*exp(-I*w)) <-> numer * a^n * u[n]
                    f = numer * a**n * Heaviside(n)
                    print(f"[compute_inverse_fourier] Using DTFT pair: {f}")
                else:
                    print(f"[compute_inverse_fourier] |a| >= 1, unstable, trying SymPy")
                    f = inverse_fourier_transform(expr, w, n)
            else:
                print(f"[compute_inverse_fourier] Not standard DTFT form, trying SymPy")
                f = inverse_fourier_transform(expr, w, n)
                
        else:  # Continuous
            # CTFT Inverse: X(jω) -> x(t)
            # Standard form: K/(I*w + a) <-> K*e^(-at)*u(t) for a > 0
            
            numer, denom = fraction(expr)
            print(f"[compute_inverse_fourier] Numerator: {numer}, Denominator: {denom}")
            
            # Extract coefficients from denominator: I*w + a
            denom_expanded = denom.expand()
            denom_collected = collect(denom_expanded, w)
            
            coeff_w = denom_collected.coeff(w, 1)
            const_term = denom_collected.coeff(w, 0)
            
            print(f"[compute_inverse_fourier] Coeff of w: {coeff_w}, Constant: {const_term}")
            
            # For standard form I*w + a, we have coeff_w = I, const_term = a
            if coeff_w == I and const_term.is_real and const_term > 0:
                a = const_term
                # Transform pair: numer/(I*w + a) <-> numer * e^(-a*t) * u(t)
                f = numer * exp(-a * t) * Heaviside(t)
                print(f"[compute_inverse_fourier] Using CTFT pair with a={a}: {f}")
            else:
                # Try SymPy as fallback
                print(f"[compute_inverse_fourier] Not standard form, trying SymPy")
                f = inverse_fourier_transform(expr, w, t)
        
        # Simplify and format
        f = simplify(f)
        
        # Format for display - use proper notation based on domain
        if domain == 'discrete':
            # For discrete: Heaviside(n) -> u[n], keep ** for powers
            res_str = str(f).replace('Heaviside(n)', 'Heaviside[n]').replace('**', '^')
            res_str = res_str.replace('Heaviside', 'u').replace('DiracDelta', 'd')
        else:
            # For continuous: Heaviside(t) -> u(t)
            res_str = str(f).replace('**', '^').replace('Heaviside', 'u').replace('DiracDelta', 'd')
        
        print(f"[compute_inverse_fourier] Result: {res_str}")
        
        # IMPORTANT: For plotting, return the SymPy expression string that can be parsed
        # Convert back to parseable format
        plot_str = str(f)  # Keep SymPy format for parsing
        print(f"[compute_inverse_fourier] Plot string: {plot_str}")
        
        return res_str  # Return formatted for display
        
    except Exception as e:
        print(f"[compute_inverse_fourier] ERROR: {e}")
        import traceback
        traceback.print_exc()
        return f"Inverse Fourier Failed: {str(e)}"


def evaluate_frequency_response(expr_str: str, w_min: float = -10, w_max: float = 10, num_points: int = 400, type: str = 'fourier'):
    """
    Evaluates X(w) for plotting frequency domain expressions.
    Handles I, i, J, j all as imaginary unit.
    """
    try:
        import re
        
        # Replace imaginary unit symbols with 1j using word boundaries
        # This ensures we don't replace 'i' in 'sin' or 'pi'
        clean_expr = expr_str
        clean_expr = re.sub(r'\bI\b', '1j', clean_expr)
        clean_expr = re.sub(r'\bi\b', '1j', clean_expr) 
        clean_expr = re.sub(r'\bJ\b', '1j', clean_expr)
        clean_expr = re.sub(r'\bj\b', '1j', clean_expr)
        
        # Also handle I* and i* patterns (multiplication)
        clean_expr = re.sub(r'I\*', '1j*', clean_expr)
        clean_expr = re.sub(r'i\*', '1j*', clean_expr)
        clean_expr = re.sub(r'J\*', '1j*', clean_expr)
        clean_expr = re.sub(r'j\*', '1j*', clean_expr)
        
        print(f"[evaluate_frequency_response] Original: {expr_str}")
        print(f"[evaluate_frequency_response] Cleaned: {clean_expr}")
        
        # Generate w values
        w_vals = np.linspace(w_min, w_max, num_points)
        
        # Evaluate the expression for each w value
        results = []
        for w_val in w_vals:
            try:
                # Create namespace with w and common functions
                namespace = {
                    'w': w_val,
                    'exp': np.exp,
                    'sin': np.sin,
                    'cos': np.cos,
                    'tan': np.tan,
                    'pi': np.pi,
                    'sqrt': np.sqrt,
                    'abs': np.abs,
                    'log': np.log,
                    'e': np.e
                }
                
                # Evaluate the expression
                result = eval(clean_expr, {"__builtins__": {}}, namespace)
                results.append(complex(result))
            except Exception as e:
                # If evaluation fails, use 0
                results.append(0+0j)
        
        # Convert to numpy array
        vals = np.array(results, dtype=complex)
        
        # Extract magnitude and phase
        mag = np.abs(vals)
        phase = np.angle(vals)
        
        print(f"[evaluate_frequency_response] Evaluated {len(vals)} points")
        print(f"[evaluate_frequency_response] Sample mag values: {mag[:5]}")
        
        return {
            "magnitude": {"x": w_vals.tolist(), "y": mag.tolist()},
            "phase": {"x": w_vals.tolist(), "y": phase.tolist()}
        }
        
    except Exception as e:
        print(f"[evaluate_frequency_response] ERROR: {e}")
        import traceback
        traceback.print_exc()
        # Return empty arrays instead of None
        return {
            "magnitude": {"x": [], "y": []},
            "phase": {"x": [], "y": []}
        }

def generate_plot_data(expr_str: str, t_min: float = -10, t_max: float = 10, num_points: int = 1000, domain: str = 'continuous'):
    """
    Generates x, y arrays for plotting.
    Continuous: smooth curve with many points
    Discrete: integer samples only (stem plot)
    """
    # Preprocess: convert formatted notation back to parseable format
    # u[n] -> Heaviside(n), u(t) -> Heaviside(t)
    # ^ -> **
    expr_str = expr_str.replace('^', '**')
    
    print(f"[generate_plot_data] Input: {expr_str}, Domain: {domain}")
    
    expr = parse_signal(expr_str, domain)
    
    # Visual Proxy for DiracDelta
    # Replace DiracDelta(arg) with a finite value for plotting
    # We substitute DiracDelta with a custom function 'VisualDirac'
    # which returns 1.0 (or high value) when arg is close to 0, else 0.
    
    # Define symbolic wrapper first
    from sympy import Function
    VisualDirac = Function('VisualDirac')
    
    # Replace DiracDelta with VisualDirac in the expression
    # This handles DiracDelta(t), DiracDelta(t-2), 3*DiracDelta(t) etc.
    expr_visual = expr.replace(DiracDelta, VisualDirac)
    
    # Define numerical implementation for lambdify
    def visual_dirac_impl(val):
        # Return 1.0 if close to 0 (approximate visual impulse)
        # For discrete, we want exactly 1 at 0
        # For continuous, we want a spike.
        # Tolerance needs to be > step size (12/1000 = 0.012)
        tolerance = 0.05 if domain == 'continuous' else 0.1
        return np.where(np.abs(val) < tolerance, 1.0, 0.0)

    modules_dict = [{'VisualDirac': visual_dirac_impl}, 'numpy']

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
        n_vals = np.arange(int(t_min), int(t_max) + 1)  # e.g., -10, -9, ..., 0, ..., 10
        try:
            y_vals = f(n_vals)
            if np.isscalar(y_vals):
                y_vals = np.full_like(n_vals, y_vals, dtype=float)
        except Exception:
            y_vals = np.zeros_like(n_vals, dtype=float)
            
        return n_vals.tolist(), np.real(y_vals).tolist()

def compute_laplace(expr_str: str):
    expr = parse_signal(expr_str, 'continuous')
    # laplace_transform returns (F, a, cond)
    try:
        F, a, cond = laplace_transform(expr, t, s, noconds=False)
        return str(F).replace('**', '^') # simplified processing
    except Exception as e:
        return f"Could not compute Laplace Transform: {str(e)}"

def compute_fourier(expr_str: str):
    expr = parse_signal(expr_str, 'continuous')
    try:
        # SymPy fourier_transform definition might differ from engineering standard (2pi factors)
        # Using standard variable 'w' (omega)
        F = fourier_transform(expr, t, w)
        return str(F).replace('**', '^')
    except Exception as e:
        return f"Could not compute Fourier Transform: {str(e)}"

def compute_inverse_laplace(expr_str: str):
    try:
        # User inputs X(s). We need to parse X(s) not x(t).
        # We need a parse_transform helper or re-use parse_signal with 's' context
        # But parse_signal expects t/n primarily.
        # Let's trust parse_signal handles s if we pass relevant hints or just standard parse
        
        # Local dict needs 's' which is there.
        # We also need to ensure user uses 's'.
        expr = parse_signal(expr_str, 'continuous') # reuse parse logic, it has 's'
        
        # inverse_laplace_transform(F, s, t)
        f = inverse_laplace_transform(expr, s, t)
        return str(f).replace('**', '^').replace('Heaviside', 'u').replace('DiracDelta', 'd')
    except Exception as e:
        return f"Inverse Laplace Failed: {str(e)}"


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
                X_jw = fourier_transform(expr, t, w)
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
                    print("DTFT: Using numerical summation approach")
                    
                    # Create a lambda function for x[n]
                    x_n_func = lambdify(n, expr, modules=['numpy'])
                    
                    # For each ω, compute the sum numerically
                    w_vals = np.linspace(w_min, w_max, num_points)
                    X_values = np.zeros(len(w_vals), dtype=complex)
                    
                    n_range = np.arange(-50, 51)  # Practical range for summation
                    
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
                print(f"DTFT computation failed: {dtft_error}")
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
            print(f"Evaluation failed: {eval_error}")
            return None
            
    except Exception as e:
        print(f"Spectrum Analysis Failed: {e}")
        import traceback
        traceback.print_exc()
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
        
        for k in indices:
            # This is an approximation/truncation extraction method
            w0 = 2*pi/period_T
            term = expr * exp(-I * k * w0 * t)
            ak = (1/period_T) * integrate(term, (t, -load, load))
            coeffs.append({"k": k, "value": abs(complex(ak))}) 
            
        return coeffs
    except Exception as e:
        print(f"FS Calculation Failed: {e}")
        return []

def parse_transfer_function(expr_str: str, variable: str = 's'):
    """
    Parse a transfer function H(s) or H(z) and extract poles and zeros.
    Input: expression like "(s+1)/(s^2 + 2*s + 1)" or "(z-0.5)/(z^2 - 1.5*z + 0.5)"
    Returns: {"poles": [{"r": real, "i": imag}, ...], "zeros": [...]}
    """
    from sympy import solve, fraction, simplify
    
    try:
        # Replace j/J/i with I for imaginary unit
        import re
        clean_expr = re.sub(r'(?<![a-zA-Z])j(?![a-zA-Z])', 'I', expr_str)
        clean_expr = re.sub(r'(?<![a-zA-Z])J(?![a-zA-Z])', 'I', clean_expr)
        clean_expr = re.sub(r'(?<![a-zA-Z])i(?![a-zA-Z])', 'I', clean_expr)
        
        # Replace ^ with ** for exponentiation
        clean_expr = clean_expr.replace('^', '**')
        
        # Parse the expression
        var = symbols(variable)
        local_dict = {'s': s, 'z': z, 'I': I, 'exp': exp, 'sin': sin, 'cos': cos, 'pi': pi}
        
        expr = parse_expr(clean_expr, local_dict=local_dict)
        expr = simplify(expr)
        
        # Extract numerator and denominator
        numer, denom = fraction(expr)
        
        # Find zeros (roots of numerator)
        zero_roots = solve(numer, var)
        zeros = []
        for root in zero_roots:
            try:
                root_complex = complex(root)
                zeros.append({"r": float(root_complex.real), "i": float(root_complex.imag)})
            except:
                # Skip non-numeric roots
                pass
        
        # Find poles (roots of denominator)
        pole_roots = solve(denom, var)
        poles = []
        for root in pole_roots:
            try:
                root_complex = complex(root)
                poles.append({"r": float(root_complex.real), "i": float(root_complex.imag)})
            except:
                # Skip non-numeric roots
                pass
        
        return {
            "poles": poles,
            "zeros": zeros,
            "numerator": str(numer),
            "denominator": str(denom)
        }
    except Exception as e:
        print(f"Transfer function parsing failed: {e}")
        return {"error": str(e), "poles": [], "zeros": []}

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
    Computes convolution y(t) = x(t) * h(t) [or y[n] = x[n]*h[n]] and generates animation frames.
    """
    try:
        expr_dom = domain 
        
        if domain == 'continuous':
            x_expr = parse_signal(x_str, 'continuous')
            h_expr = parse_signal(h_str, 'continuous')
            
            x_fn = lambdify(t, x_expr, modules=['numpy'])
            h_fn = lambdify(t, h_expr, modules=['numpy'])
            
            # Auto-range
            sx = estimate_support(x_fn)
            sh = estimate_support(h_fn)
            
            ax, bx = sx if sx else (-2, 2)
            ah, bh = sh if sh else (-2, 2)
            
            # Padded ranges
            tau_min, tau_max = min(ax, ah) - 2, max(bx, bh) + 2
            t_min, t_max = (ax + ah) - 2, (bx + bh) + 2
            
            # Grids
            num_frames = 60 # Limit for performance
            num_tau = 200
            
            t_vals = np.linspace(t_min, t_max, num_frames)
            tau_vals = np.linspace(tau_min, tau_max, num_tau)
            
            # Precompute X(tau)
            X_tau = x_fn(tau_vals)
            if np.isscalar(X_tau): X_tau = np.full_like(tau_vals, X_tau)
            
            # Compute Y(t) and Frames
            y_vals = []
            frames = []
            
            for ti in t_vals:
                # h(t - tau)
                H_shifted = h_fn(ti - tau_vals)
                if np.isscalar(H_shifted): H_shifted = np.full_like(tau_vals, H_shifted)
                
                # Conv value at ti
                val = np.trapz(X_tau * H_shifted, tau_vals)
                y_vals.append(val)
                
                frames.append({
                    "t": float(ti),
                    "h_shifted": np.real(H_shifted).tolist(), 
                    "current_y": float(val)
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
            
            x_fn = lambdify(n, x_expr, modules=['numpy'])
            h_fn = lambdify(n, h_expr, modules=['numpy'])

            # Auto-range
            sx = estimate_support_discrete(x_fn)
            sh = estimate_support_discrete(h_fn)

            ax, bx = sx if sx else (-5, 5)
            ah, bh = sh if sh else (-5, 5)
            
            # Logic: Convolution support [ax+ah, bx+bh]
            k_min, k_max = min(ax, ah) - 5, max(bx, bh) + 5 # k is integration var usually k or m
            n_min, n_max = (ax + ah) - 5, (bx + bh) + 5
            
            n_vals = np.arange(n_min, n_max + 1)
            k_vals = np.arange(k_min, k_max + 1)
            
            X_k = x_fn(k_vals)
            if np.isscalar(X_k): X_k = np.full_like(k_vals, X_k)
            
            y_vals = []
            frames = []
            
            for ni in n_vals:
                # h[n - k]
                H_shifted = h_fn(ni - k_vals)
                if np.isscalar(H_shifted): H_shifted = np.full_like(k_vals, H_shifted)
                
                # Sum product
                val = np.sum(X_k * H_shifted)
                y_vals.append(val)
                
                frames.append({
                    "t": float(ni), # use 't' key for generic frontend compat
                    "h_shifted": np.real(H_shifted).tolist(), 
                    "current_y": float(val)
                })
                
            return {
                "t": n_vals.tolist(),
                "y": np.real(y_vals).tolist(),
                "tau": k_vals.tolist(), # 'tau' for generic compat (actually k)
                "x_tau": np.real(X_k).tolist(),
                "frames": frames
            }

    except Exception as e:
        print(f"Convolution Failed: {e}")
        return None

# TODO: Add Z-Transform logic (SymPy doesn't have a direct z_transform function in older versions, 
# might need manual summation or summation wrapper)
    return "Z-Transform Logic Placeholder"

def extract_poles_zeros(expr_str: str, variable: str):
    """
    Parses H(s) or H(z) and extracts numerical poles and zeros.
    Returns:
        poles: list of {r, i} dicts
        zeros: list of {r, i} dicts
    """
    try:
        var_sym = symbols(variable)
        # Parse expression, robustly handling ^ for power
        valid_expr = expr_str.replace('^', '**')
        expr = parse_expr(valid_expr, transformations=standard_transformations + (implicit_multiplication_application,))
        
        # Simplify to rational form P/Q
        rational_expr = expr.simplify()
        
        numer, denom = rational_expr.as_numer_denom()
        
        # Find roots
        # roots() returns dict {root: multiplicity} or fails if not polynomial
        # solve() is safer for general cases
        from sympy import solve
        
        zeros_roots = solve(numer, var_sym)
        poles_roots = solve(denom, var_sym)
        
        # Helper to format complex number
        def format_root(r):
            val = complex(r) # evaluate to complex float
            return {"r": val.real, "i": val.imag}
            
        zeros_list = [format_root(z) for z in zeros_roots]
        poles_list = [format_root(p) for p in poles_roots]
        
        return {"poles": poles_list, "zeros": zeros_list}
        
    except Exception as e:
        print(f"Error extracting poles/zeros: {e}")
        return {"error": str(e)}
