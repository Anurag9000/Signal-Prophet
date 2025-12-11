import React, { useState, useEffect } from 'react';
import {
    Chart as ChartJS,
    LinearScale,
    PointElement,
    LineElement,
    Tooltip,
    Legend
} from 'chart.js';
import { Scatter } from 'react-chartjs-2';
import clsx from 'clsx';

import Plot from 'react-plotly.js';

ChartJS.register(LinearScale, PointElement, LineElement, Tooltip, Legend);

const ROCExplorer = () => {
    const [domain, setDomain] = useState('laplace'); // 'laplace' | 'z'
    const [causality, setCausality] = useState('causal'); // 'causal' | 'anticausal'
    const [stability, setStability] = useState('stable'); // 'stable' | 'unstable'
    const [poles, setPoles] = useState([]);
    const [zeros, setZeros] = useState([]);
    const [newPole, setNewPole] = useState({ r: -1, i: 0 });
    const [newZero, setNewZero] = useState({ r: 0, i: 0 });
    const [analysis, setAnalysis] = useState({ stable: true, html: "System is stable (no poles)." });
    const [updateKey, setUpdateKey] = useState(0);

    // 3D Visualization State
    const [viewMode, setViewMode] = useState('2d'); // '2d' | '3d'
    const [surfaceData, setSurfaceData] = useState(null);
    const [loading3d, setLoading3d] = useState(false);

    // Transfer function input
    const [transferFunction, setTransferFunction] = useState('');
    const [tfLoading, setTfLoading] = useState(false);

    // Handle transfer function parsing
    const handleParseTF = async () => {
        if (!transferFunction.trim()) return;

        setTfLoading(true);
        try {
            const variable = domain === 'laplace' ? 's' : 'z';
            const res = await fetch('http://localhost:8000/parse_transfer_function', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ expression: transferFunction, variable })
            });
            const data = await res.json();

            if (data.error) {
                alert(`Error: ${data.error}`);
            } else {
                setPoles(data.poles || []);
                setZeros(data.zeros || []);
                setUpdateKey(prev => prev + 1);
            }
        } catch (e) {
            alert(`Failed to parse: ${e.message}`);
        } finally {
            setTfLoading(false);
        }
    };

    // --- Analysis Logic ---
    useEffect(() => {
        let html = "";
        let isStable = false;
        let isValid = true;

        if (poles.length === 0) {
            isStable = true;
            html = "With no poles, the ROC covers the entire plane.";
            if (zeros.length > 0) html += ` (System has ${zeros.length} zeroes).`;
        } else {
            if (domain === 'laplace') {
                const realParts = poles.map(p => p.r);
                const maxReal = Math.max(...realParts);
                const minReal = Math.min(...realParts);

                if (causality === 'causal') {
                    html = `Causal System: ROC is Re(s) > ${maxReal.toFixed(2)}. `;
                    // Stable if ROC includes jω axis (Re(s) = 0)
                    const actuallyStable = maxReal < 0;

                    if (stability === 'stable' && !actuallyStable) {
                        isValid = false;
                        html = `❌ INVALID: Causal system with rightmost pole at Re(s) = ${maxReal.toFixed(2)} CANNOT be stable (ROC excludes jω axis).`;
                    } else if (stability === 'unstable' && actuallyStable) {
                        isValid = false;
                        html = `❌ INVALID: Causal system with rightmost pole at Re(s) = ${maxReal.toFixed(2)} CANNOT be unstable (ROC includes jω axis).`;
                    } else {
                        isStable = actuallyStable;
                        html += isStable ? "System is STABLE (ROC includes jω axis)." : "System is UNSTABLE (ROC excludes jω axis).";
                    }
                } else {
                    html = `Anti-Causal System: ROC is Re(s) < ${minReal.toFixed(2)}. `;
                    const actuallyStable = minReal > 0;

                    if (stability === 'stable' && !actuallyStable) {
                        isValid = false;
                        html = `❌ INVALID: Anti-causal system with leftmost pole at Re(s) = ${minReal.toFixed(2)} CANNOT be stable (ROC excludes jω axis).`;
                    } else if (stability === 'unstable' && actuallyStable) {
                        isValid = false;
                        html = `❌ INVALID: Anti-causal system with leftmost pole at Re(s) = ${minReal.toFixed(2)} CANNOT be unstable (ROC includes jω axis).`;
                    } else {
                        isStable = actuallyStable;
                        html += isStable ? "System is STABLE (ROC includes jω axis)." : "System is UNSTABLE (ROC excludes jω axis).";
                    }
                }
            } else {
                // Z Logic
                const mags = poles.map(p => Math.sqrt(p.r ** 2 + p.i ** 2));
                const maxMag = Math.max(...mags);
                const minMag = Math.min(...mags);

                if (causality === 'causal') {
                    html = `Causal System: ROC is |z| > ${maxMag.toFixed(2)}. `;
                    const actuallyStable = maxMag < 1;

                    if (stability === 'stable' && !actuallyStable) {
                        isValid = false;
                        html = `❌ INVALID: Causal system with outermost pole at |z| = ${maxMag.toFixed(2)} CANNOT be stable (ROC excludes unit circle).`;
                    } else if (stability === 'unstable' && actuallyStable) {
                        isValid = false;
                        html = `❌ INVALID: Causal system with outermost pole at |z| = ${maxMag.toFixed(2)} CANNOT be unstable (ROC includes unit circle).`;
                    } else {
                        isStable = actuallyStable;
                        html += isStable ? "System is STABLE (ROC includes unit circle)." : "System is UNSTABLE (ROC excludes unit circle).";
                    }
                } else {
                    html = `Anti-Causal System: ROC is |z| < ${minMag.toFixed(2)}. `;
                    const actuallyStable = minMag > 1;

                    if (stability === 'stable' && !actuallyStable) {
                        isValid = false;
                        html = `❌ INVALID: Anti-causal system with innermost pole at |z| = ${minMag.toFixed(2)} CANNOT be stable (ROC excludes unit circle).`;
                    } else if (stability === 'unstable' && actuallyStable) {
                        isValid = false;
                        html = `❌ INVALID: Anti-causal system with innermost pole at |z| = ${minMag.toFixed(2)} CANNOT be unstable (ROC includes unit circle).`;
                    } else {
                        isStable = actuallyStable;
                        html += isStable ? "System is STABLE (ROC includes unit circle)." : "System is UNSTABLE (ROC excludes unit circle).";
                    }
                }
            }
        }
        setAnalysis({ stable: isStable, html, valid: isValid });
    }, [poles, zeros, domain, causality, stability, updateKey]);

    // Fetch 3D Data when needed
    useEffect(() => {
        if (viewMode === '3d') {
            const fetchSurface = async () => {
                setLoading3d(true);
                try {
                    const res = await fetch('http://localhost:8000/roc/surface', {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify({
                            poles,
                            zeros,
                            gain: 1.0,
                            domain,
                            roc_type: causality
                        })
                    });
                    const data = await res.json();
                    setSurfaceData(data);
                } catch (e) {
                    console.error("Failed to load 3D surface", e);
                }
                setLoading3d(false);
            };
            fetchSurface();
        }
    }, [viewMode, poles, zeros, domain, causality]);

    // --- Chart Plugins ---
    const rocPlugin = {
        id: 'rocPlugin',
        beforeDraw: (chart) => {
            const ctx = chart.ctx;
            const xAxis = chart.scales.x;
            const yAxis = chart.scales.y;
            const topY = yAxis.getPixelForValue(yAxis.max);
            const bottomY = yAxis.getPixelForValue(yAxis.min);

            ctx.save();

            // Draw all pole boundaries first (dotted lines/circles)
            if (poles.length > 0) {
                ctx.strokeStyle = '#94a3b8';
                ctx.setLineDash([3, 3]);
                ctx.lineWidth = 1;

                if (domain === 'laplace') {
                    const realParts = poles.map(p => p.r);
                    const uniqueReals = [...new Set(realParts)];

                    uniqueReals.forEach(re => {
                        const x = xAxis.getPixelForValue(re);
                        ctx.beginPath();
                        ctx.moveTo(x, topY);
                        ctx.lineTo(x, bottomY);
                        ctx.stroke();
                    });
                } else {
                    const mags = poles.map(p => Math.sqrt(p.r ** 2 + p.i ** 2));
                    const uniqueMags = [...new Set(mags.map(m => m.toFixed(2)))].map(Number);
                    const center = { x: xAxis.getPixelForValue(0), y: yAxis.getPixelForValue(0) };
                    const oneX = xAxis.getPixelForValue(1);
                    const zeroX = xAxis.getPixelForValue(0);
                    const pxUnit = Math.abs(oneX - zeroX);

                    uniqueMags.forEach(mag => {
                        ctx.beginPath();
                        ctx.arc(center.x, center.y, mag * pxUnit, 0, 2 * Math.PI);
                        ctx.stroke();
                    });
                }
            }

            // If no poles, entire plane is ROC
            if (poles.length === 0) {
                ctx.fillStyle = 'rgba(16, 185, 129, 0.15)';
                ctx.fillRect(xAxis.left, yAxis.top, xAxis.width, yAxis.height);
                ctx.restore();
                return;
            }

            // Draw ROC region based ONLY on causality and poles
            // Color: Blue for Causal, Green for Anti-Causal
            const rocColor = causality === 'causal' ? 'rgba(59, 130, 246, 0.2)' : 'rgba(34, 197, 94, 0.2)';

            if (domain === 'laplace') {
                const realParts = poles.map(p => p.r);
                const maxReal = Math.max(...realParts);
                const minReal = Math.min(...realParts);

                ctx.fillStyle = rocColor;

                if (causality === 'causal') {
                    // ROC: Right of rightmost pole
                    const startX = xAxis.getPixelForValue(maxReal);
                    const endX = xAxis.getPixelForValue(xAxis.max);
                    ctx.fillRect(startX, topY, endX - startX, bottomY - topY);
                } else {
                    // ROC: Left of leftmost pole
                    const startX = xAxis.getPixelForValue(xAxis.min);
                    const endX = xAxis.getPixelForValue(minReal);
                    ctx.fillRect(startX, topY, endX - startX, bottomY - topY);
                }
            } else {
                const mags = poles.map(p => Math.sqrt(p.r ** 2 + p.i ** 2));
                const maxMag = Math.max(...mags);
                const minMag = Math.min(...mags);
                const center = { x: xAxis.getPixelForValue(0), y: yAxis.getPixelForValue(0) };
                const oneX = xAxis.getPixelForValue(1);
                const zeroX = xAxis.getPixelForValue(0);
                const pxUnit = Math.abs(oneX - zeroX);

                ctx.fillStyle = rocColor;
                ctx.beginPath();

                if (causality === 'causal') {
                    // ROC: Outside outermost pole
                    ctx.arc(center.x, center.y, 3000, 0, 2 * Math.PI);
                    ctx.arc(center.x, center.y, maxMag * pxUnit, 0, 2 * Math.PI, true);
                    ctx.fill();
                } else {
                    // ROC: Inside innermost pole
                    ctx.arc(center.x, center.y, minMag * pxUnit, 0, 2 * Math.PI);
                    ctx.fill();
                }
            }

            // Draw ROC boundary (bold line at pole boundary)
            ctx.setLineDash([5, 5]);
            ctx.lineWidth = 3;
            ctx.strokeStyle = causality === 'causal' ? '#3b82f6' : '#22c55e';

            if (domain === 'laplace') {
                const realParts = poles.map(p => p.r);
                const boundaryX = causality === 'causal'
                    ? xAxis.getPixelForValue(Math.max(...realParts))
                    : xAxis.getPixelForValue(Math.min(...realParts));

                ctx.beginPath();
                ctx.moveTo(boundaryX, topY);
                ctx.lineTo(boundaryX, bottomY);
                ctx.stroke();
            } else {
                const mags = poles.map(p => Math.sqrt(p.r ** 2 + p.i ** 2));
                const boundaryMag = causality === 'causal' ? Math.max(...mags) : Math.min(...mags);
                const center = { x: xAxis.getPixelForValue(0), y: yAxis.getPixelForValue(0) };
                const oneX = xAxis.getPixelForValue(1);
                const zeroX = xAxis.getPixelForValue(0);
                const pxUnit = Math.abs(oneX - zeroX);

                ctx.beginPath();
                ctx.arc(center.x, center.y, boundaryMag * pxUnit, 0, 2 * Math.PI);
                ctx.stroke();
            }

            ctx.restore();
        }
    };

    const axesPlugin = {
        id: 'axesPlugin',
        beforeDraw: (chart) => {
            const ctx = chart.ctx;
            const xAxis = chart.scales.x;
            const yAxis = chart.scales.y;
            const cx = xAxis.getPixelForValue(0);
            const cy = yAxis.getPixelForValue(0);

            ctx.save();
            ctx.strokeStyle = '#9ca3af';
            ctx.lineWidth = 1;
            ctx.beginPath();
            ctx.moveTo(xAxis.left, cy);
            ctx.lineTo(xAxis.right, cy);
            ctx.moveTo(cx, yAxis.top);
            ctx.lineTo(cx, yAxis.bottom);
            ctx.stroke();

            // Critical boundary
            ctx.lineWidth = 2;
            ctx.strokeStyle = '#374151';
            if (domain === 'laplace') {
                ctx.beginPath();
                ctx.moveTo(cx, yAxis.top);
                ctx.lineTo(cx, yAxis.bottom);
                ctx.stroke();
            } else {
                const r = Math.abs(xAxis.getPixelForValue(1) - xAxis.getPixelForValue(0));
                ctx.setLineDash([2, 5]);
                ctx.beginPath();
                ctx.arc(cx, cy, r, 0, 2 * Math.PI);
                ctx.stroke();
                ctx.setLineDash([]);
            }
            ctx.restore();
        }
    };

    const data = {
        datasets: [
            {
                label: 'Poles',
                data: poles.map(p => ({ x: p.r, y: p.i })),
                pointStyle: 'crossRot',
                borderColor: domain === 'laplace' ? '#2563eb' : '#7c3aed',
                borderWidth: 2,
                pointRadius: 6,
                backgroundColor: 'transparent'
            },
            {
                label: 'Zeros',
                data: zeros.map(z => ({ x: z.r, y: z.i })),
                pointStyle: 'circle',
                borderColor: '#ef4444',
                borderWidth: 2,
                pointRadius: 6,
                backgroundColor: 'white'
            }
        ]
    };

    // Calculate dynamic axis limits based on poles and zeros
    const calculateAxisLimits = () => {
        if (poles.length === 0 && zeros.length === 0) {
            return { min: -5, max: 5 };
        }

        const allPoints = [...poles, ...zeros];
        const realParts = allPoints.map(p => p.r);
        const imagParts = allPoints.map(p => p.i);

        const maxReal = Math.max(...realParts);
        const minReal = Math.min(...realParts);
        const maxImag = Math.max(...imagParts);
        const minImag = Math.min(...imagParts);

        // Add 20% padding
        const realRange = maxReal - minReal;
        const imagRange = maxImag - minImag;
        const padding = Math.max(realRange, imagRange, 2) * 0.3;

        const xMin = Math.floor(minReal - padding);
        const xMax = Math.ceil(maxReal + padding);
        const yMin = Math.floor(minImag - padding);
        const yMax = Math.ceil(maxImag + padding);

        return {
            xMin: Math.min(xMin, -2),
            xMax: Math.max(xMax, 2),
            yMin: Math.min(yMin, -2),
            yMax: Math.max(yMax, 2)
        };
    };

    const axisLimits = calculateAxisLimits();

    const options = {
        responsive: true,
        maintainAspectRatio: false,
        scales: {
            x: {
                min: axisLimits.xMin || axisLimits.min,
                max: axisLimits.xMax || axisLimits.max,
                grid: { display: false }
            },
            y: {
                min: axisLimits.yMin || axisLimits.min,
                max: axisLimits.yMax || axisLimits.max,
                grid: { display: false }
            }
        },
        plugins: { legend: { display: true, position: 'top' } }
    };

    return (
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-0 border rounded-xl overflow-hidden shadow-sm bg-white border-slate-200">
            {/* Controls */}
            <div className="p-6 bg-slate-50 lg:col-span-1 space-y-6">
                <div>
                    <h3 className="text-xs font-bold text-slate-900 uppercase tracking-wider mb-4">Configuration</h3>

                    {/* Domain Switch */}
                    <div className="flex mb-4 bg-white p-1 rounded-lg border border-slate-200">
                        <button
                            onClick={() => { setDomain('laplace'); setPoles([]); setZeros([]); }}
                            className={clsx("flex-1 py-1 text-xs font-medium rounded transition", domain === 'laplace' ? "bg-blue-100 text-blue-700" : "text-slate-500 hover:bg-slate-50")}
                        >S-Plane</button>
                        <button
                            onClick={() => { setDomain('z'); setPoles([]); setZeros([]); }}
                            className={clsx("flex-1 py-1 text-xs font-medium rounded transition", domain === 'z' ? "bg-purple-100 text-purple-700" : "text-slate-500 hover:bg-slate-50")}
                        >Z-Plane</button>
                    </div>

                    {/* Transfer Function Input */}
                    <div className="mb-4 p-3 bg-white rounded-lg border border-indigo-200">
                        <label className="block text-xs font-semibold text-indigo-700 mb-2 uppercase">
                            Enter {domain === 'laplace' ? 'X(s)' : 'X(z)'}
                        </label>
                        <input
                            type="text"
                            value={transferFunction}
                            onChange={(e) => setTransferFunction(e.target.value)}
                            placeholder={domain === 'laplace' ? 'e.g., (s+1)/(s^2+2*s+1)' : 'e.g., (z-0.5)/(z^2-1.5*z+0.5)'}
                            className="w-full px-3 py-2 text-sm border border-slate-300 rounded font-mono mb-2"
                        />
                        <button
                            onClick={handleParseTF}
                            disabled={tfLoading}
                            className="w-full py-2 bg-indigo-600 text-white rounded font-bold text-xs hover:bg-indigo-700 transition disabled:bg-slate-400"
                        >
                            {tfLoading ? 'Parsing...' : 'Parse & Extract Poles/Zeros'}
                        </button>
                        <p className="text-xs text-slate-500 mt-2">
                            Use <code className="bg-slate-100 px-1 rounded">j</code> or <code className="bg-slate-100 px-1 rounded">i</code> for imaginary unit
                        </p>
                    </div>

                    <hr className="border-slate-200 my-4" />

                    {/* Causality */}
                    <div className="mb-4">
                        <label className="block text-xs font-semibold text-slate-500 mb-2 uppercase">Causality</label>
                        <div className="flex shadow-sm rounded-md">
                            <button onClick={() => setCausality('causal')} className={clsx("flex-1 py-2 text-xs border rounded-l-md", causality === 'causal' ? "bg-white border-blue-500 text-blue-700 ring-1 ring-blue-500" : "bg-white border-slate-300 text-slate-600 hover:bg-slate-50")}>Causal</button>
                            <button onClick={() => setCausality('anticausal')} className={clsx("flex-1 py-2 text-xs border border-l-0 rounded-r-md", causality === 'anticausal' ? "bg-white border-blue-500 text-blue-700 ring-1 ring-blue-500" : "bg-white border-slate-300 text-slate-600 hover:bg-slate-50")}>Anti-Causal</button>
                        </div>
                    </div>

                    {/* Stability */}
                    <div className="mb-4">
                        <label className="block text-xs font-semibold text-slate-500 mb-2 uppercase">Stability</label>
                        <div className="flex shadow-sm rounded-md">
                            <button onClick={() => setStability('stable')} className={clsx("flex-1 py-2 text-xs border rounded-l-md", stability === 'stable' ? "bg-white border-green-500 text-green-700 ring-1 ring-green-500" : "bg-white border-slate-300 text-slate-600 hover:bg-slate-50")}>Stable</button>
                            <button onClick={() => setStability('unstable')} className={clsx("flex-1 py-2 text-xs border border-l-0 rounded-r-md", stability === 'unstable' ? "bg-white border-red-500 text-red-700 ring-1 ring-red-500" : "bg-white border-slate-300 text-slate-600 hover:bg-slate-50")}>Unstable</button>
                        </div>
                    </div>

                    {/* Add Pole */}
                    <div className="space-y-2 mb-4">
                        <label className="block text-xs font-semibold text-slate-500 uppercase">Add Pole (X)</label>
                        <div className="flex gap-2">
                            <input type="number" step="0.5" value={newPole.r} onChange={e => setNewPole({ ...newPole, r: parseFloat(e.target.value) })} className="w-full px-2 py-1 text-sm border rounded" placeholder="Real" />
                            <input type="number" step="0.5" value={newPole.i} onChange={e => setNewPole({ ...newPole, i: parseFloat(e.target.value) })} className="w-full px-2 py-1 text-sm border rounded" placeholder="Imag" />
                        </div>
                        <button onClick={() => setPoles([...poles, newPole])} className="w-full py-1 bg-white border border-slate-300 text-xs font-medium rounded hover:bg-slate-50 text-blue-700">Add Pole</button>
                    </div>

                    {/* Add Zero */}
                    <div className="space-y-2 mb-4">
                        <label className="block text-xs font-semibold text-slate-500 uppercase">Add Zero (O)</label>
                        <div className="flex gap-2">
                            <input type="number" step="0.5" value={newZero.r} onChange={e => setNewZero({ ...newZero, r: parseFloat(e.target.value) })} className="w-full px-2 py-1 text-sm border rounded" placeholder="Real" />
                            <input type="number" step="0.5" value={newZero.i} onChange={e => setNewZero({ ...newZero, i: parseFloat(e.target.value) })} className="w-full px-2 py-1 text-sm border rounded" placeholder="Imag" />
                        </div>
                        <button onClick={() => setZeros([...zeros, newZero])} className="w-full py-1 bg-white border border-slate-300 text-xs font-medium rounded hover:bg-slate-50 text-red-600">Add Zero</button>
                    </div>

                    <hr className="border-slate-200" />

                    <button
                        onClick={() => setUpdateKey(prev => prev + 1)}
                        className="w-full py-2 bg-slate-800 text-white rounded-lg font-bold text-xs uppercase tracking-wider hover:bg-slate-900 transition"
                    >
                        Force Update Plot
                    </button>

                    {/* List */}
                    <div className="max-h-40 overflow-y-auto space-y-1 mt-4">
                        {poles.map((p, i) => (
                            <div key={`p-${i}`} className="flex justify-between items-center bg-blue-50 px-2 py-1 border border-blue-100 rounded text-xs">
                                <span className="font-mono text-blue-800">Pole: {p.r} {p.i >= 0 ? '+' : '-'} j{Math.abs(p.i)}</span>
                                <button onClick={() => setPoles(poles.filter((_, idx) => idx !== i))} className="text-red-400 hover:text-red-700">×</button>
                            </div>
                        ))}
                        {zeros.map((z, i) => (
                            <div key={`z-${i}`} className="flex justify-between items-center bg-red-50 px-2 py-1 border border-red-100 rounded text-xs">
                                <span className="font-mono text-red-800">Zero: {z.r} {z.i >= 0 ? '+' : '-'} j{Math.abs(z.i)}</span>
                                <button onClick={() => setZeros(zeros.filter((_, idx) => idx !== i))} className="text-red-400 hover:text-red-700">×</button>
                            </div>
                        ))}
                        {poles.length === 0 && zeros.length === 0 && <p className="text-xs text-slate-400 italic">No poles or zeros added.</p>}
                    </div>
                </div>
            </div>

            {/* Viz */}
            <div className="lg:col-span-2 p-6 bg-white flex flex-col relative h-[500px]">
                <div className="flex justify-between items-center mb-4">
                    <h3 className="font-bold text-slate-800">{domain === 'laplace' ? "S-Plane (Continuous)" : "Z-Plane (Discrete)"}</h3>
                    <div className="flex gap-2 items-center">
                        <div className="flex bg-slate-100 p-1 rounded-lg">
                            <button
                                onClick={() => setViewMode('2d')}
                                className={clsx("px-3 py-1 text-xs font-bold rounded-md transition", viewMode === '2d' ? "bg-white text-indigo-600 shadow-sm" : "text-slate-500")}
                            >2D ROC</button>
                            <button
                                onClick={() => setViewMode('3d')}
                                className={clsx("px-3 py-1 text-xs font-bold rounded-md transition", viewMode === '3d' ? "bg-white text-indigo-600 shadow-sm" : "text-slate-500")}
                            >3D Surface</button>
                        </div>
                        {viewMode === '2d' && (
                            <span className={clsx("px-2 py-1 rounded-full text-xs font-bold border", analysis.stable ? "bg-green-100 text-green-700 border-green-200" : "bg-red-100 text-red-700 border-red-200")}>
                                {analysis.stable ? "STABLE" : "UNSTABLE"}
                            </span>
                        )}
                    </div>
                </div>

                <div className="flex-1 relative w-full h-full">
                    {viewMode === '2d' ? (
                        <Scatter key={updateKey} data={data} options={options} plugins={[rocPlugin, axesPlugin]} />
                    ) : (
                        loading3d ? (
                            <div className="absolute inset-0 flex items-center justify-center bg-white/80 z-10">
                                <span className="animate-spin text-2xl">🌀</span>
                            </div>
                        ) : (
                            surfaceData && (
                                <Plot
                                    data={[{
                                        type: 'surface',
                                        x: surfaceData.x,
                                        y: surfaceData.y,
                                        z: surfaceData.z,
                                        colorscale: 'Viridis',
                                        showscale: false,
                                        contours: {
                                            z: { show: true, usecolormap: true, highlightcolor: "#42f462", project: { z: true } }
                                        }
                                    }]}
                                    layout={{
                                        autosize: true,
                                        margin: { l: 0, r: 0, b: 0, t: 0 },
                                        scene: {
                                            xaxis: { title: domain === 'laplace' ? 'σ (Sigma)' : 'r (Magnitude)' },
                                            yaxis: { title: 'jω (Freq)' },
                                            zaxis: { title: domain === 'laplace' ? '|X(s)|' : '|X(z)|' },
                                            aspectratio: { x: 1, y: 1, z: 0.7 }
                                        },
                                        annotations: (poles.length === 0 && zeros.length === 0) ? [{
                                            text: "No Poles/Zeros defined.<br>Plotting flat response.",
                                            x: 0, y: 0, z: 5,
                                            showarrow: false,
                                            font: { size: 14, color: 'red' },
                                            bgcolor: 'rgba(255,255,255,0.8)',
                                            bordercolor: 'red',
                                            borderwidth: 1
                                        }] : []
                                    }}
                                    useResizeHandler={true}
                                    style={{ width: "100%", height: "100%" }}
                                />
                            )
                        )
                    )}
                </div>
            </div>

            <div className={`mt-4 p-4 border rounded-lg ${analysis.valid === false ? 'bg-red-50 border-red-300' : 'bg-slate-50 border-slate-100'}`}>
                <p className={`text-sm font-medium ${analysis.valid === false ? 'text-red-900' : 'text-slate-900'}`}>
                    {analysis.valid === false ? '⚠️ Invalid Configuration' : 'Analysis'}
                </p>
                <p className={`text-sm ${analysis.valid === false ? 'text-red-700 font-medium' : 'text-slate-600'}`}>
                    {analysis.html}
                </p>
            </div>
        </div>

    );
};

export default ROCExplorer;
