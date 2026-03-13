import React from 'react';
import Plot from 'react-plotly.js';

const Visualizer = ({ xData, yData, title, xLabel, yLabel, plotType = 'line', color = '#2563eb' }) => {
    // plotType: 'line' | 'stem'
    const renderState = (message, detail = null, tone = 'neutral') => {
        const toneClasses = tone === 'error'
            ? 'bg-red-50 border-red-200 text-red-400'
            : 'bg-white border-slate-200 text-slate-400';

        return (
            <div className={`w-full h-80 rounded-lg shadow-sm border flex flex-col items-center justify-center ${toneClasses}`}>
                <p>{message}</p>
                {detail ? <p className="text-xs">{detail}</p> : null}
            </div>
        );
    };

    const getRgba = (hex, alpha) => {
        if (!hex) return `rgba(99, 102, 241, ${alpha})`;
        if (hex.startsWith('#')) {
            const r = parseInt(hex.slice(1, 3), 16);
            const g = parseInt(hex.slice(3, 5), 16);
            const b = parseInt(hex.slice(5, 7), 16);
            return `rgba(${r}, ${g}, ${b}, ${alpha})`;
        }

        return hex;
    };

    // Safety check to prevent crashes if API returns partial or null data
    if (!xData || !yData) {
        return renderState(`No Data for ${title}`);
    }

    const validData = Array.isArray(xData) && Array.isArray(yData) && xData.length > 0;
    if (!validData) {
        return renderState(`No Data for ${title}`);
    }

    const safeX = xData;
    const safeY = yData;
    const len = safeX.length;

    let data = [];
    if (plotType === 'stem') {
        const stemX = [];
        const stemY = [];
        for (let i = 0; i < len; i++) {
            stemX.push(safeX[i], safeX[i], null);
            stemY.push(0, safeY[i], null);
        }

        data = [
            {
                x: stemX,
                y: stemY,
                mode: 'lines',
                line: { color: color, width: 1.5 },
                type: 'scatter',
                hoverinfo: 'none',
                showlegend: false
            },
            {
                x: safeX,
                y: safeY,
                mode: 'markers',
                marker: { color: color, size: 6 },
                type: 'scatter',
                name: title
            }
        ];
    } else {
        data = [{
            x: safeX,
            y: safeY,
            type: 'scatter',
            mode: 'lines',
            line: { color: color, width: 2.5 },
            fill: 'tozeroy',
            fillcolor: getRgba(color, 0.2)
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
};

export default Visualizer;
