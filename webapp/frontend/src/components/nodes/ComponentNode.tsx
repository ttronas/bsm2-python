'use client'

import React from 'react'
import { Handle, Position } from 'reactflow'
import { NodeData } from '@/types'
import { cn } from '@/lib/utils'

interface ComponentNodeProps {
  data: NodeData
  selected: boolean
}

export default function ComponentNode({ data, selected }: ComponentNodeProps) {
  const { name, icon, inputs, outputs } = data

  return (
    <div
      className={cn(
        "relative bg-white border-2 border-gray-200 rounded-lg shadow-lg min-w-[120px] min-h-[80px] p-3",
        selected && "border-blue-500 ring-2 ring-blue-200"
      )}
    >
      {/* Input handles */}
      {inputs.map((input, index) => (
        <Handle
          key={`input-${input}`}
          type="target"
          position={Position.Left}
          id={input}
          className="w-3 h-3 bg-gray-300 border-2 border-gray-400"
          style={{
            top: `${((index + 1) * 100) / (inputs.length + 1)}%`,
          }}
          title={input}
        />
      ))}

      {/* Output handles */}
      {outputs.map((output, index) => (
        <Handle
          key={`output-${output}`}
          type="source"
          position={Position.Right}
          id={output}
          className="w-3 h-3 bg-blue-300 border-2 border-blue-400"
          style={{
            top: `${((index + 1) * 100) / (outputs.length + 1)}%`,
          }}
          title={output}
        />
      ))}

      {/* Node content */}
      <div className="flex flex-col items-center space-y-2">
        {/* Icon */}
        <div className="w-8 h-8 flex items-center justify-center">
          {icon ? (
            <img
              src={`/api/icons/${icon}`}
              alt={name}
              className="w-full h-full object-contain"
              onError={(e) => {
                // Fallback to a generic icon if the specific icon fails to load
                e.currentTarget.src = 'data:image/svg+xml,<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect x="3" y="3" width="18" height="18" rx="2" ry="2"/><line x1="9" y1="9" x2="15" y2="15"/><line x1="15" y1="9" x2="9" y2="15"/></svg>'
              }}
            />
          ) : (
            <div className="w-6 h-6 bg-gray-400 rounded" />
          )}
        </div>

        {/* Name */}
        <div className="text-xs font-medium text-center text-gray-800 leading-tight">
          {name}
        </div>
      </div>

      {/* Handle labels on hover */}
      <style jsx>{`
        .react-flow__handle {
          opacity: 0.7;
          transition: opacity 0.2s;
        }
        
        .react-flow__handle:hover {
          opacity: 1;
        }
      `}</style>
    </div>
  )
}