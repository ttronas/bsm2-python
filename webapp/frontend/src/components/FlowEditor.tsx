'use client'

import React, { useState, useCallback, useRef, useEffect } from 'react'
import ReactFlow, {
  Node,
  Edge,
  addEdge,
  Connection,
  useNodesState,
  useEdgesState,
  Controls,
  MiniMap,
  Background,
  ReactFlowProvider,
} from 'reactflow'
import 'reactflow/dist/style.css'

import { ComponentType, ComponentDefinition, NodeData, SimulationConfig } from '@/types'
import { generateId } from '@/lib/utils'
import { apiClient } from '@/lib/api'

import ComponentNode from './nodes/ComponentNode'
import Sidebar from './Sidebar'

const nodeTypes = {
  component: ComponentNode,
}

const initialNodes: Node[] = []
const initialEdges: Edge[] = []

export default function FlowEditor() {
  const [nodes, setNodes, onNodesChange] = useNodesState(initialNodes)
  const [edges, setEdges, onEdgesChange] = useEdgesState(initialEdges)
  const [selectedNode, setSelectedNode] = useState<Node | null>(null)
  const [selectedEdge, setSelectedEdge] = useState<Edge | null>(null)
  const [availableComponents, setAvailableComponents] = useState<ComponentDefinition[]>([])
  const [activeTab, setActiveTab] = useState('components')
  const [simulationRunning, setSimulationRunning] = useState(false)
  const [simulationProgress, setSimulationProgress] = useState(0)
  
  const reactFlowWrapper = useRef<HTMLDivElement>(null)

  // Load available components on mount
  useEffect(() => {
    loadComponents()
  }, [])

  const loadComponents = async () => {
    try {
      const response = await apiClient.getComponents()
      setAvailableComponents(response.components)
    } catch (error) {
      console.error('Failed to load components:', error)
    }
  }

  const onConnect = useCallback(
    (params: Connection) => {
      const edge = {
        ...params,
        id: generateId(),
        source_handle: params.sourceHandle || 'effluent',
        target_handle: params.targetHandle || 'influent',
      }
      setEdges((eds) => addEdge(edge, eds))
    },
    [setEdges]
  )

  const onDragOver = useCallback((event: React.DragEvent) => {
    event.preventDefault()
    event.dataTransfer.dropEffect = 'move'
  }, [])

  const onDrop = useCallback(
    (event: React.DragEvent) => {
      event.preventDefault()

      const type = event.dataTransfer.getData('application/reactflow')
      
      if (typeof type === 'undefined' || !type) {
        return
      }

      const reactFlowBounds = reactFlowWrapper.current?.getBoundingClientRect()
      if (!reactFlowBounds) return

      const component = availableComponents.find(c => c.type === type)
      if (!component) return

      const position = {
        x: event.clientX - reactFlowBounds.left - 75, // Center the node
        y: event.clientY - reactFlowBounds.top - 50,
      }

      const newNode: Node<NodeData> = {
        id: generateId(),
        type: 'component',
        position,
        data: {
          id: generateId(),
          type: component.type,
          name: component.name,
          parameters: Object.fromEntries(
            Object.entries(component.parameters).map(([key, param]) => [
              key,
              param.default,
            ])
          ),
          inputs: component.inputs,
          outputs: component.outputs,
          icon: component.icon,
        },
      }

      setNodes((nds) => nds.concat(newNode))
    },
    [reactFlowWrapper, availableComponents, setNodes]
  )

  const onNodeClick = useCallback((event: React.MouseEvent, node: Node) => {
    setSelectedNode(node)
    setSelectedEdge(null)
    setActiveTab('details')
  }, [])

  const onEdgeClick = useCallback((event: React.MouseEvent, edge: Edge) => {
    setSelectedEdge(edge)
    setSelectedNode(null)
  }, [])

  const onPaneClick = useCallback(() => {
    setSelectedNode(null)
    setSelectedEdge(null)
  }, [])

  const updateNodeData = useCallback((nodeId: string, newData: Partial<NodeData>) => {
    setNodes((nds) =>
      nds.map((node) =>
        node.id === nodeId
          ? { ...node, data: { ...node.data, ...newData } }
          : node
      )
    )
  }, [setNodes])

  const deleteNode = useCallback((nodeId: string) => {
    setNodes((nds) => nds.filter((node) => node.id !== nodeId))
    setEdges((eds) => eds.filter((edge) => edge.source !== nodeId && edge.target !== nodeId))
    setSelectedNode(null)
  }, [setNodes, setEdges])

  const deleteEdge = useCallback((edgeId: string) => {
    setEdges((eds) => eds.filter((edge) => edge.id !== edgeId))
    setSelectedEdge(null)
  }, [setEdges])

  const exportFlowsheet = useCallback(() => {
    const flowsheet = {
      nodes: nodes.map(node => ({
        id: node.id,
        type: node.data?.type,
        name: node.data?.name,
        position: node.position,
        parameters: node.data?.parameters,
      })),
      edges: edges.map(edge => ({
        id: edge.id,
        source: edge.source,
        target: edge.target,
        source_handle: edge.sourceHandle || 'effluent',
        target_handle: edge.targetHandle || 'influent',
      })),
    }

    const dataStr = JSON.stringify(flowsheet, null, 2)
    const dataUri = 'data:application/json;charset=utf-8,'+ encodeURIComponent(dataStr)
    
    const exportFileDefaultName = 'flowsheet.json'
    
    const linkElement = document.createElement('a')
    linkElement.setAttribute('href', dataUri)
    linkElement.setAttribute('download', exportFileDefaultName)
    linkElement.click()
  }, [nodes, edges])

  const importFlowsheet = useCallback((file: File) => {
    const reader = new FileReader()
    reader.onload = (e) => {
      try {
        const flowsheet = JSON.parse(e.target?.result as string)
        
        // Recreate nodes
        const importedNodes = flowsheet.nodes.map((nodeData: any) => ({
          id: nodeData.id,
          type: 'component',
          position: nodeData.position,
          data: {
            id: nodeData.id,
            type: nodeData.type,
            name: nodeData.name,
            parameters: nodeData.parameters,
            inputs: availableComponents.find(c => c.type === nodeData.type)?.inputs || [],
            outputs: availableComponents.find(c => c.type === nodeData.type)?.outputs || [],
            icon: availableComponents.find(c => c.type === nodeData.type)?.icon || '',
          },
        }))
        
        setNodes(importedNodes)
        setEdges(flowsheet.edges)
      } catch (error) {
        console.error('Failed to import flowsheet:', error)
        alert('Failed to import flowsheet. Please check the file format.')
      }
    }
    reader.readAsText(file)
  }, [availableComponents, setNodes, setEdges])

  const createSimulationConfig = useCallback((): SimulationConfig => {
    return {
      name: 'Simulation',
      nodes: nodes.map(node => ({
        id: node.id,
        type: node.data?.type as ComponentType,
        name: node.data?.name || '',
        position: node.position,
        parameters: node.data?.parameters || {},
      })),
      edges: edges.map(edge => ({
        id: edge.id,
        source: edge.source,
        target: edge.target,
        source_handle: edge.sourceHandle || 'effluent',
        target_handle: edge.targetHandle || 'influent',
      })),
      influent: {
        type: 'dynamic',
      },
      timestep: 1.0 / 24 / 60, // 1 minute in days
      end_time: 7.0, // 7 days
    }
  }, [nodes, edges])

  return (
    <div className="h-screen w-screen flex">
      <div className="flex-1 flex flex-col">
        {/* Header */}
        <div className="h-16 bg-white border-b border-gray-200 flex items-center justify-between px-4">
          <h1 className="text-xl font-bold">BSM2 Simulator</h1>
        </div>

        {/* Flow Editor */}
        <div className="flex-1" ref={reactFlowWrapper}>
          <ReactFlowProvider>
            <ReactFlow
              nodes={nodes}
              edges={edges}
              onNodesChange={onNodesChange}
              onEdgesChange={onEdgesChange}
              onConnect={onConnect}
              onDrop={onDrop}
              onDragOver={onDragOver}
              onNodeClick={onNodeClick}
              onEdgeClick={onEdgeClick}
              onPaneClick={onPaneClick}
              nodeTypes={nodeTypes}
              fitView
            >
              <Controls />
              <MiniMap />
              <Background gap={20} size={1} />
            </ReactFlow>
          </ReactFlowProvider>
        </div>
      </div>

      {/* Sidebar */}
      <Sidebar
        activeTab={activeTab}
        onTabChange={setActiveTab}
        availableComponents={availableComponents}
        selectedNode={selectedNode}
        selectedEdge={selectedEdge}
        onNodeUpdate={updateNodeData}
        onNodeDelete={deleteNode}
        onEdgeDelete={deleteEdge}
        onExportFlowsheet={exportFlowsheet}
        onImportFlowsheet={importFlowsheet}
        onRunSimulation={() => {
          const config = createSimulationConfig()
          console.log('Starting simulation with config:', config)
          // TODO: Implement simulation execution
        }}
        simulationRunning={simulationRunning}
        simulationProgress={simulationProgress}
      />
    </div>
  )
}