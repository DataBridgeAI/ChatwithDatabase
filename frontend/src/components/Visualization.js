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

const COLORS = [
  "#0088FE",
  "#00C49F",
  "#FFBB28",
  "#FF8042",
  "#8884d8",
  "#82ca9d",
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
    if (!queryResults || queryResults.length === 0) return;

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

  if (!queryResults || !showVisualization || chartOptions.length === 0) {
    return null;
  }

  const renderChart = () => {
    if (!chartType) return null;

    switch (chartType) {
      case "Bar":
        return (
          <ResponsiveContainer width="100%" height={400}>
            <BarChart data={queryResults}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey={xAxis} />
              <YAxis />
              <Tooltip />
              <Legend />
              <Bar dataKey={yAxis} fill="#8884d8" name={yAxis}>
                {colorBy &&
                  queryResults.map((entry, index) => (
                    <Cell
                      key={`cell-${index}`}
                      fill={COLORS[index % COLORS.length]}
                    />
                  ))}
              </Bar>
            </BarChart>
          </ResponsiveContainer>
        );

      case "Line":
        return (
          <ResponsiveContainer width="100%" height={400}>
            <LineChart data={queryResults}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey={xAxis} />
              <YAxis />
              <Tooltip />
              <Legend />
              <Line
                type="monotone"
                dataKey={yAxis}
                stroke="#8884d8"
                name={yAxis}
              />
            </LineChart>
          </ResponsiveContainer>
        );

      case "Pie":
        return (
          <ResponsiveContainer width="100%" height={400}>
            <PieChart>
              <Pie
                data={queryResults}
                cx="50%"
                cy="50%"
                labelLine={true}
                label={({ name, percent }) =>
                  `${name}: ${(percent * 100).toFixed(0)}%`
                }
                outerRadius={150}
                fill="#8884d8"
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
              <Tooltip />
              <Legend />
            </PieChart>
          </ResponsiveContainer>
        );

      case "Scatter":
        return (
          <ResponsiveContainer width="100%" height={400}>
            <ScatterChart>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey={xAxis} type="number" name={xAxis} />
              <YAxis dataKey={yAxis} type="number" name={yAxis} />
              <Tooltip cursor={{ strokeDasharray: "3 3" }} />
              <Legend />
              <Scatter
                name={`${xAxis} vs ${yAxis}`}
                data={queryResults}
                fill="#8884d8"
              />
            </ScatterChart>
          </ResponsiveContainer>
        );

      case "Histogram":
        // For histogram, we'll use a bar chart with frequency count
        // This is a simplified version
        return (
          <ResponsiveContainer width="100%" height={400}>
            <BarChart data={queryResults}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey={xAxis} />
              <YAxis />
              <Tooltip />
              <Legend />
              <Bar dataKey={xAxis} fill="#8884d8" />
            </BarChart>
          </ResponsiveContainer>
        );

      default:
        return null;
    }
  };

  return (
    <div className="mt-8">
      <h2 className="text-xl font-semibold mb-4">📈 Data Visualization</h2>

      <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-6">
        <div>
          <label className="block text-sm font-medium mb-1">Chart Type</label>
          <select
            className="w-full p-2 border rounded"
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
          <label className="block text-sm font-medium mb-1">X-Axis</label>
          <select
            className="w-full p-2 border rounded"
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
            <label className="block text-sm font-medium mb-1">
              Y-Axis / Values
            </label>
            <select
              className="w-full p-2 border rounded"
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
              <label className="block text-sm font-medium mb-1">
                Color By (optional)
              </label>
              <select
                className="w-full p-2 border rounded"
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

      <div className="bg-white p-4 rounded-lg border shadow-sm">
        {renderChart()}
      </div>
    </div>
  );
};

export default Visualization;
