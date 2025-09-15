'use client'

import React from 'react'
import { Play, StopCircle } from 'lucide-react'

interface SimulationControlsProps {
  onRunSimulation: () => void
  simulationRunning: boolean
  progress: number
}

export default function SimulationControls({
  onRunSimulation,
  simulationRunning,
  progress,
}: SimulationControlsProps) {
  return (
    <div className="flex items-center space-x-4">
      {/* Progress Bar (when simulation is running) */}
      {simulationRunning && (
        <div className="w-48">
          <div className="flex justify-between text-xs text-gray-600 mb-1">
            <span>Running simulation...</span>
            <span>{Math.round(progress * 100)}%</span>
          </div>
          <div className="w-full bg-gray-200 rounded-full h-2">
            <div
              className="bg-green-600 h-2 rounded-full transition-all duration-300"
              style={{ width: `${progress * 100}%` }}
            />
          </div>
        </div>
      )}

      {/* Run/Stop Button */}
      <button
        onClick={onRunSimulation}
        className={`flex items-center px-4 py-2 text-sm font-medium rounded-md transition-colors ${
          simulationRunning
            ? 'bg-red-600 hover:bg-red-700 text-white'
            : 'bg-green-600 hover:bg-green-700 text-white'
        }`}
      >
        {simulationRunning ? (
          <>
            <StopCircle className="w-4 h-4 mr-2" />
            Stop
          </>
        ) : (
          <>
            <Play className="w-4 h-4 mr-2" />
            Run Simulation
          </>
        )}
      </button>
    </div>
  )
}