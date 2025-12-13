import React, { useState, useEffect, useRef } from 'react';
import axios from 'axios';
import Plot from 'react-plotly.js';
import { Play, Pause, Loader2, RefreshCw } from 'lucide-react';
import { API_URL } from '../config';

const ConvolutionLab = () => {
    const [domain, setDomain] = useState('continuous'); // 'continuous' | 'discrete'
    const [xExpr, setXExpr] = useState("u(t) - u(t-2)");
    const [hExpr, setHExpr] = useState("exp(-t)*u(t)");
    const [loading, setLoading] = useState(false);
    const [data, setData] = useState(null);
    const [frameIdx, setFrameIdx] = useState(0);
    const [isPlaying, setIsPlaying] = useState(false);

    // Reset defaults on domain switch
    useEffect(() => {
        if (domain === 'continuous') {
            setXExpr("u(t) - u(t-2)");
            setHExpr("exp(-t)*u(t)");
        } else {
            setXExpr("u[n] - u[n-5]");
            setHExpr("0.8**n * u[n]");
        }
        setData(null);
        setIsPlaying(false);
    }, [domain]);

    const handleSimulate = async () => {
        setLoading(true);
        setIsPlaying(false);
        try {
            const res = await axios.post(`${API_URL}/convolution`, {
                x_expr: xExpr,
                h_expr: hExpr,
                domain: domain
            });
            setData(res.data);
            setFrameIdx(0);
        } catch (e) {
            console.error(e);
            alert("Simulation failed. Check syntax.");
        } finally {
            setLoading(false);
        }
    };

    // Animation Loop
    useEffect(() => {
        let interval;
        if (isPlaying && data) {
            interval = setInterval(() => {
                setFrameIdx(prev => {
                    if (prev >= data.frames.length - 1) {
                        setIsPlaying(false); // Stop at end
                        return prev;
                    }
                    return prev + 1;
                });
            }, domain === 'discrete' ? 200 : 50); // Slower for discrete
        }
        return () => clearInterval(interval);
    }, [isPlaying, data, domain]);

    const currentFrame = data ? data.frames[frameIdx] : null;
    const tLabel = domain === 'continuous' ? 't' : 'n';
    const tauLabel = domain === 'continuous' ? 'τ' : 'k';

    // --- Chart Data Preparation ---

    // Plot A: x(tau) static, h(t-tau) dynamic
    const plotA = data ? {
        data: [
            {
                x: data.tau,
                y: data.x_tau,
                name: `x(${tauLabel})`,
                type: 'scatter',
                mode: domain === 'discrete' ? 'markers' : 'lines',
                line: { color: '#2563eb', width: 3 },
                marker: { color: '#2563eb', size: 6 },
                fill: domain === 'continuous' ? 'tozeroy' : 'none',
                fillcolor: 'rgba(37, 99, 235, 0.1)'
            },
            {
                x: data.tau,
                y: currentFrame ? currentFrame.h_shifted : [],
                name: `h(${currentFrame?.t.toFixed(domain === 'discrete' ? 0 : 2)} - ${tauLabel})`,
                type: 'scatter',
                mode: domain === 'discrete' ? 'markers' : 'lines',
                line: { color: '#ef4444', width: 2, dash: 'dot' },
                marker: { color: '#ef4444', size: 6, symbol: 'x' }
            },
            // Product fill (visual aid)
            {
                x: data.tau,
                y: currentFrame ? data.x_tau.map((x, i) => x * currentFrame.h_shifted[i]) : [],
                name: 'Product',
                type: 'scatter',
                mode: domain === 'discrete' ? 'markers' : 'none',
                marker: { color: '#10b981', size: 4 },
                fill: domain === 'continuous' ? 'tozeroy' : 'none',
                fillcolor: 'rgba(16, 185, 129, 0.3)'
            }
        ],
        layout: {
            title: { text: `Integration Window`, font: { size: 14 } },
            margin: { t: 30, b: 30, l: 40, r: 20 },
            xaxis: { title: `${tauLabel} (Shift Variable)` },
            yaxis: { range: [-2, 2] },
            showlegend: true,
            legend: { orientation: 'h', y: 1.1 }
        }
    } : null;

    // Plot B: y(t) growing
    const plotB = data ? {
        data: [
            {
                x: data.t,
                y: data.y, // Full Result shadow
                name: `y(${tLabel}) Final`,
                type: 'scatter',
                mode: domain === 'discrete' ? 'markers' : 'lines',
                line: { color: '#e2e8f0', width: 2 },
                marker: { color: '#e2e8f0', size: 6 }
            },
            {
                x: data.t.slice(0, frameIdx + 1),
                y: data.y.slice(0, frameIdx + 1),
                name: `y(${tLabel}) Current`,
                type: 'scatter',
                mode: domain === 'discrete' ? 'markers+lines' : 'lines',
                line: { color: '#10b981', width: 3 },
                marker: { color: '#10b981', size: 6 }
            },
            {
                x: [currentFrame?.t],
                y: [currentFrame?.current_y],
                mode: 'markers',
                marker: { color: '#1ee8a5ff', size: 10, symbol: 'circle-open', line: { width: 2 } }
            }
        ],
        layout: {
            title: { text: `Convolution Result: y(${tLabel})`, font: { size: 14 } },
            margin: { t: 30, b: 30, l: 40, r: 20 },
            xaxis: { title: `Time Index (${tLabel})` },
            showlegend: false
        }
    } : null;

    return (
        <div className="grid grid-cols-1 lg:grid-cols-12 gap-6 min-h-[600px]">
            {/* Input Controls */}
            <div className="lg:col-span-4 space-y-4">
                <div className="bg-white p-6 rounded-2xl shadow-sm border border-slate-200">
                    <h3 className="font-bold text-slate-800 mb-4">Convolution Config</h3>

                    {/* Domain Switch */}
                    <div className="flex mb-6 bg-slate-100 p-1 rounded-lg">
                        <button
                            onClick={() => setDomain('continuous')}
                            className={`flex-1 py-1.5 text-xs font-bold rounded-md transition ${domain === 'continuous' ? 'bg-white text-indigo-600 shadow-sm' : 'text-slate-500 hover:text-slate-700'}`}
                        >
                            Continuous CT
                        </button>
                        <button
                            onClick={() => setDomain('discrete')}
                            className={`flex-1 py-1.5 text-xs font-bold rounded-md transition ${domain === 'discrete' ? 'bg-white text-emerald-600 shadow-sm' : 'text-slate-500 hover:text-slate-700'}`}
                        >
                            Discrete DT
                        </button>
                    </div>

                    <div className="space-y-4">
                        <div>
                            <label className="block text-xs font-bold text-slate-500 uppercase mb-1">Input Signal x({tLabel})</label>
                            <input
                                type="text"
                                value={xExpr}
                                onChange={e => setXExpr(e.target.value)}
                                className="w-full px-3 py-2 border rounded-lg font-mono text-sm focus:ring-2 focus:ring-blue-500 outline-none"
                            />
                        </div>
                        <div>
                            <label className="block text-xs font-bold text-slate-500 uppercase mb-1">Impulse Response h({tLabel})</label>
                            <input
                                type="text"
                                value={hExpr}
                                onChange={e => setHExpr(e.target.value)}
                                className="w-full px-3 py-2 border rounded-lg font-mono text-sm focus:ring-2 focus:ring-blue-500 outline-none"
                            />
                        </div>

                        <button
                            onClick={handleSimulate}
                            disabled={loading}
                            className={`w-full py-2 text-white rounded-lg font-medium flex justify-center items-center gap-2 transition ${domain === 'continuous' ? 'bg-indigo-600 hover:bg-indigo-700' : 'bg-emerald-600 hover:bg-emerald-700'}`}
                        >
                            {loading ? <Loader2 className="animate-spin" size={16} /> : <RefreshCw size={16} />}
                            Simulate {domain === 'continuous' ? 'Integral' : 'Sum'}
                        </button>
                    </div>

                    <div className="mt-6 pt-4 border-t border-slate-100">
                        <p className="text-xs text-slate-400">
                            {domain === 'continuous'
                                ? "Computes $y(t) = \\int x(\\tau)h(t-\\tau)d\\tau$."
                                : "Computes $y[n] = \\sum_{k=-\\infty}^{\\infty} x[k]h[n-k]$."
                            }
                        </p>
                    </div>
                </div>
            </div>

            {/* Viz Area */}
            <div className="lg:col-span-8 space-y-4">
                {data ? (
                    <div className="bg-white p-4 rounded-2xl shadow-sm border border-slate-200 space-y-4">

                        {/* Playback Controls */}
                        <div className="flex items-center gap-4 bg-slate-50 p-2 rounded-xl">
                            <button
                                onClick={() => {
                                    if (!isPlaying && frameIdx >= data.frames.length - 1) {
                                        setFrameIdx(0);
                                        setIsPlaying(true);
                                    } else {
                                        setIsPlaying(!isPlaying);
                                    }
                                }}
                                className="p-2 bg-white shadow rounded-full hover:text-blue-600 transition"
                            >
                                {isPlaying ? <Pause size={20} fill="currentColor" /> : <Play size={20} fill="currentColor" />}
                            </button>

                            <input
                                type="range"
                                min="0"
                                max={data.frames.length - 1}
                                value={frameIdx}
                                onChange={(e) => { setIsPlaying(false); setFrameIdx(parseInt(e.target.value)); }}
                                className="flex-1"
                            />
                            <span className="text-xs font-mono w-20 text-right">{tLabel} = {currentFrame?.t.toFixed(domain === 'discrete' ? 0 : 2)}</span>
                        </div>

                        {/* Plots */}
                        <div className="h-64 w-full bg-slate-50 rounded-xl overflow-hidden border border-slate-100">
                            <Plot
                                data={plotA.data}
                                layout={{ ...plotA.layout, autosize: true }}
                                useResizeHandler={true}
                                style={{ width: '100%', height: '100%' }}
                                config={{ displayModeBar: false }}
                            />
                        </div>

                        <div className="h-48 w-full bg-slate-50 rounded-xl overflow-hidden border border-slate-100">
                            <Plot
                                data={plotB.data}
                                layout={{ ...plotB.layout, autosize: true }}
                                useResizeHandler={true}
                                style={{ width: '100%', height: '100%' }}
                                config={{ displayModeBar: false }}
                            />
                        </div>

                    </div>
                ) : (
                    <div className="h-full flex flex-col items-center justify-center bg-white rounded-2xl border border-slate-200 text-slate-400 min-h-[400px]">
                        <RefreshCw size={48} className="mb-4 opacity-20" />
                        <p>Enter signals and click Simulate</p>
                    </div>
                )}
            </div>
        </div>
    );
};

export default ConvolutionLab;
