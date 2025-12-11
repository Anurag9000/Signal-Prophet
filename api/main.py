from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional
from api.core import symbolic, system_analyzer, fourier
import uvicorn
import os

app = FastAPI(title="Signals & Systems API")

# Allow CORS for local React dev server
origins = [
    "http://localhost:5173",  # Vite default
    "http://127.0.0.1:5173",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # For dev simplicity, allow all.
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class PlotRequest(BaseModel):
    expression: str
    t_min: float = -5.0
    t_max: float = 5.0
    domain: str = "continuous" # 'continuous' or 'discrete'

class TransformRequest(BaseModel):
    expression: str
    type: str # 'laplace', 'fourier', 'z'

class SpectrumRequest(BaseModel):
    expression: str
    w_min: float = -10.0
    w_max: float = 10.0
    domain: str = 'continuous' # 'continuous' or 'discrete'

class SeriesRequest(BaseModel):
    expression: str
    period: float = 6.28
    num_coeffs: int = 5

class ConvolutionRequest(BaseModel):
    x_expr: str
    h_expr: str
    domain: str = 'continuous'

@app.get("/")
def read_root():
    return {"status": "online", "message": "Signals & Systems API Ready"}

@app.post("/plot")
def get_plot_data(req: PlotRequest):
    try:
        x, y = symbolic.generate_plot_data(req.expression, req.t_min, req.t_max, domain=req.domain)
        return {"x": x, "y": y}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/transform")
def get_transform(req: TransformRequest):
    try:
        if req.type == 'laplace':
            result = symbolic.compute_laplace(req.expression)
        elif req.type == 'fourier':
            result = symbolic.compute_fourier(req.expression)
        elif req.type == 'z':
            result = symbolic.compute_z(req.expression)
        else:
            raise HTTPException(status_code=400, detail="Invalid transform type")
        
        return {"latex": result}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/spectrum")
def get_spectrum(req: SpectrumRequest):
    try:
        data = symbolic.compute_spectrum(req.expression, req.w_min, req.w_max, domain=req.domain)
        if data is None:
             # Return empty structure rather than error for softer UI handling
             return {"magnitude": {"x": [], "y": []}, "phase": {"x": [], "y": []}}
        return data 
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/series")
def get_series(req: SeriesRequest):
    try:
        coeffs = symbolic.compute_fourier_series_coeffs(req.expression, req.period, req.num_coeffs)
        return {"coeffs": coeffs}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/convolution")
def get_convolution(req: ConvolutionRequest):
    try:
        data = symbolic.compute_convolution(req.x_expr, req.h_expr, domain=req.domain)
        if not data:
            raise HTTPException(status_code=400, detail="Convolution failed")
        return data
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

class InverseRequest(BaseModel):
    expression: str
    type: str # 'laplace' (s->t), 'fourier' (w->t)
    domain: str = 'continuous'  # 'continuous' or 'discrete'

@app.post("/inverse")
def get_inverse(req: InverseRequest):
    try:
        # Determine domain from request (default to continuous for backward compatibility)
        domain = getattr(req, 'domain', 'continuous')
        
        print(f"[/inverse] Type: {req.type}, Domain: {domain}")
        
        # 1. Compute Symbolic Inverse
        if req.type == 'laplace':
            latex_res = symbolic.compute_inverse_laplace(req.expression)
        elif req.type == 'fourier':
            latex_res = symbolic.compute_inverse_fourier(req.expression, domain=domain)
        else:
            return {"error": "Invalid inverse type"}
            
        # 2. Compute Input Spectrum Plot Data (X(w)) - THE MISSING PIECE!
        print(f"[/inverse] Computing spectrum for expression: {req.expression}")
        spec_data = symbolic.evaluate_frequency_response(req.expression, w_min=-10, w_max=10, num_points=400, type=req.type)
        if not spec_data or not spec_data.get('magnitude'):
            print("[/inverse] WARNING: evaluate_frequency_response returned no data")
            spec_data = {"magnitude": {"x": [], "y": []}, "phase": {"x": [], "y": []}}
        else:
            print(f"[/inverse] Spectrum computed successfully: {len(spec_data['magnitude']['x'])} points")
            
        # 3. Compute Output Time Domain Plot Data (x(t) or x[n])
        time_data = {"x": [], "y": []}
        if "Error" not in latex_res and "Failed" not in latex_res:
            try:
                print(f"[/inverse] Generating time plot for: {latex_res}, domain: {domain}")
                tx, ty = symbolic.generate_plot_data(latex_res, -5, 10, domain=domain)
                time_data = {"x": tx, "y": ty}
                print(f"[/inverse] Time plot generated: {len(tx)} points")
            except Exception as plot_e:
                print(f"[/inverse] Time plot failed: {plot_e}")
                import traceback
                traceback.print_exc()

        return {
            "latex": latex_res,
            "spectrum": spec_data,
            "time_plot": time_data
        }
    except Exception as e:
         return {"latex": f"Error: {str(e)}", "spectrum": None, "time_plot": None}

class TransferFunctionRequest(BaseModel):
    expression: str
    variable: str  # 's' or 'z'

@app.post("/parse_transfer_function")
def parse_transfer_function_endpoint(req: TransferFunctionRequest):
    """
    Parse a transfer function like (s+1)/(s^2 + 2*s + 1) and return poles and zeros
    """
    try:
        result = symbolic.parse_transfer_function(req.expression, req.variable)
        return result
    except Exception as e:
        return {"error": str(e), "poles": [], "zeros": []}

class SystemAnalysisRequest(BaseModel):
    equation: str
    domain: str = 'continuous'
    input_equation: Optional[str] = None

@app.post("/analyze_system")
def analyze_system_endpoint(req: SystemAnalysisRequest):
    try:
        from api.core import system_analyzer
        from sympy import symbols, Function, sympify
        
        # Analyze properties
        properties = system_analyzer.analyze_system(req.equation, req.domain)
        
        # Determine Input Equation
        if req.input_equation:
            input_str = req.input_equation
        else:
            input_str = 'delta(t)' if req.domain == 'continuous' else 'delta[n]'
            
        # Generate Input Plot
        try:
            input_px, input_py = symbolic.generate_plot_data(input_str, -5, 10, domain=req.domain)
            input_plot = {"x": input_px, "y": input_py}
        except Exception as e:
            print(f"[analyze_system] Input plot failed: {e}")
            input_plot = {"x": [], "y": []}

        # Generate Output Plot (System Response)
        try:
            # 1. Parse Input Expression
            # e.g. input_str = "cos(t)" -> input_expr = cos(t)
            input_expr = symbolic.parse_signal(input_str, req.domain)
            
            # 2. Parse System Equation with x as a Function
            # We need to treat 'x' as a Function to handle x(t-1) etc.
            t, n = symbols('t n')
            x = Function('x')
            
            # Custom parsing to ensure x is treated as Function
            # We reuse parse_signal logic but make sure 'x' is in local_dict as a Function
            # Note: symbolic.py helpers might not expose local_dict, so we do it manually or rely on parse_signal
            # Actually parse_signal maps 'x' to symbol 'x'. We might need to override.
            # Let's try to substitute on the string level first if simple, or use symbolic substitution.
            
            # BETTER APPROACH: Symbolic Substitution
            # Parse system equation using parse_signal, but we need x to be a Function.
            # parse_signal likely defines x as Symbol 'x' from line 10 of symbolic.py
            
            # Let's do a trick: replacement on the string for standard cases, 
            # OR redefine parse logic here.
            
            # Let's use clean symbolic substitution:
            from sympy.parsing.sympy_parser import parse_expr, standard_transformations, implicit_multiplication_application
            
            transformations = (standard_transformations + (implicit_multiplication_application,))
            local_dict = {
                't': t, 'n': n, 
                'x': x, # x is a Function
                'u': symbolic.Heaviside, 'd': symbolic.DiracDelta,
                'Heaviside': symbolic.Heaviside, 'DiracDelta': symbolic.DiracDelta,
                'sin': symbolic.sin, 'cos': symbolic.cos, 'exp': symbolic.exp,
                'pi': symbolic.pi, 'Abs': symbolic.Abs
            }
            
            # Pre-clean system equation similar to parse_signal
            sys_eq_clean = req.equation.replace('^', '**')
            
            # Normalize brackets: u[n] -> u(n), x[n] -> x(n)
            # This is crucial for SymPy processing where functions use ()
            sys_eq_clean = sys_eq_clean.replace('[', '(').replace(']', ')')
            
            # Handle aliases after bracket normalization
            sys_eq_clean = sys_eq_clean.replace('u(', 'Heaviside(')
            sys_eq_clean = sys_eq_clean.replace('d(', 'DiracDelta(')
            
            system_expr = parse_expr(sys_eq_clean, local_dict=local_dict, transformations=transformations)
            
            # 3. Substitute x(...) with input_expr
            # Case A: x(t) or x(arg) -> input_expr.subs(t, arg)
            # Case B: x (symbol) -> input_expr (direct replacement)
            
            # We need a lambda for the substitution
            # input_expr depends on t (or n)
            var = t if req.domain == 'continuous' else n
            
            # Define the replacement Logic
            # sub_func will take the argument of x (e.g. t-1) and return input_expr with t replaced by t-1
            def sub_func(*args):
                if not args: return input_expr
                return input_expr.subs(var, args[0])
            
            # Perform substitution
            # replace(x, sub_func) handles x(t), x(t-1)
            output_expr = system_expr.replace(x, sub_func)
            
            print(f"[analyze_system] Output Expr: {output_expr}")
            
            # 4. Generate Data from Output Expr
            output_px, output_py = symbolic.generate_plot_data(str(output_expr), -5, 10, domain=req.domain)
            output_plot = {"x": output_px, "y": output_py}
            
        except Exception as plot_e:
            print(f"[analyze_system] Output plot failed: {plot_e}")
            import traceback
            traceback.print_exc()
            output_plot = {"x": [], "y": []}
            output_expr = "Error calculating output"

        # Generate Impulse Response Plot
        # properties['impulse_response'] contains h(t) string from system_analyzer
        impulse_plot = {"x": [], "y": []}
        if properties and 'impulse_response' in properties:
             try:
                 h_str = properties['impulse_response']
                 # Convert h_str labels back to symbolic functions for plotting if needed? 
                 # The string returned has 'u' and 'd', symbolic parser handles them.
                 # generate_plot_data calls parse_signal which handles u/d.
                 h_px, h_py = symbolic.generate_plot_data(h_str, -5, 10, domain=req.domain)
                 impulse_plot = {"x": h_px, "y": h_py}
             except Exception as e:
                 print(f"[analyze_system] Impulse plot failed: {e}")

        output_eq_str = str(output_expr).replace('**', '^').replace('DiracDelta', 'd').replace('Heaviside', 'u')
        if req.domain == 'discrete':
            output_eq_str = output_eq_str.replace('(', '[').replace(')', ']')

        return {
            "properties": properties, 
            "plot": output_plot,
            "input_plot": input_plot,
            "impulse_plot": impulse_plot,
            "output_equation": output_eq_str
        }

    except Exception as e:
        print(f"Analyze System Error: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

# ==========================================
# Fourier Series Endpoints
# ==========================================

class FourierAnalysisRequest(BaseModel):
    expression: str
    T: float = 6.28  # Period for CT
    N: int = 10      # Period for DT
    domain: str = 'continuous'
    k_min: int = -5
    k_max: int = 5

class FourierSynthesisRequest(BaseModel):
    ak_expression: str # e.g. "1/k"
    T: float = 6.28
    N: int = 10
    domain: str = 'continuous'
    k_min: int = -5
    k_max: int = 5

@app.post("/fourier/analyze")
def fourier_analyze(req: FourierAnalysisRequest):
    try:
        coeffs = []
        if req.domain == 'continuous':
            coeffs = fourier.calculate_ctfs(req.expression, req.T, req.k_min, req.k_max)
        else:
            coeffs = fourier.calculate_dtfs(req.expression, req.N)
            
        return {"coeffs": coeffs}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/fourier/synthesize")
def fourier_synthesize(req: FourierSynthesisRequest):
    try:
        # 1. Calculate Symbolic Expression for Reconstructed Signal
        if req.domain == 'continuous':
            xt_expr = fourier.calculate_inverse_ctfs(req.ak_expression, req.T, req.k_min, req.k_max)
            
            # 2. Generate Plot Data from this expression
            # x(t) plot
            x_vals, y_vals = symbolic.generate_plot_data(str(xt_expr), 0, req.T * 2, domain='continuous')
            
            return {
                "expression": str(xt_expr).replace('**', '^').replace('I', 'j'),
                "plot": {"x": x_vals, "y": y_vals}
            }
        else:
            # DT Synthesis placeholder or implement if needed
            # For now, let's just return empty or support later if formula based
            return {"expression": "Not implemented for DT yet", "plot": {"x": [], "y": []}}
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    uvicorn.run("api.main:app", host="0.0.0.0", port=8000, reload=True)
