'use client';

import React from 'react';
import { SidebarTab, FlowNode, FlowEdge } from '@/types';
import ComponentsTab from './sidebar/ComponentsTab';
import DetailsTab from './sidebar/DetailsTab';
import SettingsTab from './sidebar/SettingsTab';
import ResultsTab from './sidebar/ResultsTab';

interface SidebarProps {
  activeTab: SidebarTab;
  onTabChange: (tab: SidebarTab) => void;
  selectedNode: FlowNode | null;
  selectedEdge: FlowEdge | null;
  onNodeUpdate: (nodeId: string, data: Partial<FlowNode['data']>) => void;
  nodes: FlowNode[];
  edges: FlowEdge[];
}

const tabs: { id: SidebarTab; label: string; icon: string }[] = [
  { id: 'components', label: 'Components', icon: '🧩' },
  { id: 'details', label: 'Details', icon: '⚙️' },
  { id: 'settings', label: 'Simulation', icon: '🎯' },
  { id: 'results', label: 'Results', icon: '📊' },
];

export default function Sidebar({
  activeTab,
  onTabChange,
  selectedNode,
  selectedEdge,
  onNodeUpdate,
  nodes,
  edges,
}: SidebarProps) {
  return (
    <div className="w-80 bg-white border-l border-gray-200 flex flex-col">
      {/* Tab Navigation */}
      <div className="flex border-b border-gray-200">
        {tabs.map((tab) => (
          <button
            key={tab.id}
            onClick={() => onTabChange(tab.id)}
            className={`flex-1 p-3 text-sm font-medium transition-colors ${
              activeTab === tab.id
                ? 'bg-blue-50 text-blue-700 border-b-2 border-blue-700'
                : 'text-gray-600 hover:text-gray-900 hover:bg-gray-50'
            }`}
          >
            <div className="flex flex-col items-center gap-1">
              <span className="text-lg">{tab.icon}</span>
              <span>{tab.label}</span>
            </div>
          </button>
        ))}
      </div>

      {/* Tab Content */}
      <div className="flex-1 overflow-y-auto">
        {activeTab === 'components' && <ComponentsTab />}
        {activeTab === 'details' && (
          <DetailsTab
            selectedNode={selectedNode}
            selectedEdge={selectedEdge}
            onNodeUpdate={onNodeUpdate}
          />
        )}
        {activeTab === 'settings' && (
          <SettingsTab
            nodes={nodes}
            edges={edges}
          />
        )}
        {activeTab === 'results' && (
          <ResultsTab
            nodes={nodes}
            edges={edges}
          />
        )}
      </div>
    </div>
  );
}