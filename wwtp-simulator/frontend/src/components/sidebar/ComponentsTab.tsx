'use client';

import React from 'react';
import Image from 'next/image';
import { BSM2_COMPONENTS } from '@/lib/components';

export default function ComponentsTab() {
  const onDragStart = (event: React.DragEvent, componentType: string) => {
    event.dataTransfer.setData('application/reactflow', componentType);
    event.dataTransfer.effectAllowed = 'move';
  };

  return (
    <div className="p-4">
      <h3 className="text-lg font-semibold mb-4 text-gray-900">Available Components</h3>
      <p className="text-sm text-gray-600 mb-4">
        Drag and drop components onto the flowsheet to build your wastewater treatment plant.
      </p>
      
      <div className="space-y-3">
        {BSM2_COMPONENTS.map((component) => (
          <div
            key={component.id}
            draggable
            onDragStart={(e) => onDragStart(e, component.id)}
            className="p-3 bg-gray-50 rounded-lg border border-gray-200 cursor-grab active:cursor-grabbing hover:bg-gray-100 transition-colors"
          >
            <div className="flex items-start gap-3">
              <div className="w-10 h-10 flex items-center justify-center bg-white rounded border border-gray-300">
                {component.icon.endsWith('.svg') ? (
                  <Image
                    src={component.icon}
                    alt={component.name}
                    width={24}
                    height={24}
                    className="w-6 h-6"
                  />
                ) : (
                  <div className="w-6 h-6 bg-gray-400 rounded"></div>
                )}
              </div>
              
              <div className="flex-1 min-w-0">
                <h4 className="font-medium text-gray-900 truncate">{component.name}</h4>
                <p className="text-xs text-gray-600 mt-1 line-clamp-2">
                  {component.description}
                </p>
                
                <div className="mt-2 flex items-center gap-4 text-xs text-gray-500">
                  <span>📥 {component.inputs.length} input{component.inputs.length !== 1 ? 's' : ''}</span>
                  <span>📤 {component.outputs.length} output{component.outputs.length !== 1 ? 's' : ''}</span>
                  {component.parameters.length > 0 && (
                    <span>⚙️ {component.parameters.length} param{component.parameters.length !== 1 ? 's' : ''}</span>
                  )}
                </div>
              </div>
            </div>
          </div>
        ))}
      </div>
      
      <div className="mt-6 p-3 bg-blue-50 rounded-lg border border-blue-200">
        <p className="text-sm text-blue-800">
          💡 <strong>Tip:</strong> After adding components, connect them by dragging from output ports (green) 
          to input ports (blue). Each port can only have one connection.
        </p>
      </div>
    </div>
  );
}