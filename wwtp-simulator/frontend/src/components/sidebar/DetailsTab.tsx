'use client';

import React, { useState, useCallback } from 'react';
import { FlowNode, FlowEdge } from '@/types';
import { BSM2_COMPONENTS } from '@/lib/components';
import { Edit3, Save, X, Upload, FileText, AlertCircle } from 'lucide-react';

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
  const [csvFile, setCsvFile] = useState<File | null>(null);
  const [csvError, setCsvError] = useState<string | null>(null);
  const [showCsvDialog, setShowCsvDialog] = useState(false);

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

    const handleCsvUpload = useCallback((file: File, resolution: number) => {
      const reader = new FileReader();
      reader.onload = (e) => {
        try {
          const csvText = e.target?.result as string;
          const lines = csvText.trim().split('\n');
          
          // Validate CSV format - should have 22 columns (time + 21 state variables)
          const firstDataLine = lines[0].split(',');
          if (firstDataLine.length !== 22) {
            setCsvError(`Invalid CSV format. Expected 22 columns, found ${firstDataLine.length}. CSV should contain: time, SI, SS, XI, XS, XBH, XBA, XP, SO, SNO, SNH, SND, XND, SALK, TSS, Q, TEMP, SD1, SD2, SD3, XD4, XD5`);
            return;
          }

          // Update the node parameters
          handleParamChange('csv_file', file.name);
          handleParamChange('timestep_resolution', resolution);
          handleParamChange('influent_type', 'dynamic');
          
          setCsvError(null);
          setCsvFile(file);
          setShowCsvDialog(false);
        } catch (error) {
          setCsvError('Error reading CSV file. Please check the file format.');
        }
      };
      reader.readAsText(file);
    }, []);

    const CsvUploadDialog = () => {
      const [dragOver, setDragOver] = useState(false);
      const [tempResolution, setTempResolution] = useState(15);

      const handleDrop = useCallback((e: React.DragEvent) => {
        e.preventDefault();
        setDragOver(false);
        
        const files = Array.from(e.dataTransfer.files);
        const csvFile = files.find(f => f.name.toLowerCase().endsWith('.csv'));
        
        if (csvFile) {
          handleCsvUpload(csvFile, tempResolution);
        } else {
          setCsvError('Please upload a CSV file.');
        }
      }, [tempResolution]);

      const handleFileSelect = (e: React.ChangeEvent<HTMLInputElement>) => {
        const file = e.target.files?.[0];
        if (file) {
          handleCsvUpload(file, tempResolution);
        }
      };

      return (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg p-6 max-w-md w-full mx-4">
            <div className="flex items-center justify-between mb-4">
              <h4 className="text-lg font-medium">Upload Influent CSV</h4>
              <button
                onClick={() => setShowCsvDialog(false)}
                className="text-gray-400 hover:text-gray-600"
              >
                <X size={20} />
              </button>
            </div>

            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Timestep Resolution (minutes)
                </label>
                <select
                  value={tempResolution}
                  onChange={(e) => setTempResolution(parseInt(e.target.value))}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                >
                  <option value={1}>1 minute</option>
                  <option value={5}>5 minutes</option>
                  <option value={15}>15 minutes (BSM2 default)</option>
                  <option value={30}>30 minutes</option>
                  <option value={60}>1 hour</option>
                </select>
              </div>

              <div
                onDrop={handleDrop}
                onDragOver={(e) => { e.preventDefault(); setDragOver(true); }}
                onDragLeave={() => setDragOver(false)}
                className={`border-2 border-dashed rounded-lg p-6 text-center transition-colors ${
                  dragOver 
                    ? 'border-blue-500 bg-blue-50' 
                    : 'border-gray-300 hover:border-gray-400'
                }`}
              >
                <Upload size={24} className="mx-auto mb-2 text-gray-400" />
                <p className="text-sm text-gray-600 mb-2">
                  Drag and drop your CSV file here, or
                </p>
                <input
                  type="file"
                  accept=".csv"
                  onChange={handleFileSelect}
                  className="hidden"
                  id="csv-upload"
                />
                <label
                  htmlFor="csv-upload"
                  className="cursor-pointer text-blue-600 hover:text-blue-800 text-sm font-medium"
                >
                  browse files
                </label>
              </div>

              <div className="text-xs text-gray-500">
                <p className="font-medium mb-1">CSV Format Requirements:</p>
                <ul className="list-disc list-inside space-y-1">
                  <li>22 columns: time, SI, SS, XI, XS, XBH, XBA, XP, SO, SNO, SNH, SND, XND, SALK, TSS, Q, TEMP, SD1, SD2, SD3, XD4, XD5</li>
                  <li>Time column should be in days</li>
                  <li>Each row represents one timestep</li>
                </ul>
              </div>

              {csvError && (
                <div className="flex items-start gap-2 p-3 bg-red-50 border border-red-200 rounded-md">
                  <AlertCircle size={16} className="text-red-600 mt-0.5 flex-shrink-0" />
                  <p className="text-sm text-red-700">{csvError}</p>
                </div>
              )}
            </div>
          </div>
        </div>
      );
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
                      
                      {/* Special handling for Influent component */}
                      {component.id === 'influent' && param.id === 'influent_type' ? (
                        <select
                          value={String(currentValue)}
                          onChange={(e) => handleParamChange(param.id, e.target.value)}
                          disabled={!isEditing}
                          className={`w-full px-3 py-2 border border-gray-300 rounded-md ${
                            isEditing 
                              ? 'focus:ring-2 focus:ring-blue-500 focus:border-blue-500' 
                              : 'bg-gray-50 text-gray-600'
                          }`}
                        >
                          <option value="constant">Constant</option>
                          <option value="dynamic">Dynamic</option>
                        </select>
                      ) : component.id === 'influent' && param.id === 'csv_file' ? (
                        <div className="space-y-2">
                          <div className="flex gap-2">
                            <input
                              type="text"
                              value={String(currentValue)}
                              disabled
                              placeholder={currentValue ? String(currentValue) : "No file selected"}
                              className="flex-1 px-3 py-2 border border-gray-300 rounded-md bg-gray-50 text-gray-600"
                            />
                            {isEditing && (
                              <button
                                onClick={() => setShowCsvDialog(true)}
                                className="px-3 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 flex items-center gap-1"
                              >
                                <FileText size={16} />
                                Browse
                              </button>
                            )}
                          </div>
                          {String(editingParams['influent_type'] ?? selectedNode.data.parameters['influent_type'] ?? 'constant') === 'constant' && (
                            <p className="text-xs text-amber-600">
                              💡 Set type to "Dynamic" to upload custom CSV file
                            </p>
                          )}
                        </div>
                      ) : param.type === 'number' ? (
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

        {/* CSV Upload Dialog */}
        {showCsvDialog && <CsvUploadDialog />}
      </div>
    );
  }

  return null;
}