
import numpy as np

def calculate_roc_surface(poles, zeros, gain, domain, roc_type, points=50):
    """
    Generates X, Y, Z data for 3D surface plot of |H(s)| or |H(z)|.
    
    Args:
        poles (list of complex): System poles.
        zeros (list of complex): System zeros.
        gain (float): System gain.
        domain (str): 'laplace' or 'z'.
        roc_type (str): 'causal' or 'anticausal'.
        points (int): Grid resolution.
        
    Returns:
        dict: {x: list, y: list, z: list} (lists of lists for Plotly)
    """
    # Define Grid
    if domain == 'laplace':
        # s = sigma + j*omega
        # Range logic: encompass all poles/zeros + buffer
        all_pts = poles + zeros + [0] # Ensure 0 is included
        max_r = max([abs(p.real) for p in all_pts] + [2]) + 1
        max_i = max([abs(p.imag) for p in all_pts] + [5]) + 1
        
        x_vals = np.linspace(-max_r, max_r, points)  # Sigma
        y_vals = np.linspace(-max_i, max_i, points)  # j*Omega
        X, Y = np.meshgrid(x_vals, y_vals)
        S = X + 1j * Y
        
    else: # z-transform
        # z = r * e^(j*omega)
        # Plot vs r and omega
        all_pts = poles + zeros + [0]
        max_r = max([abs(p) for p in all_pts] + [1.5]) + 1
        
        r_vals = np.linspace(0, max_r, points) # r
        w_vals = np.linspace(-np.pi, np.pi, points) # omega
        X, Y = np.meshgrid(r_vals, w_vals) # X is r, Y is omega
        S = X * np.exp(1j * Y) # Z values

    # Calculate H(s) or H(z)
    numerator = np.ones_like(S, dtype=complex)
    for z in zeros:
        numerator *= (S - z)
        
    denominator = np.ones_like(S, dtype=complex)
    for p in poles:
        denominator *= (S - p)
    
    # Avoid division by zero
    epsilon = 1e-10
    H_complex = gain * numerator / (denominator + epsilon)
    H_mag = np.abs(H_complex)
    
    # Cap infinity for visualization
    MAX_HEIGHT = 10.0
    H_mag = np.minimum(H_mag, MAX_HEIGHT)
    
    # Apply ROC Masking (NaN for undefined regions)
    mask = np.ones_like(H_mag, dtype=bool)
    
    if domain == 'laplace':
        # Causal: Re(s) > max(Re(poles))
        # Anti-Causal: Re(s) < min(Re(poles))
        real_parts = [p.real for p in poles]
        
        if not real_parts:
            # No poles, ROC is entire plane
            pass 
        elif roc_type == 'causal':
            limit = max(real_parts)
            mask = X > limit 
        elif roc_type == 'anticausal':
            limit = min(real_parts)
            mask = X < limit
            
    else: # z-transform
        # Causal: |z| > max(|poles|)
        # Anti-Causal: |z| < min(|poles|)
        magnitudes = [abs(p) for p in poles]
        
        # Calculate |z| mesh for comparison
        # Since X is 'r', we just compare X
        Z_abs = X 
        
        if not magnitudes:
            pass
        elif roc_type == 'causal':
            limit = max(magnitudes)
            mask = Z_abs > limit
        elif roc_type == 'anticausal':
            limit = min(magnitudes)
            mask = Z_abs < limit

    # Apply mask (set invalid to None/NaN)
    # Numpy use nan
    H_mag_masked = np.where(mask, H_mag, np.nan)

    # Convert to lists for JSON serialization
    return {
        "x": x_vals.tolist() if domain == 'laplace' else r_vals.tolist(),
        "y": y_vals.tolist() if domain == 'laplace' else w_vals.tolist(),
        "z": H_mag_masked.tolist()
    }
