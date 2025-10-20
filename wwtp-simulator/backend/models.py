"""
Pydantic models for the WWTP Simulator API.
"""

from pydantic import BaseModel, Field
from typing import Dict, List, Optional, Union, Any
from datetime import datetime

class ComponentPort(BaseModel):
    """Model for component input/output ports."""
    id: str
    name: str
    position: str = Field(..., pattern="^(left|right|top|bottom)$")

class ComponentParameter(BaseModel):
    """Model for component parameters."""
    id: str
    name: str
    type: str = Field(..., pattern="^(number|boolean|string)$")
    defaultValue: Union[str, int, float, bool]
    unit: Optional[str] = None
    description: Optional[str] = None
    min: Optional[float] = None
    max: Optional[float] = None

class BSM2ComponentType(BaseModel):
    """Model for BSM2 component type definition."""
    id: str
    name: str
    icon: str
    inputs: List[ComponentPort]
    outputs: List[ComponentPort]
    parameters: List[ComponentParameter]
    description: str

class FlowNode(BaseModel):
    """Model for a flow chart node."""
    id: str
    type: str
    position: Dict[str, float]  # {x, y}
    data: Dict[str, Any]  # Contains label, componentType, parameters, etc.

class FlowEdge(BaseModel):
    """Model for a flow chart edge."""
    id: str
    source: str
    target: str
    sourceHandle: str
    targetHandle: str
    data: Optional[Dict[str, Any]] = None

class SimulationSettings(BaseModel):
    """Model for simulation settings."""
    timestep: int = Field(..., ge=1, le=1440, description="Timestep in minutes")
    endTime: float = Field(..., gt=0, le=365, description="End time in days")
    startTime: float = Field(default=0, ge=0, description="Start time in days")

class SimulationConfig(BaseModel):
    """Model for complete simulation configuration."""
    id: Optional[str] = None
    name: str
    description: Optional[str] = None
    nodes: List[FlowNode]
    edges: List[FlowEdge]
    settings: SimulationSettings
    createdAt: Optional[str] = None
    updatedAt: Optional[str] = None

class SimulationResult(BaseModel):
    """Model for simulation results."""
    id: str
    configId: str
    status: str = Field(..., pattern="^(running|completed|failed)$")
    progress: float = Field(..., ge=0, le=100)
    results: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    createdAt: str
    completedAt: Optional[str] = None

class SimulationProgress(BaseModel):
    """Model for simulation progress updates."""
    progress: float = Field(..., ge=0, le=100)
    currentTime: float
    totalTime: float
    status: str = Field(..., pattern="^(running|completed|failed)$")
    message: Optional[str] = None

class APIResponse(BaseModel):
    """Generic API response model."""
    success: bool
    data: Optional[Any] = None
    error: Optional[str] = None
    message: Optional[str] = None

class ComponentValidationError(Exception):
    """Exception raised when component configuration is invalid."""
    pass

class SimulationError(Exception):
    """Exception raised when simulation fails."""
    pass