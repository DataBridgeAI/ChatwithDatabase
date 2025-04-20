import React, { useState, useEffect, useCallback } from "react";
import { useAppContext } from "../context/AppContext";
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  BarChart,
  Bar,
  PieChart,
  Pie,
  Cell,
  ResponsiveContainer,
  Scatter,
  ScatterChart,
} from "recharts";

// Modern color palette for glass theme
const COLORS = [
  "#60a5fa", // blue
  "#4ade80", // green
  "#f59e0b", // amber
  "#ec4899", // pink
  "#8b5cf6", // purple
  "#14b8a6", // teal
];

const Visualization = () => {
  const { queryResults, showVisualization } = useAppContext();
  const [chartType, setChartType] = useState("");
  const [xAxis, setXAxis] = useState("");
  const [yAxis, setYAxis] = useState("");
  const [colorBy, setColorBy] = useState("");
  const [numColumns, setNumColumns] = useState([]);
  const [catColumns, setCatColumns] = useState([]);
  const [chartOptions, setChartOptions] = useState([]);

  const analyzeColumns = useCallback(() => {
    if (!queryResults || queryResults.length === 0) {
      return;
    }

    const sample = queryResults[0];
    const numCols = [];
    const catCols = [];

    // Detect column types
    Object.entries(sample).forEach(([key, value]) => {
      if (typeof value === "number") {
        numCols.push(key);
      } else {
        catCols.push(key);
      }
    });

    setNumColumns(numCols);
    setCatColumns(catCols);

    // Set available chart options based on data types
    const options = [];

    if (numCols.length === 0) {
      // No visualization possible for completely categorical data
      setChartOptions([]);
      return;
    }

    if (numCols.length >= 2) {
      options.push("Scatter", "Line");
    }

    if (numCols.length >= 1 && catCols.length >= 1) {
      options.push("Bar");
      options.push("Pie");
    }

    if (numCols.length >= 1) {
      options.push("Histogram");
    }

    setChartOptions(options);

    // Set default chart type and axes
    if (options.length > 0) {
      setChartType(options[0]);

      if (options[0] === "Bar") {
        setXAxis(catCols[0]);
        setYAxis(numCols[0]);
      } else if (options[0] === "Pie") {
        setXAxis(catCols[0]);
        setYAxis(numCols[0]);
      } else if (options[0] === "Scatter" || options[0] === "Line") {
        setXAxis(numCols[0]);
        setYAxis(numCols[1] || numCols[0]);
      } else if (options[0] === "Histogram") {
        setXAxis(numCols[0]);
      }

      if (catCols.length > 0) {
        setColorBy(catCols[0]);
      }
    }
  }, [queryResults]);

  useEffect(() => {
    if (queryResults && showVisualization) {
      analyzeColumns();
    }
  }, [queryResults, showVisualization, analyzeColumns]);

  if (!queryResults || !showVisualization) {
    return null;
  }

  if (chartOptions.length === 0) {
    return (
      <div className="glass p-6 rounded-xl border border-[#334155]/50 shadow-lg">
        <h2 className="text-xl font-semibold mb-4 text-white">📈 Data Visualization</h2>
        <p className="text-gray-300">No suitable visualizations available for this dataset. The data may not contain numerical columns required for charts.</p>
      </div>
    );
  }

  const renderChart = () => {
    if (!chartType) return null;

    // Common chart theme props
    const chartTheme = {
      style: {
        background: 'transparent',
      },
    };

    // Text styling for the chart
    const textStyle = {
      fill: '#94a3b8',
      fontSize: 12,
    };

    // Grid styling
    const gridStyle = {
      stroke: '#334155',
      strokeDasharray: '3 3',
      opacity: 0.6,
    };

    // Tooltip styling
    const tooltipStyle = {
      backgroundColor: 'rgba(30, 41, 59, 0.9)',
      borderColor: '#475569',
      color: '#f1f5f9',
    };

    switch (chartType) {
      case "Bar":
        return (
          <ResponsiveContainer width="100%" height={400}>
            <BarChart data={queryResults} {...chartTheme}>
              <CartesianGrid {...gridStyle} />
              <XAxis 
                dataKey={xAxis} 
                tick={textStyle} 
                axisLine={{ stroke: '#475569' }} 
              />
              <YAxis 
                tick={textStyle} 
                axisLine={{ stroke: '#475569' }} 
              />
              <Tooltip 
                contentStyle={tooltipStyle}
                cursor={{fill: 'rgba(51, 65, 85, 0.4)'}}
              />
              <Legend
                wrapperStyle={{ color: '#94a3b8' }}
              />
              <Bar dataKey={yAxis} name={yAxis} radius={[4, 4, 0, 0]}>
                {colorBy
                  ? queryResults.map((entry, index) => (
                      <Cell
                        key={`cell-${index}`}
                        fill={COLORS[index % COLORS.length]}
                      />
                    ))
                  : <Cell fill={COLORS[0]} />
                }
              </Bar>
            </BarChart>
          </ResponsiveContainer>
        );

      case "Line":
        return (
          <ResponsiveContainer width="100%" height={400}>
            <LineChart data={queryResults} {...chartTheme}>
              <CartesianGrid {...gridStyle} />
              <XAxis 
                dataKey={xAxis} 
                tick={textStyle} 
                axisLine={{ stroke: '#475569' }}
              />
              <YAxis 
                tick={textStyle} 
                axisLine={{ stroke: '#475569' }}
              />
              <Tooltip
                contentStyle={tooltipStyle}
              />
              <Legend 
                wrapperStyle={{ color: '#94a3b8' }}
              />
              <Line
                type="monotone"
                dataKey={yAxis}
                stroke={COLORS[0]}
                strokeWidth={2}
                dot={{ fill: COLORS[0], r: 4, strokeWidth: 0 }}
                activeDot={{ r: 6, strokeWidth: 0 }}
                name={yAxis}
              />
            </LineChart>
          </ResponsiveContainer>
        );

      case "Pie":
        return (
          <ResponsiveContainer width="100%" height={400}>
            <PieChart {...chartTheme}>
              <Pie
                data={queryResults}
                cx="50%"
                cy="50%"
                labelLine={true}
                label={({ name, percent }) =>
                  `${name}: ${(percent * 100).toFixed(0)}%`
                }
                outerRadius={150}
                dataKey={yAxis}
                nameKey={xAxis}
              >
                {queryResults.map((entry, index) => (
                  <Cell
                    key={`cell-${index}`}
                    fill={COLORS[index % COLORS.length]}
                  />
                ))}
              </Pie>
              <Tooltip
                contentStyle={tooltipStyle}
              />
              <Legend 
                wrapperStyle={{ color: '#94a3b8' }}
              />
            </PieChart>
          </ResponsiveContainer>
        );

      case "Scatter":
        return (
          <ResponsiveContainer width="100%" height={400}>
            <ScatterChart {...chartTheme}>
              <CartesianGrid {...gridStyle} />
              <XAxis 
                dataKey={xAxis} 
                type="number" 
                name={xAxis} 
                tick={textStyle} 
                axisLine={{ stroke: '#475569' }}
              />
              <YAxis 
                dataKey={yAxis} 
                type="number" 
                name={yAxis} 
                tick={textStyle} 
                axisLine={{ stroke: '#475569' }}
              />
              <Tooltip
                cursor={{ strokeDasharray: "3 3", stroke: '#475569' }}
                contentStyle={tooltipStyle}
              />
              <Legend 
                wrapperStyle={{ color: '#94a3b8' }}
              />
              <Scatter
                name={`${xAxis} vs ${yAxis}`}
                data={queryResults}
                fill={COLORS[0]}
              />
            </ScatterChart>
          </ResponsiveContainer>
        );

      case "Histogram":
        // For histogram, we'll use a bar chart with frequency count
        return (
          <ResponsiveContainer width="100%" height={400}>
            <BarChart data={queryResults} {...chartTheme}>
              <CartesianGrid {...gridStyle} />
              <XAxis 
                dataKey={xAxis} 
                tick={textStyle} 
                axisLine={{ stroke: '#475569' }}
              />
              <YAxis 
                tick={textStyle} 
                axisLine={{ stroke: '#475569' }}
              />
              <Tooltip
                contentStyle={tooltipStyle}
                cursor={{fill: 'rgba(51, 65, 85, 0.4)'}}
              />
              <Legend 
                wrapperStyle={{ color: '#94a3b8' }}
              />
              <Bar dataKey={xAxis} fill={COLORS[0]} radius={[4, 4, 0, 0]} />
            </BarChart>
          </ResponsiveContainer>
        );

      default:
        return null;
    }
  };

  return (
    <div className="fade-in">
      <h2 className="text-xl font-semibold mb-4 text-white">📈 Data Visualization</h2>

      <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-6">
        <div>
          <label className="block text-sm font-medium mb-1 text-gray-300">Chart Type</label>
          <select
            className="w-full p-2 glass-light rounded-full text-white border border-[#334155]/50 focus:outline-none focus:ring-2 focus:ring-blue-500"
            value={chartType}
            onChange={(e) => setChartType(e.target.value)}
          >
            {chartOptions.map((option) => (
              <option key={option} value={option}>
                {option}
              </option>
            ))}
          </select>
        </div>

        <div>
          <label className="block text-sm font-medium mb-1 text-gray-300">X-Axis</label>
          <select
            className="w-full p-2 glass-light rounded-full text-white border border-[#334155]/50 focus:outline-none focus:ring-2 focus:ring-blue-500"
            value={xAxis}
            onChange={(e) => setXAxis(e.target.value)}
            disabled={!chartType}
          >
            {(chartType === "Bar" || chartType === "Pie"
              ? catColumns
              : chartType === "Histogram"
              ? numColumns
              : [...numColumns, ...catColumns]
            ).map((col) => (
              <option key={col} value={col}>
                {col}
              </option>
            ))}
          </select>
        </div>

        {(chartType === "Bar" ||
          chartType === "Line" ||
          chartType === "Scatter" ||
          chartType === "Pie") && (
          <div>
            <label className="block text-sm font-medium mb-1 text-gray-300">
              Y-Axis / Values
            </label>
            <select
              className="w-full p-2 glass-light rounded-full text-white border border-[#334155]/50 focus:outline-none focus:ring-2 focus:ring-blue-500"
              value={yAxis}
              onChange={(e) => setYAxis(e.target.value)}
              disabled={!chartType}
            >
              {numColumns.map((col) => (
                <option key={col} value={col}>
                  {col}
                </option>
              ))}
            </select>
          </div>
        )}

        {catColumns.length > 0 &&
          (chartType === "Line" ||
            chartType === "Scatter" ||
            chartType === "Bar") && (
            <div>
              <label className="block text-sm font-medium mb-1 text-gray-300">
                Color By (optional)
              </label>
              <select
                className="w-full p-2 glass-light rounded-full text-white border border-[#334155]/50 focus:outline-none focus:ring-2 focus:ring-blue-500"
                value={colorBy}
                onChange={(e) => setColorBy(e.target.value)}
              >
                <option value="">None</option>
                {catColumns.map((col) => (
                  <option key={col} value={col}>
                    {col}
                  </option>
                ))}
              </select>
            </div>
          )}
      </div>

      <div className="glass p-6 rounded-xl border border-[#334155]/50 shadow-lg">
        {renderChart()}
      </div>
    </div>
  );
};

export default Visualization;