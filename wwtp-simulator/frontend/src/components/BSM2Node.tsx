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

  // Calculate input positions for proper alignment
  const getInputPosition = (index: number, total: number) => {
    if (total === 1) return 50;
    return ((index + 1) * 100) / (total + 1);
  };

  // Calculate output positions for proper alignment
  const getOutputPosition = (index: number, total: number) => {
    if (total === 1) return 50;
    return ((index + 1) * 100) / (total + 1);
  };

  return (
    <div
      className={`group bg-white border-2 rounded-lg min-w-[120px] shadow-lg transition-all ${
        selected ? 'border-blue-500 shadow-xl' : 'border-gray-300'
      }`}
    >
      {/* Input Handles */}
      {Array.from({ length: component.inputs }, (_, index) => (
        <Handle
          key={`input-${index}`}
          type="target"
          position={Position.Left}
          id={`input-${index}`}
          style={{
            top: `${getInputPosition(index, component.inputs)}%`,
            background: '#3b82f6',
          }}
          className="w-3 h-3"
        />
      ))}

      {/* Output Handles */}
      {Array.from({ length: component.outputs }, (_, index) => (
        <Handle
          key={`output-${index}`}
          type="source"
          position={Position.Right}
          id={`output-${index}`}
          style={{
            top: `${getOutputPosition(index, component.outputs)}%`,
            background: '#10b981',
          }}
          className="w-3 h-3"
        />
      ))}

      <div className="p-2">
        {/* Simplified Node Header - Only Icon and Label */}
        <div className="flex items-center gap-2">
          <div className="w-6 h-6 flex items-center justify-center bg-gray-100 rounded">
            {component.icon && component.icon.endsWith('.svg') ? (
              <Image
                src={component.icon}
                alt={component.name}
                width={20}
                height={20}
                className="w-5 h-5"
              />
            ) : (
              <span className="text-xs font-bold">{component.name[0]}</span>
            )}
          </div>
          
          <div className="flex-1 flex items-center gap-1">
            {isEditing ? (
              <div className="flex items-center gap-1 flex-1">
                <input
                  value={editLabel}
                  onChange={(e) => setEditLabel(e.target.value)}
                  onKeyDown={handleLabelKeyDown}
                  className="flex-1 px-1 py-0.5 text-xs border border-gray-300 rounded focus:outline-none focus:border-blue-500"
                  autoFocus
                />
                <button
                  onClick={handleLabelEdit}
                  className="p-0.5 text-green-600 hover:bg-green-100 rounded"
                >
                  <Check size={10} />
                </button>
                <button
                  onClick={handleLabelCancel}
                  className="p-0.5 text-red-600 hover:bg-red-100 rounded"
                >
                  <X size={10} />
                </button>
              </div>
            ) : (
              <div className="flex items-center gap-1 flex-1">
                <span className="text-xs font-medium truncate">{data.label}</span>
                <button
                  onClick={handleLabelEdit}
                  className="p-0.5 text-gray-400 hover:text-gray-600 hover:bg-gray-100 rounded opacity-0 group-hover:opacity-100"
                >
                  <Edit3 size={10} />
                </button>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}

export default memo(BSM2Node);