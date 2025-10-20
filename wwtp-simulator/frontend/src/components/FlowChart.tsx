'use client';

import React, { useCallback, useState, useRef } from 'react';
import {
  ReactFlow,
  Node,
  Edge,
  addEdge,
  useNodesState,
  useEdgesState,
  Connection,
  Background,
  Controls,
  MiniMap,
} from '@xyflow/react';
import '@xyflow/react/dist/style.css';

import Sidebar from './Sidebar';
import BSM2Node from './BSM2Node';
import { FlowNode, FlowEdge, SidebarTab } from '@/types';
import { v4 as uuidv4 } from 'uuid';

const nodeTypes = {
  'bsm2-component': BSM2Node,
};

const initialNodes: Node[] = [];
const initialEdges: Edge[] = [];

export default function FlowChart() {
  const [nodes, setNodes, onNodesChange] = useNodesState(initialNodes);
  const [edges, setEdges, onEdgesChange] = useEdgesState(initialEdges);
  const [activeTab, setActiveTab] = useState<SidebarTab>('components');
  const [selectedNode, setSelectedNode] = useState<FlowNode | null>(null);
  const [selectedEdge, setSelectedEdge] = useState<FlowEdge | null>(null);
  
  const reactFlowWrapper = useRef<HTMLDivElement>(null);

  const onConnect = useCallback(
    (params: Connection) => {
      // Validate connection - each port can only have one connection
      const existingSourceConnection = edges.find(
        (edge) => edge.source === params.source && edge.sourceHandle === params.sourceHandle
      );
      const existingTargetConnection = edges.find(
        (edge) => edge.target === params.target && edge.targetHandle === params.targetHandle
      );

      if (existingSourceConnection || existingTargetConnection) {
        console.warn('Connection already exists or port already connected');
        return;
      }

      const newEdge: Edge = {
        ...params,
        id: uuidv4(),
        data: { label: `${params.sourceHandle} → ${params.targetHandle}` },
      };
      
      setEdges((eds) => addEdge(newEdge, eds));
    },
    [edges, setEdges]
  );

  const onNodesDelete = useCallback(
    (deletedNodes: Node[]) => {
      const deletedNodeIds = deletedNodes.map(node => node.id);
      setEdges((eds) => eds.filter(
        (edge) => !deletedNodeIds.includes(edge.source) && !deletedNodeIds.includes(edge.target)
      ));
    },
    [setEdges]
  );

  const onEdgesDelete = useCallback(
    (deletedEdges: Edge[]) => {
      console.log('Edges deleted:', deletedEdges);
    },
    []
  );

  const onNodeClick = useCallback(
    (event: React.MouseEvent, node: Node) => {
      setSelectedNode(node as FlowNode);
      setSelectedEdge(null);
      setActiveTab('details');
    },
    []
  );

  const onEdgeClick = useCallback(
    (event: React.MouseEvent, edge: Edge) => {
      setSelectedEdge(edge as FlowEdge);
      setSelectedNode(null);
      setActiveTab('details');
    },
    []
  );

  const onDragOver = useCallback((event: React.DragEvent) => {
    event.preventDefault();
    event.dataTransfer.dropEffect = 'move';
  }, []);

  const onDrop = useCallback(
    (event: React.DragEvent) => {
      event.preventDefault();

      if (!reactFlowWrapper.current) return;

      const reactFlowBounds = reactFlowWrapper.current.getBoundingClientRect();
      const componentType = event.dataTransfer.getData('application/reactflow');

      if (!componentType) return;

      const position = {
        x: event.clientX - reactFlowBounds.left,
        y: event.clientY - reactFlowBounds.top,
      };

      const newNode: Node = {
        id: uuidv4(),
        type: 'bsm2-component',
        position,
        data: {
          label: componentType.replace('-', ' ').replace(/\b\w/g, l => l.toUpperCase()),
          componentType,
          parameters: {},
          isSelected: false,
        },
      };

      setNodes((nds) => nds.concat(newNode));
    },
    [setNodes]
  );

  const updateNodeData = useCallback(
    (nodeId: string, data: Partial<FlowNode['data']>) => {
      setNodes((nds) =>
        nds.map((node) => {
          if (node.id === nodeId) {
            return { ...node, data: { ...node.data, ...data } };
          }
          return node;
        })
      );
    },
    [setNodes]
  );

  return (
    <div className="flex h-full">
      <div className="flex-1" ref={reactFlowWrapper}>
        <ReactFlow
          nodes={nodes}
          edges={edges}
          onNodesChange={onNodesChange}
          onEdgesChange={onEdgesChange}
          onConnect={onConnect}
          onNodesDelete={onNodesDelete}
          onEdgesDelete={onEdgesDelete}
          onNodeClick={onNodeClick}
          onEdgeClick={onEdgeClick}
          onDrop={onDrop}
          onDragOver={onDragOver}
          nodeTypes={nodeTypes}
          fitView
          className="bg-gray-50"
        >
          <Background />
          <Controls />
          <MiniMap 
            nodeColor={(node) => {
              switch (node.data.componentType) {
                case 'asm1-reactor':
                  return '#3b82f6';
                case 'adm1-reactor':
                  return '#10b981';
                case 'primary-clarifier':
                case 'settler':
                  return '#8b5cf6';
                case 'thickener':
                case 'dewatering':
                  return '#f59e0b';
                case 'storage':
                  return '#6b7280';
                case 'combiner':
                case 'splitter':
                  return '#ef4444';
                default:
                  return '#9ca3af';
              }
            }}
          />
        </ReactFlow>
      </div>
      
      <Sidebar
        activeTab={activeTab}
        onTabChange={setActiveTab}
        selectedNode={selectedNode}
        selectedEdge={selectedEdge}
        onNodeUpdate={updateNodeData}
        nodes={nodes as FlowNode[]}
        edges={edges as FlowEdge[]}
      />
    </div>
  );
}