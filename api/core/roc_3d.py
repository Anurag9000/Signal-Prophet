
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
    # Define Grid (Cartesian for both domains to ensure correct 3D representation)
    max_range = plot_range
    x_vals = np.linspace(-max_range, max_range, points)
    y_vals = np.linspace(-max_range, max_range, points)
    X, Y = np.meshgrid(x_vals, y_vals)
    S = X + 1j * Y

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

    elif roc_type == 'stable':
        # Stable system: ROC includes the imaginary axis (Laplace) or unit circle (Z)
        if domain == 'laplace':
            # For a stable system to EXIST, any strip ROC must include the jw axis.
            # Usually, if we just want to see the STABLE ROC, we find the poles 
            # and take the strip containing Re(s)=0.
            # If all poles are Re(s) < 0, it's the causal ROC.
            # If all poles are Re(s) > 0, it's the anti-causal ROC.
            # For now, we'll implement the 'strip' logic:
            real_parts = [p.real for p in poles]
            if not real_parts:
                mask = np.ones_like(H_final, dtype=bool)
            else:
                left_pole = max([r for r in real_parts if r < 0], default=-np.inf)
                right_pole = min([r for r in real_parts if r > 0], default=np.inf)
                # ROC: left_pole < Re(s) < right_pole
                mask = (np.real(S) > left_pole) & (np.real(S) < right_pole)
        else:
            # ROC includes unit circle |z|=1
            mags = [abs(p) for p in poles]
            if not mags:
                mask = np.ones_like(H_final, dtype=bool)
            else:
                inner_pole = max([m for m in mags if m < 1], default=0)
                outer_pole = min([m for m in mags if m > 1], default=np.inf)
                # ROC: inner_pole < |z| < outer_pole
                mask = (np.abs(S) > inner_pole) & (np.abs(S) < outer_pole)

    # Apply mask (set invalid to None/NaN)
    H_final_masked = np.where(mask, H_final, np.nan)

    # Convert to lists for JSON serialization
    z_list = H_final_masked.tolist()
    # Replace nan with None for valid JSON
    z_list_clean = [[(val if not np.isnan(val) else None) for val in row] for row in z_list]

    return {
        "x": x_vals.tolist(),
        "y": y_vals.tolist(),
        "z": z_list_clean
    }
