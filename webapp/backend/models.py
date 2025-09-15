"""
Pydantic models for the BSM2 simulation API
"""

from pydantic import BaseModel, Field
from typing import Dict, List, Any, Optional, Union
from enum import Enum


class ComponentType(str, Enum):
    """Available component types in BSM2"""
    ASM1_REACTOR = "asm1_reactor"
    ADM1_REACTOR = "adm1_reactor"
    PRIMARY_CLARIFIER = "primary_clarifier"
    SETTLER = "settler"
    THICKENER = "thickener"
    DEWATERING = "dewatering"
    STORAGE = "storage"
    SPLITTER = "splitter"
    COMBINER = "combiner"
    INFLUENT = "influent"


class NodeConfig(BaseModel):
    """Configuration for a single node in the flowsheet"""
    id: str
    type: ComponentType
    name: str
    position: Dict[str, float]  # {x: float, y: float}
    parameters: Dict[str, Any] = Field(default_factory=dict)


class EdgeConfig(BaseModel):
    """Configuration for a connection between nodes"""
    id: str
    source: str
    target: str
    source_handle: str
    target_handle: str


class InfluentConfig(BaseModel):
    """Configuration for influent data"""
    type: str  # "constant" or "dynamic"
    file_data: Optional[List[List[float]]] = None
    constant_values: Optional[List[float]] = None


class SimulationConfig(BaseModel):
    """Complete simulation configuration"""
    name: str
    nodes: List[NodeConfig]
    edges: List[EdgeConfig]
    influent: InfluentConfig
    timestep: float = Field(default=1.0/24/60, description="Timestep in days (default: 1 minute)")
    end_time: float = Field(default=7.0, description="End time in days")
    user_id: Optional[str] = None


class SimulationProgress(BaseModel):
    """Simulation progress update"""
    simulation_id: str
    progress: float  # 0.0 to 1.0
    current_time: float
    status: str
    message: str


class ComponentResult(BaseModel):
    """Results for a single component"""
    component_id: str
    component_name: str
    outputs: Dict[str, List[float]]  # output_name -> time series data
    time: List[float]


class SimulationResult(BaseModel):
    """Complete simulation results"""
    simulation_id: str
    config: SimulationConfig
    components: List[ComponentResult]
    metadata: Dict[str, Any]
    created_at: str