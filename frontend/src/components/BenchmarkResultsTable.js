import React from "react";

// BenchmarkResultsTable Component
function BenchmarkResultsTable({ resultsText }) {
  // Parse the text into rows (skip lines that are just separators)
  const lines = resultsText
    .split("\n")
    .filter((line) => line.trim() && !/^[-+|]+$/.test(line));
  // Find header and data rows
  const headerIdx = lines.findIndex((line) => /Metric/i.test(line));
  if (headerIdx === -1) return <div>No table data found.</div>;
  const headerLine = lines[headerIdx];
  const colNames = headerLine
    .split("|")
    .map((s) => s.trim())
    .filter(Boolean);
  const dataRows = lines
    .slice(headerIdx + 1)
    .map((line) =>
      line
        .split("|")
        .map((s) => s.trim())
        .filter(Boolean)
    )
    .filter((row) => row.length === colNames.length);

  if (dataRows.length === 0) return <div>No benchmark table data found.</div>;

  return (
    <div style={{ overflowX: "auto" }}>
      <table className="benchmark-table">
        <thead>
          <tr>
            {colNames.map((col, idx) => (
              <th key={idx}>{col}</th>
            ))}
          </tr>
        </thead>
        <tbody>
          {dataRows.map((row, i) => (
            <tr key={i}>
              {row.map((cell, j) => (
                <td key={j}>{cell}</td>
              ))}
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}

export default BenchmarkResultsTable;
