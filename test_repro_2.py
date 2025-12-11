import sys
import os
import numpy as np
sys.path.append(os.getcwd())
from api.core.roc_3d import calculate_roc_surface

def test_backend_2():
    print("Testing backend logic 2...")
    # Matches user case: (s+1)/(s^2+2*s+1) -> Pole at -1 (double)
    poles = [{'r': -1, 'i': 0}, {'r': -1, 'i': 0}]
    zeros = [{'r': -1, 'i': 0}]
    
    try:
        data = calculate_roc_surface(
            [complex(p['r'], p['i']) for p in poles],
            [complex(z['r'], z['i']) for z in zeros],
            1.0,
            'laplace',
            'causal',
            plot_range=10.0
        )
        
        z = np.array(data['z'], dtype=float)
        print(f"Z shape: {len(data['z'])}x{len(data['z'][0])}")
        
        valid_z = z[~np.isnan(z)]
        print(f"Total points: {z.size}")
        print(f"Valid points: {valid_z.size}")
        
        if valid_z.size > 0:
            print(f"Max Z: {np.max(valid_z)}")
            print(f"Min Z: {np.min(valid_z)}")
        else:
            print("ERROR: No valid Z points found (All NaN).")
             
    except Exception as e:
        print(f"EXCEPTION: {e}")

if __name__ == "__main__":
    test_backend_2()
