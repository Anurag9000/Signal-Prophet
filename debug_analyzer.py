
try:
    from api.core import system_analyzer
    print("Import successful")
    
    eq = "3x(t)* u(t)"
    domain = "continuous"
    
    print(f"Analyzing: {eq}")
    results = system_analyzer.analyze_system(eq, domain)
    print("Results:", results)
    
except Exception as e:
    print(f"CRASH: {e}")
    import traceback
    traceback.print_exc()
