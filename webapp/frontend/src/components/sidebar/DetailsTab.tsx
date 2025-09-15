'use client'

import React from 'react'
import { Node, Edge } from 'reactflow'
import { Trash2, Settings } from 'lucide-react'
import { NodeData } from '@/types'

interface DetailsTabProps {
  selectedNode: Node | null
  selectedEdge: Edge | null
  onNodeUpdate: (nodeId: string, newData: Partial<NodeData>) => void
  onNodeDelete: (nodeId: string) => void
  onEdgeDelete: (edgeId: string) => void
}

export default function DetailsTab({
  selectedNode,
  selectedEdge,
  onNodeUpdate,
  onNodeDelete,
  onEdgeDelete,
}: DetailsTabProps) {
  if (!selectedNode && !selectedEdge) {
    return (
      <div className="p-4">
        <div className="text-center text-gray-500 py-8">
          <Settings className="w-8 h-8 mx-auto mb-2 text-gray-400" />
          <p className="text-sm">Select a component or connection to view details</p>
        </div>
      </div>
    )
  }

  if (selectedEdge) {
    return (
      <div className="p-4 space-y-4">
        <div className="flex items-center justify-between">
          <h3 className="text-sm font-semibold text-gray-900">Connection Details</h3>
          <button
            onClick={() => onEdgeDelete(selectedEdge.id)}
            className="p-1 text-red-600 hover:bg-red-50 rounded"
            title="Delete connection"
          >
            <Trash2 className="w-4 h-4" />
          </button>
        </div>

        <div className="space-y-3">
          <div>
            <label className="block text-xs font-medium text-gray-700 mb-1">
              Connection ID
            </label>
            <div className="text-sm text-gray-900 font-mono">{selectedEdge.id}</div>
          </div>

          <div>
            <label className="block text-xs font-medium text-gray-700 mb-1">
              From
            </label>
            <div className="text-sm text-gray-900">
              {selectedEdge.source} → {selectedEdge.sourceHandle}
            </div>
          </div>

          <div>
            <label className="block text-xs font-medium text-gray-700 mb-1">
              To
            </label>
            <div className="text-sm text-gray-900">
              {selectedEdge.target} ← {selectedEdge.targetHandle}
            </div>
          </div>
        </div>
      </div>
    )
  }

  const nodeData = selectedNode?.data as NodeData

  const handleParameterChange = (paramKey: string, value: any) => {
    if (selectedNode) {
      onNodeUpdate(selectedNode.id, {
        parameters: {
          ...nodeData.parameters,
          [paramKey]: value,
        },
      })
    }
  }

  const handleNameChange = (newName: string) => {
    if (selectedNode) {
      onNodeUpdate(selectedNode.id, { name: newName })
    }
  }

  return (
    <div className="p-4 space-y-4">
      <div className="flex items-center justify-between">
        <h3 className="text-sm font-semibold text-gray-900">Component Details</h3>
        <button
          onClick={() => selectedNode && onNodeDelete(selectedNode.id)}
          className="p-1 text-red-600 hover:bg-red-50 rounded"
          title="Delete component"
        >
          <Trash2 className="w-4 h-4" />
        </button>
      </div>

      <div className="space-y-4">
        {/* Component Name */}
        <div>
          <label className="block text-xs font-medium text-gray-700 mb-1">
            Component Name
          </label>
          <input
            type="text"
            value={nodeData?.name || ''}
            onChange={(e) => handleNameChange(e.target.value)}
            className="w-full px-3 py-2 text-sm border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
          />
        </div>

        {/* Component Type */}
        <div>
          <label className="block text-xs font-medium text-gray-700 mb-1">
            Type
          </label>
          <div className="text-sm text-gray-900 font-mono">{nodeData?.type}</div>
        </div>

        {/* Parameters */}
        {nodeData?.parameters && Object.keys(nodeData.parameters).length > 0 && (
          <div>
            <label className="block text-xs font-medium text-gray-700 mb-2">
              Parameters
            </label>
            <div className="space-y-3">
              {Object.entries(nodeData.parameters).map(([key, value]) => (
                <div key={key}>
                  <label className="block text-xs text-gray-600 mb-1">
                    {key}
                  </label>
                  {typeof value === 'boolean' ? (
                    <label className="flex items-center">
                      <input
                        type="checkbox"
                        checked={value}
                        onChange={(e) => handleParameterChange(key, e.target.checked)}
                        className="mr-2"
                      />
                      <span className="text-sm text-gray-700">
                        {value ? 'Enabled' : 'Disabled'}
                      </span>
                    </label>
                  ) : typeof value === 'number' ? (
                    <input
                      type="number"
                      value={value}
                      onChange={(e) => handleParameterChange(key, parseFloat(e.target.value) || 0)}
                      className="w-full px-2 py-1 text-sm border border-gray-300 rounded focus:outline-none focus:ring-1 focus:ring-blue-500"
                    />
                  ) : (
                    <input
                      type="text"
                      value={String(value)}
                      onChange={(e) => handleParameterChange(key, e.target.value)}
                      className="w-full px-2 py-1 text-sm border border-gray-300 rounded focus:outline-none focus:ring-1 focus:ring-blue-500"
                    />
                  )}
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Inputs/Outputs */}
        <div className="grid grid-cols-2 gap-4">
          <div>
            <label className="block text-xs font-medium text-gray-700 mb-1">
              Inputs
            </label>
            <div className="space-y-1">
              {nodeData?.inputs.map((input) => (
                <div key={input} className="text-xs text-gray-600 font-mono">
                  {input}
                </div>
              ))}
            </div>
          </div>
          <div>
            <label className="block text-xs font-medium text-gray-700 mb-1">
              Outputs
            </label>
            <div className="space-y-1">
              {nodeData?.outputs.map((output) => (
                <div key={output} className="text-xs text-gray-600 font-mono">
                  {output}
                </div>
              ))}
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}