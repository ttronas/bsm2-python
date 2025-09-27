'use client'

import React from 'react'
import { Node, Edge } from 'reactflow'
import { 
  Package, 
  Settings, 
  Play, 
  BarChart3,
  X,
  Trash2,
  Download,
  Upload
} from 'lucide-react'

import { ComponentDefinition, NodeData, TabConfig } from '@/types'
import { cn } from '@/lib/utils'

import ComponentsTab from './sidebar/ComponentsTab'
import DetailsTab from './sidebar/DetailsTab'
import SimulationTab from './sidebar/SimulationTab'
import ResultsTab from './sidebar/ResultsTab'

const tabs: TabConfig[] = [
  { id: 'components', label: 'Components', icon: Package },
  { id: 'details', label: 'Details', icon: Settings },
  { id: 'simulation', label: 'Simulation', icon: Play },
  { id: 'results', label: 'Results', icon: BarChart3 },
]

interface SidebarProps {
  activeTab: string
  onTabChange: (tabId: string) => void
  availableComponents: ComponentDefinition[]
  selectedNode: Node | null
  selectedEdge: Edge | null
  onNodeUpdate: (nodeId: string, newData: Partial<NodeData>) => void
  onNodeDelete: (nodeId: string) => void
  onEdgeDelete: (edgeId: string) => void
  onExportFlowsheet: () => void
  onImportFlowsheet: (file: File) => void
  onRunSimulation: () => void
  simulationRunning: boolean
  simulationProgress: number
}

export default function Sidebar({
  activeTab,
  onTabChange,
  availableComponents,
  selectedNode,
  selectedEdge,
  onNodeUpdate,
  onNodeDelete,
  onEdgeDelete,
  onExportFlowsheet,
  onImportFlowsheet,
  onRunSimulation,
  simulationRunning,
  simulationProgress,
}: SidebarProps) {
  const handleFileImport = (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0]
    if (file) {
      onImportFlowsheet(file)
      event.target.value = '' // Reset file input
    }
  }

  const renderTabContent = () => {
    switch (activeTab) {
      case 'components':
        return (
          <ComponentsTab
            components={availableComponents}
            onExport={onExportFlowsheet}
            onImport={handleFileImport}
          />
        )
      case 'details':
        return (
          <DetailsTab
            selectedNode={selectedNode}
            selectedEdge={selectedEdge}
            onNodeUpdate={onNodeUpdate}
            onNodeDelete={onNodeDelete}
            onEdgeDelete={onEdgeDelete}
          />
        )
      case 'simulation':
        return (
          <SimulationTab
            onRunSimulation={onRunSimulation}
            simulationRunning={simulationRunning}
            simulationProgress={simulationProgress}
          />
        )
      case 'results':
        return <ResultsTab />
      default:
        return null
    }
  }

  return (
    <div className="w-80 bg-white border-l border-gray-200 flex flex-col h-full">
      {/* Tab Headers */}
      <div className="flex border-b border-gray-200">
        {tabs.map((tab) => {
          const Icon = tab.icon
          return (
            <button
              key={tab.id}
              onClick={() => onTabChange(tab.id)}
              className={cn(
                "flex-1 px-3 py-3 text-xs font-medium flex flex-col items-center space-y-1 transition-colors",
                activeTab === tab.id
                  ? "bg-blue-50 text-blue-600 border-b-2 border-blue-600"
                  : "text-gray-600 hover:text-gray-900 hover:bg-gray-50"
              )}
            >
              <Icon size={16} />
              <span>{tab.label}</span>
            </button>
          )
        })}
      </div>

      {/* Tab Content */}
      <div className="flex-1 overflow-y-auto">
        {renderTabContent()}
      </div>
    </div>
  )
}