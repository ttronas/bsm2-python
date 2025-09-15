'use client'

import React, { useState } from 'react'
import { BarChart3, Download, Eye } from 'lucide-react'
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts'

export default function ResultsTab() {
  const [selectedComponent, setSelectedComponent] = useState<string>('')
  const [selectedOutput, setSelectedOutput] = useState<string>('')
  const [viewMode, setViewMode] = useState<'table' | 'chart'>('chart')

  // Mock data for demonstration
  const mockResults = {
    'reactor-1': {
      name: 'ASM1 Reactor 1',
      outputs: {
        'effluent': [
          { time: 0, value: 10.5 },
          { time: 1, value: 11.2 },
          { time: 2, value: 10.8 },
          { time: 3, value: 11.5 },
          { time: 4, value: 10.9 },
          { time: 5, value: 11.1 },
          { time: 6, value: 10.7 },
        ]
      }
    },
    'clarifier-1': {
      name: 'Primary Clarifier',
      outputs: {
        'effluent': [
          { time: 0, value: 8.5 },
          { time: 1, value: 9.1 },
          { time: 2, value: 8.8 },
          { time: 3, value: 9.2 },
          { time: 4, value: 8.9 },
          { time: 5, value: 9.0 },
          { time: 6, value: 8.7 },
        ],
        'sludge': [
          { time: 0, value: 2.1 },
          { time: 1, value: 2.3 },
          { time: 2, value: 2.0 },
          { time: 3, value: 2.4 },
          { time: 4, value: 2.2 },
          { time: 5, value: 2.1 },
          { time: 6, value: 2.3 },
        ]
      }
    }
  }

  const components = Object.keys(mockResults)
  const selectedComponentData = selectedComponent ? mockResults[selectedComponent as keyof typeof mockResults] : null
  const outputs = selectedComponentData ? Object.keys(selectedComponentData.outputs) : []
  const chartData = selectedComponentData && selectedOutput ? 
    selectedComponentData.outputs[selectedOutput as keyof typeof selectedComponentData.outputs] : []

  return (
    <div className="p-4 space-y-4">
      <div>
        <h3 className="text-sm font-semibold text-gray-900 mb-4">Simulation Results</h3>
        
        {components.length === 0 ? (
          <div className="text-center text-gray-500 py-8">
            <BarChart3 className="w-8 h-8 mx-auto mb-2 text-gray-400" />
            <p className="text-sm">No simulation results available</p>
            <p className="text-xs text-gray-400 mt-1">Run a simulation to see results here</p>
          </div>
        ) : (
          <div className="space-y-4">
            {/* Component Selection */}
            <div>
              <label className="block text-xs font-medium text-gray-700 mb-1">
                Select Component
              </label>
              <select
                value={selectedComponent}
                onChange={(e) => {
                  setSelectedComponent(e.target.value)
                  setSelectedOutput('')
                }}
                className="w-full px-3 py-2 text-sm border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
              >
                <option value="">Choose a component...</option>
                {components.map(compId => (
                  <option key={compId} value={compId}>
                    {mockResults[compId as keyof typeof mockResults].name}
                  </option>
                ))}
              </select>
            </div>

            {/* Output Selection */}
            {selectedComponent && (
              <div>
                <label className="block text-xs font-medium text-gray-700 mb-1">
                  Select Output
                </label>
                <select
                  value={selectedOutput}
                  onChange={(e) => setSelectedOutput(e.target.value)}
                  className="w-full px-3 py-2 text-sm border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                >
                  <option value="">Choose an output...</option>
                  {outputs.map(output => (
                    <option key={output} value={output}>
                      {output}
                    </option>
                  ))}
                </select>
              </div>
            )}

            {/* View Mode Toggle */}
            {selectedComponent && selectedOutput && (
              <div className="flex space-x-2">
                <button
                  onClick={() => setViewMode('chart')}
                  className={`flex-1 px-3 py-2 text-xs font-medium rounded-md transition-colors ${
                    viewMode === 'chart'
                      ? 'bg-blue-100 text-blue-700 border border-blue-300'
                      : 'bg-gray-100 text-gray-700 border border-gray-300'
                  }`}
                >
                  <BarChart3 className="w-4 h-4 mx-auto" />
                </button>
                <button
                  onClick={() => setViewMode('table')}
                  className={`flex-1 px-3 py-2 text-xs font-medium rounded-md transition-colors ${
                    viewMode === 'table'
                      ? 'bg-blue-100 text-blue-700 border border-blue-300'
                      : 'bg-gray-100 text-gray-700 border border-gray-300'
                  }`}
                >
                  <Eye className="w-4 h-4 mx-auto" />
                </button>
              </div>
            )}

            {/* Results Display */}
            {selectedComponent && selectedOutput && (
              <div className="border border-gray-200 rounded-lg p-3">
                <div className="flex justify-between items-center mb-3">
                  <h4 className="text-sm font-medium text-gray-900">
                    {selectedComponentData?.name} - {selectedOutput}
                  </h4>
                  <button
                    onClick={() => {
                      // TODO: Implement export functionality
                      console.log('Exporting data...')
                    }}
                    className="p-1 text-gray-500 hover:text-gray-700"
                    title="Export data"
                  >
                    <Download className="w-4 h-4" />
                  </button>
                </div>

                {viewMode === 'chart' ? (
                  <div className="h-48">
                    <ResponsiveContainer width="100%" height="100%">
                      <LineChart data={chartData}>
                        <CartesianGrid strokeDasharray="3 3" />
                        <XAxis 
                          dataKey="time" 
                          fontSize={10}
                          label={{ value: 'Time (days)', position: 'insideBottom', offset: -5, fontSize: 10 }}
                        />
                        <YAxis 
                          fontSize={10}
                          label={{ value: 'Value', angle: -90, position: 'insideLeft', fontSize: 10 }}
                        />
                        <Tooltip />
                        <Line 
                          type="monotone" 
                          dataKey="value" 
                          stroke="#2563eb" 
                          strokeWidth={2}
                          dot={{ r: 3 }}
                        />
                      </LineChart>
                    </ResponsiveContainer>
                  </div>
                ) : (
                  <div className="max-h-48 overflow-y-auto">
                    <table className="w-full text-xs">
                      <thead className="bg-gray-50">
                        <tr>
                          <th className="px-2 py-1 text-left font-medium text-gray-700">Time</th>
                          <th className="px-2 py-1 text-left font-medium text-gray-700">Value</th>
                        </tr>
                      </thead>
                      <tbody className="divide-y divide-gray-200">
                        {chartData.map((row, index) => (
                          <tr key={index}>
                            <td className="px-2 py-1 text-gray-900">{row.time}</td>
                            <td className="px-2 py-1 text-gray-900">{row.value.toFixed(3)}</td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  </div>
                )}
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  )
}