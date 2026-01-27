from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional
from api.core import symbolic, system_analyzer, fourier, roc_3d
from sympy import symbols, Function, pi, I, Abs
import uvicorn
import os
import logging
import traceback

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger("SignalProphetAPI")

app = FastAPI(title="Signals & Systems API")

# Allow CORS for local React dev server
origins = [
    "http://localhost:5173",
    "http://127.0.0.1:5173",
    "http://localhost:3000",
    "https://Anurag9000.github.io"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
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

class ROC3DRequest(BaseModel):
    poles: list[dict] # [{r, i}, ...]
    zeros: list[dict] # [{r, i}, ...]
    gain: float = 1.0
    domain: str # 'laplace' | 'z'
    roc_type: str # 'causal' | 'anticausal'
    plot_range: float = 10.0 # Default range

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
        domain = getattr(req, 'domain', 'continuous')
        
        if req.type == 'laplace':
            latex_res = symbolic.compute_inverse_laplace(req.expression)
        elif req.type == 'fourier':
            latex_res = symbolic.compute_inverse_fourier(req.expression, domain=req.domain)
        elif req.type == 'z':
            latex_res = symbolic.compute_inverse_z(req.expression)
        else:
            raise HTTPException(status_code=400, detail="Invalid inverse type")
            
        # 2. Compute Input Spectrum Plot Data
        spec_data = symbolic.evaluate_frequency_response(req.expression, w_min=-10, w_max=10, num_points=400, type=req.type)
            
        # 3. Compute Output Time Domain Plot Data
        time_data = {"x": [], "y": []}
        if "Error" not in latex_res and "Failed" not in latex_res:
            try:
                # For inverse Z, result is always discrete
                plot_domain = 'discrete' if req.type == 'z' else req.domain
                tx, ty = symbolic.generate_plot_data(latex_res, -5, 10, domain=plot_domain)
                time_data = {"x": tx, "y": ty}
            except Exception as plot_e:
                logger.error(f"[/inverse] Time plot failed: {plot_e}")

        return {
            "latex": latex_res,
            "spectrum": spec_data,
            "time_plot": time_data
        }
    except Exception as e:
         raise HTTPException(status_code=400, detail=str(e))

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
        raise HTTPException(status_code=400, detail=str(e))

class SystemAnalysisRequest(BaseModel):
    equation: str
    domain: str = 'continuous'
    input_equation: Optional[str] = None

@app.post("/analyze_system")
def analyze_system_endpoint(req: SystemAnalysisRequest):
    try:
        # 1. Analyze properties
        properties = system_analyzer.analyze_system(req.equation, req.domain)
        
        # 2. Determine Input and Output
        input_str = req.input_equation if req.input_equation else ('d(t)' if req.domain == 'continuous' else 'd[n]')
        
        # 3. Calculate Input Plot
        try:
            input_px, input_py = symbolic.generate_plot_data(input_str, -5, 10, domain=req.domain)
            input_plot = {"x": input_px, "y": input_py}
        except:
            input_plot = {"x": [], "y": []}

        # 4. Calculate Response
        try:
            output_eq_str, output_plot = system_analyzer.calculate_system_response(req.equation, input_str, req.domain)
        except Exception as e:
            logger.error(f"Response calculation failed: {e}")
            output_eq_str, output_plot = "Error", {"x": [], "y": []}

        # 5. Calculate Impulse Response Plot
        impulse_plot = {"x": [], "y": []}
        if properties and 'impulse_response' in properties:
             try:
                 h_px, h_py = symbolic.generate_plot_data(properties['impulse_response'], -5, 10, domain=req.domain)
                 impulse_plot = {"x": h_px, "y": h_py}
             except: pass

        return {
            "properties": properties, 
            "plot": output_plot,
            "input_plot": input_plot,
            "impulse_plot": impulse_plot,
            "output_equation": output_eq_str
        }
    except Exception as e:
        logger.error(f"System analysis failed: {e}")
        logger.error(traceback.format_exc())
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
            # DT Synthesis
            x_vals_data = fourier.calculate_inverse_dtfs(req.ak_expression, req.N)
            
            # Extract x and y for plot
            x_list = [item['n'] for item in x_vals_data]
            y_list = [item['value'] for item in x_vals_data]
            
            return {
                "expression": f"Synthesized sequence (N={req.N})", 
                "plot": {"x": x_list, "y": y_list}
            }
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


class PeriodDetectionRequest(BaseModel):
    expression: str
    domain: str = 'continuous'

@app.post("/fourier/detect-period")
def detect_period_endpoint(req: PeriodDetectionRequest):
    """
    Auto-detect period T (CT) or N (DT) for a given signal.
    Returns: {period: float|int|null, message: str}
    """
    try:
        from api.core.period_detection import detect_period_ct, detect_period_dt
        
        if req.domain == 'continuous':
            period, message = detect_period_ct(req.expression)
        else:
            period, message = detect_period_dt(req.expression)
        
        return {"period": period, "message": message}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/roc/surface")
def get_roc_surface(req: ROC3DRequest):
    try:
        # Convert dict objects to complex numbers
        poles_c = [complex(p['r'], p['i']) for p in req.poles]
        zeros_c = [complex(z['r'], z['i']) for z in req.zeros]
        
        data = roc_3d.calculate_roc_surface(
            poles_c, zeros_c, req.gain, req.domain, req.roc_type, plot_range=req.plot_range
        )
        return data
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

if __name__ == "__main__":
    uvicorn.run("api.main:app", host="0.0.0.0", port=8000, reload=True)
