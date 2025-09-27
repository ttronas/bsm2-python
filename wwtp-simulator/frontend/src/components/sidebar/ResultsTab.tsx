'use client';

import React, { useState, useMemo } from 'react';
import { FlowNode, FlowEdge, BSM2_VARIABLES } from '@/types';
import { BarChart3, Download, Eye, EyeOff } from 'lucide-react';

interface ResultsTabProps {
  nodes: FlowNode[];
  edges: FlowEdge[];
}

interface SimulationResults {
  [edgeId: string]: {
    timesteps: number[];
    data: { [variable: string]: number[] };
  };
}

export default function ResultsTab({ nodes, edges }: ResultsTabProps) {
  const [selectedEdge, setSelectedEdge] = useState<string>('');
  const [visibleVariables, setVisibleVariables] = useState<Set<string>>(new Set(['Q', 'TSS', 'SO']));

  // Mock data for demonstration - in real implementation, this would come from API
  const mockResults = useMemo(() => {
    if (edges.length === 0) return {};

    const mockData: SimulationResults = {};
    edges.forEach(edge => {
      const timesteps = Array.from({ length: 100 }, (_, i) => i * 15 / 1440); // 15 min intervals
      const data: { [variable: string]: number[] } = {};
      
      BSM2_VARIABLES.forEach(variable => {
        // Generate mock data with some realistic patterns
        data[variable] = timesteps.map((t) => {
          const baseValue = variable === 'Q' ? 20000 : 
                          variable === 'SO' ? 2 :
                          variable === 'TSS' ? 3000 :
                          variable === 'TEMP' ? 15 : 
                          Math.random() * 100;
          
          // Add some daily variation
          const dailyVariation = Math.sin(t * 2 * Math.PI) * baseValue * 0.2;
          const noise = (Math.random() - 0.5) * baseValue * 0.1;
          return Math.max(0, baseValue + dailyVariation + noise);
        });
      });
      
      mockData[edge.id] = { timesteps, data };
    });
    
    return mockData;
  }, [edges]);

  const handleVariableToggle = (variable: string) => {
    setVisibleVariables(prev => {
      const newSet = new Set(prev);
      if (newSet.has(variable)) {
        newSet.delete(variable);
      } else {
        newSet.add(variable);
      }
      return newSet;
    });
  };

  const handleExportResults = () => {
    if (Object.keys(mockResults).length === 0) {
      alert('No results available to export.');
      return;
    }

    const exportData = {
      nodes: nodes.map(n => ({ id: n.id, label: n.data.label, type: n.data.componentType })),
      edges: edges.map(e => ({ id: e.id, from: e.source, to: e.target })),
      results: mockResults,
    };

    const blob = new Blob([JSON.stringify(exportData, null, 2)], {
      type: 'application/json',
    });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `simulation_results_${new Date().toISOString().split('T')[0]}.json`;
    a.click();
    URL.revokeObjectURL(url);
  };

  const getEdgeLabel = (edgeId: string) => {
    const edge = edges.find(e => e.id === edgeId);
    if (!edge) return edgeId;
    
    const sourceNode = nodes.find(n => n.id === edge.source);
    const targetNode = nodes.find(n => n.id === edge.target);
    
    return `${sourceNode?.data.label || edge.source} → ${targetNode?.data.label || edge.target}`;
  };

  if (nodes.length === 0) {
    return (
      <div className="p-4">
        <h3 className="text-lg font-semibold mb-4 text-gray-900">Results</h3>
        <div className="text-center py-8">
          <div className="text-gray-400 mb-2">
            <div className="w-16 h-16 mx-auto mb-4 bg-gray-100 rounded-full flex items-center justify-center">
              📊
            </div>
          </div>
          <p className="text-gray-600">
            Add components and run a simulation to view results.
          </p>
        </div>
      </div>
    );
  }

  return (
    <div className="p-4 space-y-4">
      <div className="flex items-center justify-between">
        <h3 className="text-lg font-semibold text-gray-900">Simulation Results</h3>
        <button
          onClick={handleExportResults}
          disabled={Object.keys(mockResults).length === 0}
          className="p-2 text-gray-600 hover:text-gray-900 hover:bg-gray-100 rounded disabled:text-gray-400 disabled:cursor-not-allowed"
          title="Export Results"
        >
          <Download size={16} />
        </button>
      </div>

      {edges.length === 0 ? (
        <div className="text-center py-8">
          <p className="text-gray-600">
            Connect components to see flow data in results.
          </p>
        </div>
      ) : (
        <>
          {/* Edge Selection */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Select Connection
            </label>
            <select
              value={selectedEdge}
              onChange={(e) => setSelectedEdge(e.target.value)}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
            >
              <option value="">-- Select Connection --</option>
              {edges.map((edge) => (
                <option key={edge.id} value={edge.id}>
                  {getEdgeLabel(edge.id)}
                </option>
              ))}
            </select>
          </div>

          {/* Variable Selection */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Variables to Display
            </label>
            <div className="grid grid-cols-3 gap-2 max-h-40 overflow-y-auto">
              {BSM2_VARIABLES.map((variable) => (
                <button
                  key={variable}
                  onClick={() => handleVariableToggle(variable)}
                  className={`flex items-center gap-1 p-2 text-xs rounded border transition-colors ${
                    visibleVariables.has(variable)
                      ? 'bg-blue-50 border-blue-300 text-blue-700'
                      : 'bg-gray-50 border-gray-200 text-gray-600 hover:bg-gray-100'
                  }`}
                >
                  {visibleVariables.has(variable) ? (
                    <Eye size={12} />
                  ) : (
                    <EyeOff size={12} />
                  )}
                  {variable}
                </button>
              ))}
            </div>
          </div>

          {/* Results Display */}
          {selectedEdge && mockResults[selectedEdge] && (
            <div className="space-y-4">
              <h4 className="font-medium text-gray-800">
                Flow Data: {getEdgeLabel(selectedEdge)}
              </h4>

              {/* Summary Statistics */}
              <div className="grid grid-cols-2 gap-4">
                {Array.from(visibleVariables).slice(0, 4).map((variable) => {
                  const values = mockResults[selectedEdge].data[variable];
                  const avg = values.reduce((a, b) => a + b, 0) / values.length;
                  const max = Math.max(...values);
                  const min = Math.min(...values);

                  return (
                    <div key={variable} className="p-3 bg-gray-50 rounded-lg">
                      <div className="text-sm font-medium text-gray-700 mb-1">
                        {variable}
                      </div>
                      <div className="text-xs text-gray-600 space-y-1">
                        <div>Avg: {avg.toFixed(2)}</div>
                        <div>Min: {min.toFixed(2)}</div>
                        <div>Max: {max.toFixed(2)}</div>
                      </div>
                    </div>
                  );
                })}
              </div>

              {/* Simple Chart Visualization */}
              <div className="space-y-2">
                <div className="flex items-center gap-2">
                  <BarChart3 size={16} />
                  <span className="text-sm font-medium text-gray-700">Time Series Data</span>
                </div>
                
                {Array.from(visibleVariables).slice(0, 3).map((variable) => {
                  const values = mockResults[selectedEdge].data[variable];
                  const max = Math.max(...values);
                  const min = Math.min(...values);
                  
                  return (
                    <div key={variable} className="space-y-1">
                      <div className="flex justify-between text-xs text-gray-600">
                        <span>{variable}</span>
                        <span>{min.toFixed(1)} - {max.toFixed(1)}</span>
                      </div>
                      <div className="h-8 bg-gray-200 rounded overflow-hidden">
                        <div className="h-full flex">
                          {values.slice(0, 50).map((value, i) => {
                            const height = ((value - min) / (max - min)) * 100;
                            return (
                              <div
                                key={i}
                                className="flex-1 bg-blue-500 opacity-70"
                                style={{ height: `${height}%`, alignSelf: 'flex-end' }}
                              />
                            );
                          })}
                        </div>
                      </div>
                    </div>
                  );
                })}
              </div>

              {/* Data Table Preview */}
              <div className="space-y-2">
                <div className="text-sm font-medium text-gray-700">
                  Data Preview (First 10 timesteps)
                </div>
                <div className="overflow-x-auto">
                  <table className="w-full text-xs">
                    <thead>
                      <tr className="border-b border-gray-200">
                        <th className="text-left p-2">Time (days)</th>
                        {Array.from(visibleVariables).slice(0, 4).map((variable) => (
                          <th key={variable} className="text-left p-2">{variable}</th>
                        ))}
                      </tr>
                    </thead>
                    <tbody>
                      {mockResults[selectedEdge].timesteps.slice(0, 10).map((time, i) => (
                        <tr key={i} className="border-b border-gray-100">
                          <td className="p-2 font-mono">{time.toFixed(3)}</td>
                          {Array.from(visibleVariables).slice(0, 4).map((variable) => (
                            <td key={variable} className="p-2 font-mono">
                              {mockResults[selectedEdge].data[variable][i]?.toFixed(2) || '-'}
                            </td>
                          ))}
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              </div>
            </div>
          )}

          {Object.keys(mockResults).length > 0 && !selectedEdge && (
            <div className="p-3 bg-blue-50 border border-blue-200 rounded-lg">
              <p className="text-sm text-blue-800">
                💡 Select a connection above to view detailed flow data and visualizations.
              </p>
            </div>
          )}
        </>
      )}
    </div>
  );
}