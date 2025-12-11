
import numpy as np

def calculate_roc_surface(poles, zeros, gain, domain, roc_type, points=50, plot_range=10.0):
    """
    Generates X, Y, Z data for 3D surface plot of |H(s)| or |H(z)|.
    """
    # Dynamic resolution based on range for smoothness
    # Base points = 50. For larger ranges, increase density.
    # Cap at 200 to prevent performance issues.
    adaptive_points = int(max(50, min(plot_range * 2, 200))) 
    points = adaptive_points
    
    # Define Grid
    if domain == 'laplace':
        # s = sigma + j*omega
        max_r = plot_range
        max_i = plot_range
        
        x_vals = np.linspace(-max_r, max_r, points)  # Sigma
        y_vals = np.linspace(-max_i, max_i, points)  # j*Omega
        X, Y = np.meshgrid(x_vals, y_vals)
        S = X + 1j * Y
        
    else: # z-transform
        # z = r * e^(j*omega)
        max_r = plot_range
        
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
    
    # Visual Clamping (Prevent infinity spikes)
    if len(poles) > 0:
        # For poles, cap at a dynamic robust max to allow seeing the rest of the surface
        robust_max = np.nanpercentile(H_mag, 90)
        # Allow at least 10, but clamp to reasonable upper bound
        clamp_val = max(10.0, min(robust_max * 1.5, 1000.0))
        H_mag = np.minimum(H_mag, clamp_val)
    # For zeros only, do NOT clamp (let it grow to show valleys)
    
    H_final = H_mag

    # Apply ROC Masking
    mask = np.ones_like(H_final, dtype=bool)
    
    if roc_type == 'causal':
        # ROC is outside the outermost pole
        if domain == 'laplace':
            limit = max([p.real for p in poles]) if poles else -np.inf
            # Re(s) > limit
            mask = np.real(S) > limit
        else:
            limit = max([abs(p) for p in poles]) if poles else 0
            # |z| > limit
            mask = np.abs(S) > limit
            
    elif roc_type == 'anticausal':
        # ROC is inside the innermost pole
        if domain == 'laplace':
            limit = min([p.real for p in poles]) if poles else np.inf
            mask = np.real(S) < limit
        else:
            limit = min([abs(p) for p in poles]) if poles else np.inf
            mask = np.abs(S) < limit

    # Apply mask (set invalid to None/NaN)
    H_final_masked = np.where(mask, H_final, np.nan)

    # Convert to lists for JSON serialization
    z_list = H_final_masked.tolist()
    # Replace nan with None for valid JSON
    z_list_clean = [[(val if not np.isnan(val) else None) for val in row] for row in z_list]

    return {
        "x": x_vals.tolist() if domain == 'laplace' else r_vals.tolist(),
        "y": y_vals.tolist() if domain == 'laplace' else w_vals.tolist(),
        "z": z_list_clean
    }
