
try:
    from api.core import symbolic
    import numpy as np
    
    # Simulate System Analyzer logic
    eq = "3*x(t)*u(t)"
    domain = 'continuous'
    
    print(f"Original Equation: {eq}")
    
    # 1. Replace x(t) with 1
    plot_eq = eq.replace('x(t)', '1')
    print(f"Plot Equation: {plot_eq}")
    
    # 2. Generate Plot Data
    print("Calling generate_plot_data...")
    tx, ty = symbolic.generate_plot_data(plot_eq, -2, 10, domain=domain)
    
    print(f"Success! Generated {len(tx)} points.")
    print(f"Sample y: {ty[:5]}")

except Exception as e:
    print(f"CRASH: {e}")
    import traceback
    traceback.print_exc()
