import React from 'react';
import Plot from 'react-plotly.js';

const Visualizer = ({ xData, yData, title, xLabel, yLabel, plotType = 'line', color = '#2563eb' }) => {
    // plotType: 'line' | 'stem'

    // Safety check to prevent crashes if API returns partial or null data
    if (!xData || !yData) {
        return (
            <div className="w-full h-80 bg-white rounded-lg shadow-sm border border-slate-200 flex items-center justify-center text-slate-400">
                <p>No Data for {title}</p>
            </div>
        );
    }

    try {
        // Ensure lengths match to avoid Plotly errors
        const len = Math.min(xData.length, yData.length);
        if (len === 0) throw new Error("Empty Data");

        const safeX = xData.slice(0, len);
        const safeY = yData.slice(0, len);

        let data = [];
        if (plotType === 'stem') {
            data = [
                // Stems (vertical lines)
                ...safeX.map((x, i) => ({
                    x: [x, x],
                    y: [0, safeY[i]],
                    mode: 'lines',
                    line: { color: color, width: 2 },
                    type: 'scatter',
                    showlegend: false,
                    hoverinfo: 'none'
                })),
                // Markers (tops)
                {
                    x: safeX,
                    y: safeY,
                    mode: 'markers',
                    marker: { color: color, size: 8 },
                    type: 'scatter',
                    name: title
                }
            ];
        } else {
            // Standard Line Plot
            data = [{
                x: safeX,
                y: safeY,
                type: 'scatter',
                mode: 'lines',
                line: { color: color, width: 2.5 },
                fill: 'tozeroy',
                fillcolor: color + '20'
            }];
        }

        return (
            <div className="w-full h-80 bg-white rounded-lg shadow-sm border border-slate-200 p-2 relative">
                <Plot
                    data={data}
                    layout={{
                        autosize: true,
                        title: { text: title, font: { family: 'Inter', size: 16, color: '#1e293b' } },
                        xaxis: { title: xLabel, zeroline: true, showgrid: true, gridcolor: '#f1f5f9' },
                        yaxis: { title: yLabel, zeroline: false, showgrid: true, gridcolor: '#f1f5f9' },
                        margin: { t: 40, r: 20, b: 40, l: 50 },
                        showlegend: false,
                    }}
                    useResizeHandler={true}
                    style={{ width: '100%', height: '100%' }}
                    config={{
                        displayModeBar: true,
                        modeBarButtonsToRemove: ['lasso2d', 'select2d'],
                        displaylogo: false
                    }}
                />
            </div>
        );
    } catch (err) {
        console.error("Visualizer Error:", err);
        return (
            <div className="w-full h-80 bg-red-50 rounded-lg border border-red-200 flex flex-col items-center justify-center text-red-400">
                <p>Visualization Error</p>
                <p className="text-xs">{err.message}</p>
            </div>
        );
    }
};

export default Visualizer;
