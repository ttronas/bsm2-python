'use client'

import React, { useState } from 'react'
import { Play, StopCircle, Upload } from 'lucide-react'
import { validateCSVFile, parseCSVFile } from '@/lib/utils'

interface SimulationTabProps {
  onRunSimulation: () => void
  simulationRunning: boolean
  simulationProgress: number
}

export default function SimulationTab({
  onRunSimulation,
  simulationRunning,
  simulationProgress,
}: SimulationTabProps) {
  const [simulationSettings, setSimulationSettings] = useState({
    timestep: 1, // minutes
    endTime: 7, // days
    influentType: 'dynamic' as 'constant' | 'dynamic',
    influentFile: null as File | null,
  })

  const handleSettingChange = (key: string, value: any) => {
    setSimulationSettings(prev => ({
      ...prev,
      [key]: value,
    }))
  }

  const handleInfluentFileChange = async (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0]
    if (file) {
      const isValid = await validateCSVFile(file)
      if (isValid) {
        setSimulationSettings(prev => ({
          ...prev,
          influentFile: file,
        }))
      } else {
        alert('Invalid CSV file. Please check the format.')
        event.target.value = ''
      }
    }
  }

  return (
    <div className="p-4 space-y-6">
      <div>
        <h3 className="text-sm font-semibold text-gray-900 mb-4">Simulation Settings</h3>
        
        <div className="space-y-4">
          {/* Timestep */}
          <div>
            <label className="block text-xs font-medium text-gray-700 mb-1">
              Timestep (minutes)
            </label>
            <select
              value={simulationSettings.timestep}
              onChange={(e) => handleSettingChange('timestep', parseInt(e.target.value))}
              className="w-full px-3 py-2 text-sm border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
            >
              <option value={1}>1 minute</option>
              <option value={5}>5 minutes</option>
              <option value={10}>10 minutes</option>
              <option value={15}>15 minutes</option>
            </select>
          </div>

          {/* End Time */}
          <div>
            <label className="block text-xs font-medium text-gray-700 mb-1">
              Simulation Duration (days)
            </label>
            <input
              type="number"
              min="0.1"
              step="0.1"
              value={simulationSettings.endTime}
              onChange={(e) => handleSettingChange('endTime', parseFloat(e.target.value) || 1)}
              className="w-full px-3 py-2 text-sm border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
          </div>

          {/* Influent Type */}
          <div>
            <label className="block text-xs font-medium text-gray-700 mb-2">
              Influent Type
            </label>
            <div className="space-y-2">
              <label className="flex items-center">
                <input
                  type="radio"
                  name="influentType"
                  value="constant"
                  checked={simulationSettings.influentType === 'constant'}
                  onChange={(e) => handleSettingChange('influentType', e.target.value)}
                  className="mr-2"
                />
                <span className="text-sm text-gray-700">Constant (first line of default file)</span>
              </label>
              <label className="flex items-center">
                <input
                  type="radio"
                  name="influentType"
                  value="dynamic"
                  checked={simulationSettings.influentType === 'dynamic'}
                  onChange={(e) => handleSettingChange('influentType', e.target.value)}
                  className="mr-2"
                />
                <span className="text-sm text-gray-700">Dynamic (time series)</span>
              </label>
            </div>
          </div>

          {/* Dynamic Influent File Upload */}
          {simulationSettings.influentType === 'dynamic' && (
            <div>
              <label className="block text-xs font-medium text-gray-700 mb-1">
                Influent Data File (CSV)
              </label>
              <div className="flex items-center space-x-2">
                <label className="flex-1 flex items-center justify-center px-3 py-2 text-xs font-medium text-gray-700 bg-white border border-gray-300 rounded-md hover:bg-gray-50 transition-colors cursor-pointer">
                  <Upload className="w-4 h-4 mr-1" />
                  {simulationSettings.influentFile ? simulationSettings.influentFile.name : 'Choose file'}
                  <input
                    type="file"
                    accept=".csv"
                    onChange={handleInfluentFileChange}
                    className="hidden"
                  />
                </label>
              </div>
              <p className="text-xs text-gray-500 mt-1">
                Leave empty to use default BSM2 dynamic influent data
              </p>
            </div>
          )}
        </div>
      </div>

      {/* Run Simulation */}
      <div className="border-t border-gray-200 pt-4">
        <button
          onClick={onRunSimulation}
          disabled={false} // TODO: Add validation
          className={`w-full flex items-center justify-center px-4 py-3 text-sm font-medium rounded-md transition-colors ${
            simulationRunning
              ? 'bg-red-600 hover:bg-red-700 text-white'
              : 'bg-blue-600 hover:bg-blue-700 text-white disabled:bg-gray-300 disabled:text-gray-500'
          }`}
        >
          {simulationRunning ? (
            <>
              <StopCircle className="w-4 h-4 mr-2" />
              Stop Simulation
            </>
          ) : (
            <>
              <Play className="w-4 h-4 mr-2" />
              Run Simulation
            </>
          )}
        </button>

        {/* Progress Bar */}
        {simulationRunning && (
          <div className="mt-3">
            <div className="flex justify-between text-xs text-gray-600 mb-1">
              <span>Progress</span>
              <span>{Math.round(simulationProgress * 100)}%</span>
            </div>
            <div className="w-full bg-gray-200 rounded-full h-2">
              <div
                className="bg-blue-600 h-2 rounded-full transition-all duration-300"
                style={{ width: `${simulationProgress * 100}%` }}
              />
            </div>
          </div>
        )}
      </div>

      {/* Simulation Info */}
      <div className="text-xs text-gray-500 space-y-1">
        <p>• Simulation will run for {simulationSettings.endTime} days</p>
        <p>• Timestep: {simulationSettings.timestep} minute(s)</p>
        <p>• Total steps: {Math.ceil((simulationSettings.endTime * 24 * 60) / simulationSettings.timestep)}</p>
      </div>
    </div>
  )
}