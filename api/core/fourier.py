
import numpy as np
from sympy import symbols, sympify, integrate, Sum, exp, pi, I, lambdify, Abs, arg, simplify, Function
from sympy.parsing.sympy_parser import parse_expr, standard_transformations, implicit_multiplication_application
from api.core.symbolic import parse_signal, t, n

k = symbols('k')

def calculate_ctfs(signal_eq: str, T: float, k_min: int = -5, k_max: int = 5):
    """
    Calculates Continuous Time Fourier Series coefficients a_k.
    a_k = (1/T) * int(x(t) * exp(-j*k*w0*t), t, 0, T)
    """
    try:
        # Parse signal x(t)
        x_expr = parse_signal(signal_eq, 'continuous')
        
        # Fundamental frequency - recover symbolic pi if T is a multiple
        from sympy import nsimplify
        T_sym = nsimplify(T, [pi])
        w0 = 2 * pi / T_sym
        
        coeffs = []
        
        # Provide a symbolic formula if possible? 
        # SymPy integration might be slow for general k. 
        # We will calculate for specific k values for the spectrum plot.
        
        for k_val in range(k_min, k_max + 1):
            # Term to integrate
            if k_val == 0:
                term = x_expr
            else:
                term = x_expr * exp(-I * k_val * w0 * t)
            
            # Integrate over one period [0, T]
            # Note: User equation might be definedpiecewise or valid for all t.
            # Assuming periodic extension of the definition in [0, T] or standard function.
            
            # Using simplify() can be slow but helps result readability
            ak_sym = integrate(term, (t, 0, T)) / T
            ak_sym = simplify(ak_sym)
            
            # Evaluate to complex number for plotting
            ak_num = complex(ak_sym.evalf())
            
            coeffs.append({
                "k": k_val,
                "value_str": str(ak_sym).replace('**', '^').replace('I', 'j'),
                "magnitude": float(abs(ak_num)),
                "phase": float(arg(ak_num))
            })
            
        return coeffs
            
    except Exception as e:
        print(f"Error calculating CTFS: {e}")
        return []

def calculate_inverse_ctfs(ak_eq: str, T: float, k_min: int = -5, k_max: int = 5):
    """
    Synthesizes x(t) from coefficient formula a_k.
    x(t) = sum(a_k * exp(j*k*w0*t))
    """
    try:
        local_dict = {'k': k, 'pi': pi, 'sin': sympify('sin'), 'sinc': sympify('sinc'), 'I': I, 'j': I}
        transformations = (standard_transformations + (implicit_multiplication_application,))
        ak_expr = parse_expr(ak_eq.replace('^', '**'), local_dict=local_dict, transformations=transformations)
        
        w0 = 2 * pi / T
        xt_terms = []
        
        for k_val in range(k_min, k_max + 1):
            if k_val == 0:
                # Handle 0 specifically if formula has singularity (e.g. 1/k) -- unlikely for valid FS but possible in user input
                try:
                    ak_val = ak_expr.subs(k, 0)
                    if ak_val.has(I): ak_val = complex(ak_val)
                    xt_terms.append(ak_val)
                except:
                    xt_terms.append(0) # Skip DC if singular
            else:
                ak_val = ak_expr.subs(k, k_val)
                xt_terms.append(ak_val * exp(I * k_val * w0 * t))
                
        xt_sym = sum(xt_terms)
        # return real part ideally for physical signals, but keep general
        return xt_sym
        
    except Exception as e:
        print(f"Error calculating Inverse CTFS: {e}")
        return None

def calculate_dtfs(signal_eq: str, N: int):
    """
    Calculates Discrete Time Fourier Series coefficients a_k.
    a_k = (1/N) * sum(x[n] * exp(-j*k*(2pi/N)*n), n, 0, N-1)
    """
    try:
        x_expr = parse_signal(signal_eq, 'discrete')
        # Evaluate x[n] for n = 0 to N-1
        x_vals = []
        # We need a numerical lambda for efficiency
        # Handle 'n' substitution
        for n_val in range(N):
            val = x_expr.subs(n, n_val).evalf()
            if hasattr(val, 'is_complex') and val.is_complex:
                 x_vals.append(complex(val))
            else:
                 x_vals.append(float(val))
                 
        coeffs = []
        for k_val in range(N):
            sum_val = 0
            for n_val in range(N):
                term = x_vals[n_val] * np.exp(-1j * k_val * (2 * np.pi / N) * n_val)
                sum_val += term
            
            ak = sum_val / N
            
            coeffs.append({
                "k": k_val,
                "value_str": f"{ak:.3f}",
                "magnitude": float(np.abs(ak)),
                "phase": float(np.angle(ak))
            })
            
        return coeffs
        
    except Exception as e:
        print(f"Error calculating DTFS: {e}")
        return []

def calculate_inverse_dtfs(ak_list, N: int):
    """
    Synthesizes x[n] from list of coefficients.
    x[n] = sum(a_k * exp(j*k*(2pi/N)*n))
    """
    # Assuming ak_list is list of complex numbers or dicts
    # Simplification: User provides just a formula for ak usually in this app context? 
    # Or strict list? Let's assume formula for consistency with CTFS inverse for now, 
    # or handle list input if passed. 
    # For now implementation: Formula based inverse DTFS (common in textbooks)
    return None # Placeholder, will implement if requested or reuse CTFS structure adapted
