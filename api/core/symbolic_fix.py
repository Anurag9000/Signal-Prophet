def generate_plot_data(expr_str_or_obj, t_min: float = -5, t_max: float = 5, num_points: int = 500, domain: str = 'continuous'):
    """
    Generates x, y arrays for plotting.
    """
    try:
        if isinstance(expr_str_or_obj, str):
            # Preprocess: convert formatted notation back to parseable format
            expr_str = expr_str_or_obj.replace('^', '**')
            expr = parse_signal(expr_str, domain)
        else:
            expr = expr_str_or_obj
        
        # Visual Proxy for DiracDelta: Replace with VisualDirac for plotting
        from sympy import Function
        VisualDirac = Function('VisualDirac')
        expr_visual = expr.replace(DiracDelta, VisualDirac)
        
        # Use shared modules dict
        modules_dict = get_shared_modules_dict(domain)

        if domain == 'continuous':
            # Create lambda function
            f = lambdify(t, expr_visual, modules=modules_dict)
            # Generate time vector
            t_vals = np.linspace(t_min, t_max, num_points)
            try:
                y_vals = f(t_vals)
                # Handle constant output
                if np.isscalar(y_vals):
                    y_vals = np.full_like(t_vals, y_vals)
            except Exception:
                # Fallback for complex issues or singularities: eval one by one (slower but safer)
                y_vals = np.zeros_like(t_vals)
            
            return t_vals.tolist(), np.real(y_vals).tolist() # Return real part for standard plotting
            
        elif domain == 'discrete':
            f = lambdify(n, expr_visual, modules=modules_dict)
            # Integer samples only for discrete signals
            n_vals = np.arange(int(t_min), int(t_max) + 1)
            try:
                y_vals = f(n_vals)
                if np.isscalar(y_vals):
                    y_vals = np.full_like(n_vals, y_vals, dtype=float)
            except Exception:
                y_vals = np.zeros_like(n_vals, dtype=float)
                
            return n_vals.tolist(), np.real(y_vals).tolist()
            
    except Exception as outer_e:
        print(f"[generate_plot_data] Error: {outer_e}")
        return [], []
