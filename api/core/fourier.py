
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
            # Term to integrate: x(t) * exp(-j * k * w0 * t)
            # exp(0) is 1, so no need for special k=0 check
            term = x_expr * exp(-I * k_val * w0 * t)
            
            # Integrate over one period [0, T]
            # Note: User equation might be definedpiecewise or valid for all t.
            # Assuming periodic extension of the definition in [0, T] or standard function.
            
            # Integrate over one period [-T/2, T/2] which is better for centered signals
            ak_sym = integrate(term, (t, -T_sym/2, T_sym/2)) / T_sym
            ak_sym = simplify(ak_sym)
            
            # Evaluate to complex number for plotting
            ak_num = complex(ak_sym.evalf())
            
            coeffs.append({
                "k": int(k_val),
                "value_str": str(ak_sym).replace('**', '^').replace('I', 'j'),
                "magnitude": float(abs(ak_num)),
                "phase": float(arg(ak_num)),
                "real": float(ak_num.real),
                "imag": float(ak_num.imag)
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
    Optimized with lambdify.
    """
    try:
        x_expr = parse_signal(signal_eq, 'discrete')
        # Numerical implementation for efficiency
        from api.core.utils import get_shared_modules_dict
        m_dict = get_shared_modules_dict('discrete')
        x_fn = lambdify(n, x_expr, modules=m_dict)
        
        n_vals = np.arange(N)
        try:
            x_num = x_fn(n_vals)
        except:
            # Fallback for complex symbolic expressions
            x_num = np.array([complex(x_expr.subs(n, nv).evalf()) for nv in n_vals])
            
        if np.isscalar(x_num): x_num = np.full_like(n_vals, x_num)
                 
        # a_k = (1/N) * sum_{n=0}^{N-1} x[n] exp(-j * k * (2pi/N) * n)
        # This is exactly (1/N) * DFT(x[n])
        ak_values = np.fft.fft(x_num) / N
                 
        coeffs = []
        for k_val, ak in enumerate(ak_values):
            coeffs.append({
                "k": int(k_val),
                "value_str": f"{ak.real:.3f} + {ak.imag:.3f}j",
                "magnitude": float(np.abs(ak)),
                "phase": float(np.angle(ak)),
                "real": float(ak.real),
                "imag": float(ak.imag)
            })
            
        return coeffs
    except Exception as e:
        print(f"Error calculating DTFS: {e}")
        return []

def calculate_inverse_dtfs(ak_eq: str, N: int):
    """
    Synthesizes x[n] from coefficient formula a_k.
    Optimized with lambdify.
    """
    try:
        local_dict = {'k': k, 'pi': pi, 'sin': sympify('sin'), 'sinc': sympify('sinc'), 'I': I, 'j': I}
        transformations = (standard_transformations + (implicit_multiplication_application,))
        ak_expr = parse_expr(ak_eq.replace('^', '**'), local_dict=local_dict, transformations=transformations)
        
        from api.core.utils import get_shared_modules_dict
        m_dict = get_shared_modules_dict('discrete')
        ak_fn = lambdify(k, ak_expr, modules=m_dict)
        
        k_vals = np.arange(N)
        try:
            ak_num = ak_fn(k_vals)
        except:
            ak_num = np.array([complex(ak_expr.subs(k, kv).evalf()) for kv in k_vals])
            
        if np.isscalar(ak_num): ak_num = np.full_like(k_vals, ak_num)
        
        # x[n] = sum_{k=0}^{N-1} a_k exp(j * n * (2pi/N) * k)
        # This is N * IDFT(a_k)
        # Note: np.fft.ifft(A) computes (1/N) * sum(A * exp(j * 2pi/N * n * k))
        # So sum(A * exp(...)) = N * ifft(A)
        xn_values = np.fft.ifft(ak_num) * N
        
        x_values = []
        for n_val, x_comp in enumerate(xn_values):
            x_values.append({
                "n": int(n_val),
                "value": float(np.real(x_comp)),
                "imag": float(np.imag(x_comp))
            })
            
        return x_values
    except Exception as e:
        print(f"Error calculating Inverse DTFS: {e}")
        return []
