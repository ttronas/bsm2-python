// BSM2 Component Types based on bsm2-python library
export interface BSM2ComponentType {
  id: string;
  name: string;
  icon: string;
  inputs: ComponentPort[];
  outputs: ComponentPort[];
  parameters: ComponentParameter[];
  description: string;
}

export interface ComponentPort {
  id: string;
  name: string;
  position: 'left' | 'right' | 'top' | 'bottom';
}

export interface ComponentParameter {
  id: string;
  name: string;
  type: 'number' | 'boolean' | 'string';
  defaultValue: string | number | boolean;
  unit?: string;
  description?: string;
  min?: number;
  max?: number;
}

// Flow Chart Types
export interface FlowNode {
  id: string;
  type: string;
  position: { x: number; y: number };
  data: {
    label: string;
    componentType: string;
    parameters: Record<string, string | number | boolean>;
    isSelected: boolean;
  };
}

export interface FlowEdge {
  id: string;
  source: string;
  target: string;
  sourceHandle: string;
  targetHandle: string;
  data?: {
    label: string;
  };
}

// Simulation Types
export interface SimulationConfig {
  id?: string;
  name: string;
  description?: string;
  nodes: FlowNode[];
  edges: FlowEdge[];
  settings: {
    timestep: number; // minutes
    endTime: number; // days
    startTime?: number;
  };
  createdAt?: string;
  updatedAt?: string;
}

export interface SimulationResult {
  id: string;
  configId: string;
  status: 'running' | 'completed' | 'failed';
  progress: number;
  results?: {
    [edgeId: string]: {
      timestep: number[];
      values: number[][];
    };
  };
  error?: string;
  createdAt: string;
  completedAt?: string;
}

// API Types
export interface APIResponse<T> {
  success: boolean;
  data?: T;
  error?: string;
  message?: string;
}

export interface SimulationProgress {
  progress: number;
  currentTime: number;
  totalTime: number;
  status: 'running' | 'completed' | 'failed';
  message?: string;
}

// Sidebar Tab Types
export type SidebarTab = 'components' | 'details' | 'settings' | 'results';

// State Variable Names (21 components from BSM2-Python)
export const BSM2_VARIABLES = [
  'SI', 'SS', 'XI', 'XS', 'XBH', 'XBA', 'XP', 'SO', 'SNO', 'SNH', 
  'SND', 'XND', 'SALK', 'TSS', 'Q', 'TEMP', 'SD1', 'SD2', 'SD3', 'XD4', 'XD5'
] as const;

export type BSM2Variable = typeof BSM2_VARIABLES[number];