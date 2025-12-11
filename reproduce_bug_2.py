
try:
    from api.core import symbolic
    from api.core import system_analyzer
    
    eq = "3*x(t-3)*u(t-3)"
    domain = 'continuous'
    
    print(f"Testing Equation: {eq}")
    
    # 1. Test Analysis (Linearity Check)
    print("--- 1. Analyzing Properties ---")
    results = system_analyzer.analyze_system(eq, domain)
    print("Linearity Status:", results['linearity']['status'])
    print("Explanation:", results['linearity']['explanation'])
    
    # 2. Test Plotting Logic (Simulation of api/main.py failure)
    print("\n--- 2. generating Plot Data ---")
    # Simulate the naive replacement from api/main.py
    plot_eq = eq.replace('x(t)', '1')
    print(f"Processed Plot Equation: {plot_eq}")
    
    if plot_eq == eq:
        print("WARNING: x(t) replacement failed! Equation is unchanged.")
    
    print("Calling generate_plot_data...")
    tx, ty = symbolic.generate_plot_data(plot_eq, -2, 10, domain=domain)
    
    print(f"Success! Generated {len(tx)} points.")

except Exception as e:
    print(f"\nCRASH DETECTED: {e}")
    import traceback
    traceback.print_exc()
