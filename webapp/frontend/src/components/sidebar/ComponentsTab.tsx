'use client'

import React from 'react'
import { Download, Upload } from 'lucide-react'
import { ComponentDefinition } from '@/types'

interface ComponentsTabProps {
  components: ComponentDefinition[]
  onExport: () => void
  onImport: (event: React.ChangeEvent<HTMLInputElement>) => void
}

export default function ComponentsTab({ components, onExport, onImport }: ComponentsTabProps) {
  const onDragStart = (event: React.DragEvent, componentType: string) => {
    event.dataTransfer.setData('application/reactflow', componentType)
    event.dataTransfer.effectAllowed = 'move'
  }

  return (
    <div className="p-4 space-y-4">
      <div className="space-y-2">
        <h3 className="text-sm font-semibold text-gray-900">Available Components</h3>
        <p className="text-xs text-gray-600">
          Drag and drop components to the flowsheet
        </p>
      </div>

      {/* Component List */}
      <div className="space-y-2">
        {components.map((component) => (
          <div
            key={component.id}
            draggable
            onDragStart={(event) => onDragStart(event, component.type)}
            className="p-3 border border-gray-200 rounded-lg cursor-move hover:bg-gray-50 transition-colors"
          >
            <div className="flex items-center space-x-3">
              <div className="w-8 h-8 flex items-center justify-center">
                {component.icon ? (
                  <img
                    src={`/api/icons/${component.icon}`}
                    alt={component.name}
                    className="w-full h-full object-contain"
                    onError={(e) => {
                      e.currentTarget.src = 'data:image/svg+xml,<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect x="3" y="3" width="18" height="18" rx="2" ry="2"/></svg>'
                    }}
                  />
                ) : (
                  <div className="w-6 h-6 bg-gray-300 rounded" />
                )}
              </div>
              <div className="flex-1">
                <div className="text-sm font-medium text-gray-900">{component.name}</div>
                <div className="text-xs text-gray-500">
                  {component.inputs.length} inputs, {component.outputs.length} outputs
                </div>
              </div>
            </div>
          </div>
        ))}
      </div>

      {/* Export/Import Controls */}
      <div className="border-t border-gray-200 pt-4 space-y-2">
        <h4 className="text-sm font-medium text-gray-900">Flowsheet</h4>
        
        <div className="flex space-x-2">
          <button
            onClick={onExport}
            className="flex-1 flex items-center justify-center px-3 py-2 text-xs font-medium text-gray-700 bg-white border border-gray-300 rounded-md hover:bg-gray-50 transition-colors"
          >
            <Download className="w-4 h-4 mr-1" />
            Export
          </button>
          
          <label className="flex-1 flex items-center justify-center px-3 py-2 text-xs font-medium text-gray-700 bg-white border border-gray-300 rounded-md hover:bg-gray-50 transition-colors cursor-pointer">
            <Upload className="w-4 h-4 mr-1" />
            Import
            <input
              type="file"
              accept=".json"
              onChange={onImport}
              className="hidden"
            />
          </label>
        </div>
      </div>
    </div>
  )
}