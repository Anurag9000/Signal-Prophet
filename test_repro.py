import sys
import os
import numpy as np
sys.path.append(os.getcwd())
from api.core.roc_3d import calculate_roc_surface

def test_backend():
    print("Testing backend logic...")
    poles = [{'r': -1, 'i': 0}]
    zeros = []
    
    # Simulate backend call
    try:
        data = calculate_roc_surface(
            [complex(p['r'], p['i']) for p in poles],
            [complex(z['r'], z['i']) for z in zeros],
            1.0,
            'laplace',
            'causal',
            plot_range=10.0
        )
        
        z = np.array(data['z'])
        print(f"Z shape: {len(data['z'])}x{len(data['z'][0])}")
        print(f"X shape: {len(data['x'])}x{len(data['x'][0])}")
        print(f"Max Z: {np.nanmax(np.array(data['z'], dtype=float))}")
        print(f"Min Z: {np.nanmin(np.array(data['z'], dtype=float))}")
        
        if np.all(np.isnan(np.array(data['z'], dtype=float))):
             print("ERROR: All Z values are NaN/None")
        else:
             print("SUCCESS: Data generated.")
             
    except Exception as e:
        print(f"EXCEPTION: {e}")

if __name__ == "__main__":
    test_backend()
