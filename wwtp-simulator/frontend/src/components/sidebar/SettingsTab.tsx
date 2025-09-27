'use client';

import React, { useState } from 'react';
import { FlowNode, FlowEdge, SimulationConfig } from '@/types';
import { Play, Save, Upload, Download, Loader2 } from 'lucide-react';

interface SettingsTabProps {
  nodes: FlowNode[];
  edges: FlowEdge[];
}

export default function SettingsTab({ nodes, edges }: SettingsTabProps) {
  const [settings, setSettings] = useState({
    timestep: 15, // minutes
    endTime: 14, // days
    startTime: 0,
  });
  const [configName, setConfigName] = useState('');
  const [configDescription, setConfigDescription] = useState('');
  const [isRunning, setIsRunning] = useState(false);
  const [progress, setProgress] = useState(0);

  const handleRunSimulation = async () => {
    if (nodes.length === 0) {
      alert('Please add components to the flowsheet before running simulation.');
      return;
    }

    if (edges.length === 0) {
      alert('Please connect components before running simulation.');
      return;
    }

    const config: SimulationConfig = {
      name: configName || 'Untitled Simulation',
      description: configDescription,
      nodes,
      edges,
      settings,
    };

    setIsRunning(true);
    setProgress(0);

    try {
      const response = await fetch('/api/simulation/run', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(config),
      });

      if (response.ok) {
        const result = await response.json();
        console.log('Simulation started:', result);
        // Here you would typically start polling for progress or use WebSocket
      } else {
        throw new Error('Failed to start simulation');
      }
    } catch (error) {
      console.error('Simulation error:', error);
      alert('Failed to start simulation. Please check your configuration.');
    } finally {
      setIsRunning(false);
    }
  };

  const handleSaveConfig = async () => {
    const config: SimulationConfig = {
      name: configName || 'Untitled Configuration',
      description: configDescription,
      nodes,
      edges,
      settings,
      createdAt: new Date().toISOString(),
    };

    try {
      const response = await fetch('/api/config/save', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(config),
      });

      if (response.ok) {
        alert('Configuration saved successfully!');
      } else {
        throw new Error('Failed to save configuration');
      }
    } catch (error) {
      console.error('Save error:', error);
      alert('Failed to save configuration.');
    }
  };

  const handleLoadConfig = () => {
    const input = document.createElement('input');
    input.type = 'file';
    input.accept = '.json';
    input.onchange = (e) => {
      const file = (e.target as HTMLInputElement).files?.[0];
      if (file) {
        const reader = new FileReader();
        reader.onload = (e) => {
          try {
            const config = JSON.parse(e.target?.result as string);
            setConfigName(config.name || '');
            setConfigDescription(config.description || '');
            setSettings(config.settings || settings);
            // Note: nodes and edges would need to be updated via parent component
          } catch (error) {
            alert('Invalid configuration file.');
          }
        };
        reader.readAsText(file);
      }
    };
    input.click();
  };

  const handleExportConfig = () => {
    const config: SimulationConfig = {
      name: configName || 'Untitled Configuration',
      description: configDescription,
      nodes,
      edges,
      settings,
      createdAt: new Date().toISOString(),
    };

    const blob = new Blob([JSON.stringify(config, null, 2)], {
      type: 'application/json',
    });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `${config.name.replace(/[^a-z0-9]/gi, '_').toLowerCase()}.json`;
    a.click();
    URL.revokeObjectURL(url);
  };

  return (
    <div className="p-4 space-y-6">
      <h3 className="text-lg font-semibold text-gray-900">Simulation Settings</h3>

      {/* Configuration Details */}
      <div className="space-y-4">
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">
            Configuration Name
          </label>
          <input
            type="text"
            value={configName}
            onChange={(e) => setConfigName(e.target.value)}
            className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
            placeholder="Enter configuration name..."
          />
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">
            Description
          </label>
          <textarea
            value={configDescription}
            onChange={(e) => setConfigDescription(e.target.value)}
            rows={3}
            className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
            placeholder="Describe your simulation setup..."
          />
        </div>
      </div>

      {/* Simulation Parameters */}
      <div className="space-y-4">
        <h4 className="text-md font-medium text-gray-800">Simulation Parameters</h4>
        
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">
            Timestep (minutes)
          </label>
          <select
            value={settings.timestep}
            onChange={(e) => setSettings(prev => ({ ...prev, timestep: parseInt(e.target.value) }))}
            className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
          >
            <option value={1}>1 minute</option>
            <option value={5}>5 minutes</option>
            <option value={15}>15 minutes</option>
            <option value={30}>30 minutes</option>
            <option value={60}>1 hour</option>
          </select>
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">
            Simulation Duration (days)
          </label>
          <input
            type="number"
            value={settings.endTime}
            onChange={(e) => setSettings(prev => ({ ...prev, endTime: parseFloat(e.target.value) || 1 }))}
            min={0.1}
            max={365}
            step={0.1}
            className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
          />
        </div>

        <div className="p-3 bg-amber-50 border border-amber-200 rounded-md">
          <p className="text-sm text-amber-800">
            ⚠️ <strong>Note:</strong> Long simulations ({'>'}30 days) with small timesteps ({'≤'}5 min) 
            may take significant time to complete.
          </p>
        </div>
      </div>

      {/* Current Configuration Status */}
      <div className="p-3 bg-gray-50 rounded-lg">
        <h5 className="text-sm font-medium text-gray-700 mb-2">Current Configuration</h5>
        <div className="text-sm text-gray-600 space-y-1">
          <div>Components: {nodes.length}</div>
          <div>Connections: {edges.length}</div>
          <div>Estimated runtime: ~{Math.ceil((settings.endTime * 1440) / settings.timestep)} timesteps</div>
        </div>
      </div>

      {/* Action Buttons */}
      <div className="space-y-3">
        <button
          onClick={handleRunSimulation}
          disabled={isRunning || nodes.length === 0}
          className={`w-full py-2 px-4 rounded-md font-medium flex items-center justify-center gap-2 transition-colors ${
            isRunning
              ? 'bg-gray-400 text-white cursor-not-allowed'
              : nodes.length === 0
              ? 'bg-gray-300 text-gray-500 cursor-not-allowed'
              : 'bg-green-600 text-white hover:bg-green-700'
          }`}
        >
          {isRunning ? (
            <>
              <Loader2 className="animate-spin" size={16} />
              Running... {progress}%
            </>
          ) : (
            <>
              <Play size={16} />
              Run Simulation
            </>
          )}
        </button>

        {isRunning && (
          <div className="w-full bg-gray-200 rounded-full h-2">
            <div
              className="bg-green-600 h-2 rounded-full transition-all duration-300"
              style={{ width: `${progress}%` }}
            ></div>
          </div>
        )}

        <div className="flex gap-2">
          <button
            onClick={handleSaveConfig}
            className="flex-1 py-2 px-4 bg-blue-600 text-white rounded-md font-medium hover:bg-blue-700 flex items-center justify-center gap-2"
          >
            <Save size={16} />
            Save Config
          </button>
          <button
            onClick={handleLoadConfig}
            className="flex-1 py-2 px-4 bg-gray-600 text-white rounded-md font-medium hover:bg-gray-700 flex items-center justify-center gap-2"
          >
            <Upload size={16} />
            Load Config
          </button>
        </div>

        <button
          onClick={handleExportConfig}
          className="w-full py-2 px-4 bg-indigo-600 text-white rounded-md font-medium hover:bg-indigo-700 flex items-center justify-center gap-2"
        >
          <Download size={16} />
          Export Configuration
        </button>

        <div className="border-t border-gray-200 pt-3">
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Import Predefined Flowsheets
          </label>
          <select
            className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-blue-500 mb-2"
            defaultValue=""
          >
            <option value="" disabled>Select a predefined flowsheet...</option>
            <option value="bsm2-ol">BSM2 Open Loop</option>
            <option value="bsm2-cl">BSM2 Closed Loop</option>
            <option value="bsm1-ol">BSM1 Open Loop</option>
            <option value="bsm1-cl">BSM1 Closed Loop</option>
            <option value="single-asm1">Single ASM1 Reactor</option>
            <option value="single-adm1">Single ADM1 Reactor</option>
          </select>
          <button
            className="w-full py-2 px-4 bg-purple-600 text-white rounded-md font-medium hover:bg-purple-700 flex items-center justify-center gap-2"
            onClick={() => alert('Import predefined flowsheets functionality will be implemented')}
          >
            <Upload size={16} />
            Import Predefined
          </button>
        </div>
      </div>
    </div>
  );
}