'use client';

import React, { memo, useState } from 'react';
import { Handle, Position, NodeProps } from '@xyflow/react';
import Image from 'next/image';
import { BSM2_COMPONENTS } from '@/lib/components';
import { Edit3, Check, X } from 'lucide-react';

interface BSM2NodeData {
  label: string;
  componentType: string;
  parameters: Record<string, string | number | boolean>;
  isSelected: boolean;
}

function BSM2Node({ data, selected }: NodeProps & { data: BSM2NodeData }) {
  const [isEditing, setIsEditing] = useState(false);
  const [editLabel, setEditLabel] = useState(data.label);

  const component = BSM2_COMPONENTS.find(c => c.id === data.componentType);

  if (!component) {
    return (
      <div className="px-4 py-2 bg-red-100 border-2 border-red-300 rounded-lg">
        <div className="text-red-700">Unknown Component</div>
      </div>
    );
  }

  const handleLabelEdit = () => {
    if (isEditing) {
      // Save the label
      setIsEditing(false);
      // Update node data would be handled by parent component
    } else {
      setIsEditing(true);
    }
  };

  const handleLabelCancel = () => {
    setEditLabel(data.label);
    setIsEditing(false);
  };

  const handleLabelKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter') {
      handleLabelEdit();
    } else if (e.key === 'Escape') {
      handleLabelCancel();
    }
  };

  return (
    <div
      className={`bg-white border-2 rounded-lg min-w-[160px] shadow-lg transition-all ${
        selected ? 'border-blue-500 shadow-xl' : 'border-gray-300'
      }`}
    >
      {/* Input Handles */}
      {component.inputs.map((input, index) => (
        <Handle
          key={input.id}
          type="target"
          position={Position.Left}
          id={input.id}
          style={{
            top: component.inputs.length === 1 ? '50%' : `${((index + 1) * 100) / (component.inputs.length + 1)}%`,
            background: '#3b82f6',
          }}
          className="w-3 h-3"
        />
      ))}

      {/* Output Handles */}
      {component.outputs.map((output) => (
        <Handle
          key={output.id}
          type="source"
          position={output.position === 'right' ? Position.Right : 
                   output.position === 'top' ? Position.Top : Position.Bottom}
          id={output.id}
          style={{
            ...(output.position === 'right' ? {
              top: component.outputs.filter(o => o.position === 'right').length === 1 ? '50%' : 
                   `${((component.outputs.filter(o => o.position === 'right').findIndex(o => o.id === output.id) + 1) * 100) / 
                     (component.outputs.filter(o => o.position === 'right').length + 1)}%`
            } : output.position === 'top' ? {
              left: '50%',
              top: 0,
            } : {
              left: '50%',
              bottom: 0,
            }),
            background: '#10b981',
          }}
          className="w-3 h-3"
        />
      ))}

      <div className="p-3">
        {/* Node Header with Icon and Label */}
        <div className="flex items-center gap-2 mb-2">
          <div className="w-8 h-8 flex items-center justify-center bg-gray-100 rounded">
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
          
          <div className="flex-1 flex items-center gap-1">
            {isEditing ? (
              <div className="flex items-center gap-1 flex-1">
                <input
                  value={editLabel}
                  onChange={(e) => setEditLabel(e.target.value)}
                  onKeyDown={handleLabelKeyDown}
                  className="flex-1 px-1 py-0.5 text-sm border border-gray-300 rounded focus:outline-none focus:border-blue-500"
                  autoFocus
                />
                <button
                  onClick={handleLabelEdit}
                  className="p-0.5 text-green-600 hover:bg-green-100 rounded"
                >
                  <Check size={12} />
                </button>
                <button
                  onClick={handleLabelCancel}
                  className="p-0.5 text-red-600 hover:bg-red-100 rounded"
                >
                  <X size={12} />
                </button>
              </div>
            ) : (
              <div className="flex items-center gap-1 flex-1">
                <span className="text-sm font-medium truncate">{data.label}</span>
                <button
                  onClick={handleLabelEdit}
                  className="p-0.5 text-gray-400 hover:text-gray-600 hover:bg-gray-100 rounded"
                >
                  <Edit3 size={12} />
                </button>
              </div>
            )}
          </div>
        </div>

        {/* Input/Output Labels */}
        <div className="space-y-1">
          {component.inputs.map((input) => (
            <div key={input.id} className="text-xs text-blue-600 text-left">
              ● {input.name}
            </div>
          ))}
          {component.outputs.map((output) => (
            <div key={output.id} className="text-xs text-green-600 text-right">
              {output.name} ●
            </div>
          ))}
        </div>

        {/* Parameter Summary */}
        {component.parameters.length > 0 && (
          <div className="mt-2 pt-2 border-t border-gray-200">
            <div className="text-xs text-gray-500">
              {component.parameters.length} parameter{component.parameters.length !== 1 ? 's' : ''}
            </div>
          </div>
        )}
      </div>
    </div>
  );
}

export default memo(BSM2Node);