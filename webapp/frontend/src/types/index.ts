export enum ComponentType {
  ASM1_REACTOR = "asm1_reactor",
  ADM1_REACTOR = "adm1_reactor",
  PRIMARY_CLARIFIER = "primary_clarifier",
  SETTLER = "settler",
  THICKENER = "thickener",
  DEWATERING = "dewatering",
  STORAGE = "storage",
  SPLITTER = "splitter",
  COMBINER = "combiner",
  INFLUENT = "influent",
}

export interface ComponentParameter {
  type: 'float' | 'boolean' | 'select' | 'file';
  default?: any;
  description: string;
  options?: string[];
}

export interface ComponentDefinition {
  id: string;
  name: string;
  type: ComponentType;
  icon: string;
  inputs: string[];
  outputs: string[];
  parameters: Record<string, ComponentParameter>;
}

export interface NodeData {
  id: string;
  type: ComponentType;
  name: string;
  parameters: Record<string, any>;
  inputs: string[];
  outputs: string[];
  icon: string;
}

export interface SimulationConfig {
  name: string;
  nodes: Array<{
    id: string;
    type: ComponentType;
    name: string;
    position: { x: number; y: number };
    parameters: Record<string, any>;
  }>;
  edges: Array<{
    id: string;
    source: string;
    target: string;
    source_handle: string;
    target_handle: string;
  }>;
  influent: {
    type: 'constant' | 'dynamic';
    file_data?: number[][];
    constant_values?: number[];
  };
  timestep: number;
  end_time: number;
  user_id?: string;
}

export interface SimulationProgress {
  simulation_id: string;
  progress: number;
  current_time: number;
  status: string;
  message: string;
}

export interface SimulationResult {
  simulation_id: string;
  config: SimulationConfig;
  components: ComponentResult[];
  metadata: Record<string, any>;
}

export interface ComponentResult {
  component_id: string;
  component_name: string;
  outputs: Record<string, number[][]>;
  time: number[];
}

export interface TabConfig {
  id: string;
  label: string;
  icon: any; // Using any for Lucide React icons
}