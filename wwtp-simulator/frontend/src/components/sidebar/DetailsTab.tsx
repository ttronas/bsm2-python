'use client';

import React, { useState } from 'react';
import { FlowNode, FlowEdge } from '@/types';
import { BSM2_COMPONENTS } from '@/lib/components';
import { Edit3, Save, X } from 'lucide-react';

interface DetailsTabProps {
  selectedNode: FlowNode | null;
  selectedEdge: FlowEdge | null;
  onNodeUpdate: (nodeId: string, data: Partial<FlowNode['data']>) => void;
}

export default function DetailsTab({
  selectedNode,
  selectedEdge,
  onNodeUpdate,
}: DetailsTabProps) {
  const [editingParams, setEditingParams] = useState<Record<string, string | number | boolean>>({});
  const [isEditing, setIsEditing] = useState(false);

  if (!selectedNode && !selectedEdge) {
    return (
      <div className="p-4">
        <h3 className="text-lg font-semibold mb-4 text-gray-900">Component Details</h3>
        <div className="text-center py-8">
          <div className="text-gray-400 mb-2">
            <div className="w-16 h-16 mx-auto mb-4 bg-gray-100 rounded-full flex items-center justify-center">
              ⚙️
            </div>
          </div>
          <p className="text-gray-600">
            Select a component or connection to view and edit its properties.
          </p>
        </div>
      </div>
    );
  }

  if (selectedEdge) {
    return (
      <div className="p-4">
        <h3 className="text-lg font-semibold mb-4 text-gray-900">Connection Details</h3>
        <div className="space-y-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Connection ID
            </label>
            <input
              type="text"
              value={selectedEdge.id}
              disabled
              className="w-full px-3 py-2 border border-gray-300 rounded-md bg-gray-50 text-gray-600"
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              From
            </label>
            <input
              type="text"
              value={`${selectedEdge.source} (${selectedEdge.sourceHandle})`}
              disabled
              className="w-full px-3 py-2 border border-gray-300 rounded-md bg-gray-50 text-gray-600"
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              To
            </label>
            <input
              type="text"
              value={`${selectedEdge.target} (${selectedEdge.targetHandle})`}
              disabled
              className="w-full px-3 py-2 border border-gray-300 rounded-md bg-gray-50 text-gray-600"
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Label
            </label>
            <input
              type="text"
              value={selectedEdge.data?.label || ''}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
              placeholder="Connection label..."
            />
          </div>
        </div>
      </div>
    );
  }

  if (selectedNode) {
    const component = BSM2_COMPONENTS.find(c => c.id === selectedNode.data.componentType);

    if (!component) {
      return (
        <div className="p-4">
          <h3 className="text-lg font-semibold mb-4 text-gray-900">Component Details</h3>
          <div className="text-red-600">Unknown component type: {selectedNode.data.componentType}</div>
        </div>
      );
    }

    const handleStartEdit = () => {
      setEditingParams({ ...selectedNode.data.parameters });
      setIsEditing(true);
    };

    const handleSaveEdit = () => {
      onNodeUpdate(selectedNode.id, { parameters: editingParams });
      setIsEditing(false);
    };

    const handleCancelEdit = () => {
      setEditingParams({});
      setIsEditing(false);
    };

    const handleParamChange = (paramId: string, value: string | number | boolean) => {
      setEditingParams(prev => ({ ...prev, [paramId]: value }));
    };

    return (
      <div className="p-4">
        <div className="flex items-center justify-between mb-4">
          <h3 className="text-lg font-semibold text-gray-900">Component Details</h3>
          {!isEditing ? (
            <button
              onClick={handleStartEdit}
              className="p-2 text-gray-600 hover:text-gray-900 hover:bg-gray-100 rounded"
            >
              <Edit3 size={16} />
            </button>
          ) : (
            <div className="flex gap-1">
              <button
                onClick={handleSaveEdit}
                className="p-2 text-green-600 hover:bg-green-100 rounded"
              >
                <Save size={16} />
              </button>
              <button
                onClick={handleCancelEdit}
                className="p-2 text-red-600 hover:bg-red-100 rounded"
              >
                <X size={16} />
              </button>
            </div>
          )}
        </div>

        <div className="space-y-4">
          <div className="flex items-center gap-3 p-3 bg-gray-50 rounded-lg">
            <div className="w-10 h-10 flex items-center justify-center bg-white rounded border">
              <span className="text-lg">{component.name[0]}</span>
            </div>
            <div>
              <h4 className="font-medium text-gray-900">{component.name}</h4>
              <p className="text-sm text-gray-600">{component.description}</p>
            </div>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Component Name
            </label>
            <input
              type="text"
              value={selectedNode.data.label}
              disabled={!isEditing}
              className={`w-full px-3 py-2 border border-gray-300 rounded-md ${
                isEditing 
                  ? 'focus:ring-2 focus:ring-blue-500 focus:border-blue-500' 
                  : 'bg-gray-50 text-gray-600'
              }`}
            />
          </div>

          {component.parameters.length > 0 && (
            <div>
              <h5 className="text-sm font-medium text-gray-700 mb-3">Parameters</h5>
              <div className="space-y-3">
                {component.parameters.map((param) => {
                  const currentValue = isEditing 
                    ? (editingParams[param.id] ?? param.defaultValue)
                    : (selectedNode.data.parameters[param.id] ?? param.defaultValue);

                  return (
                    <div key={param.id}>
                      <label className="block text-sm text-gray-600 mb-1">
                        {param.name}
                        {param.unit && <span className="text-gray-500"> ({param.unit})</span>}
                      </label>
                      
                      {param.type === 'number' ? (
                        <input
                          type="number"
                          value={typeof currentValue === 'number' ? currentValue : 0}
                          onChange={(e) => handleParamChange(param.id, parseFloat(e.target.value) || 0)}
                          disabled={!isEditing}
                          min={param.min}
                          max={param.max}
                          step="any"
                          className={`w-full px-3 py-2 border border-gray-300 rounded-md ${
                            isEditing 
                              ? 'focus:ring-2 focus:ring-blue-500 focus:border-blue-500' 
                              : 'bg-gray-50 text-gray-600'
                          }`}
                        />
                      ) : param.type === 'boolean' ? (
                        <label className="flex items-center">
                          <input
                            type="checkbox"
                            checked={Boolean(currentValue)}
                            onChange={(e) => handleParamChange(param.id, e.target.checked)}
                            disabled={!isEditing}
                            className="mr-2"
                          />
                          <span className="text-sm text-gray-700">
                            {currentValue ? 'Enabled' : 'Disabled'}
                          </span>
                        </label>
                      ) : (
                        <input
                          type="text"
                          value={String(currentValue)}
                          onChange={(e) => handleParamChange(param.id, e.target.value)}
                          disabled={!isEditing}
                          className={`w-full px-3 py-2 border border-gray-300 rounded-md ${
                            isEditing 
                              ? 'focus:ring-2 focus:ring-blue-500 focus:border-blue-500' 
                              : 'bg-gray-50 text-gray-600'
                          }`}
                        />
                      )}
                      
                      {param.description && (
                        <p className="text-xs text-gray-500 mt-1">{param.description}</p>
                      )}
                    </div>
                  );
                })}
              </div>
            </div>
          )}

          <div>
            <h5 className="text-sm font-medium text-gray-700 mb-3">Connections</h5>
            <div className="space-y-2">
              <div>
                <span className="text-sm text-gray-600">Inputs:</span>
                <div className="ml-4">
                  {component.inputs.map((input) => (
                    <div key={input.id} className="text-sm text-blue-600">
                      • {input.name}
                    </div>
                  ))}
                </div>
              </div>
              <div>
                <span className="text-sm text-gray-600">Outputs:</span>
                <div className="ml-4">
                  {component.outputs.map((output) => (
                    <div key={output.id} className="text-sm text-green-600">
                      • {output.name}
                    </div>
                  ))}
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    );
  }

  return null;
}