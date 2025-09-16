"""
BSM2 Simulation Web API

This FastAPI application provides a REST API for running BSM2 wastewater treatment
plant simulations with dynamic configuration from a React Flow frontend.
"""

from fastapi import FastAPI, HTTPException, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
import uvicorn
import asyncio
import json
import uuid
from typing import Dict, List, Any, Optional
import os
import sys
from pathlib import Path

# Add the bsm2_python package to the path
repo_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(repo_root / "src"))

from simulation_engine import SimulationEngine
from models import (
    SimulationConfig,
    SimulationResult,
    NodeConfig,
    EdgeConfig,
    ComponentType
)
from supabase_client import SupabaseClient

app = FastAPI(
    title="BSM2 Simulation API",
    description="API for running dynamic BSM2 wastewater treatment plant simulations",
    version="1.0.0"
)

# Enable CORS for frontend communication
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # Next.js dev server
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global storage for active simulations and WebSocket connections
active_simulations: Dict[str, SimulationEngine] = {}
websocket_connections: Dict[str, WebSocket] = {}

# Initialize Supabase client
supabase_client = SupabaseClient()

@app.get("/")
async def root():
    """Health check endpoint"""
    return {"message": "BSM2 Simulation API is running"}

@app.get("/api/components")
async def get_available_components():
    """Get list of available BSM2 components for the frontend with proper BSM2 parameters"""
    components = [
        {
            "id": "asm1_reactor",
            "name": "ASM1 Reactor",
            "type": ComponentType.ASM1_REACTOR,
            "icon": "activated-sludge-reactor.svg",
            "inputs": ["influent"],
            "outputs": ["effluent"],
            "parameters": {
                "kla": {"type": "float", "default": 120.0, "description": "Oxygen transfer coefficient [d⁻¹]"},
                "volume": {"type": "float", "default": 1333.0, "description": "Reactor volume [m³]"},
                "carb": {"type": "float", "default": 2.0, "description": "External carbon flow rate [kg(COD)⋅d⁻¹]"},
                "csourceconc": {"type": "float", "default": 400000.0, "description": "Carbon source concentration [g(COD)⋅m⁻³]"},
                "tempmodel": {"type": "boolean", "default": False, "description": "Use temperature model"},
                "activate": {"type": "boolean", "default": True, "description": "Activate dummy states"}
            }
        },
        {
            "id": "primary_clarifier",
            "name": "Primary Clarifier",
            "type": ComponentType.PRIMARY_CLARIFIER,
            "icon": "primary-clarifier.svg",
            "inputs": ["influent"],
            "outputs": ["effluent", "sludge"],
            "parameters": {
                "vol_p": {"type": "float", "default": 900.0, "description": "Primary clarifier volume [m³]"},
                "area_p": {"type": "float", "default": 1500.0, "description": "Primary clarifier area [m²]"}
            }
        },
        {
            "id": "settler",
            "name": "Secondary Clarifier",
            "type": ComponentType.SETTLER,
            "icon": "settler.svg",
            "inputs": ["influent"],
            "outputs": ["effluent", "sludge"],
            "parameters": {
                "vol_s": {"type": "float", "default": 6000.0, "description": "Settler volume [m³]"},
                "area_s": {"type": "float", "default": 1500.0, "description": "Settler area [m²]"},
                "height_s": {"type": "float", "default": 4.0, "description": "Settler height [m]"},
                "tempmodel": {"type": "boolean", "default": False, "description": "Use temperature model"}
            }
        },
        {
            "id": "adm1_reactor",
            "name": "ADM1 Digester",
            "type": ComponentType.ADM1_REACTOR,
            "icon": "anerobic-digester.svg",
            "inputs": ["sludge"],
            "outputs": ["effluent", "biogas"],
            "parameters": {
                "volume": {"type": "float", "default": 3400.0, "description": "Digester volume [m³]"},
                "tempmodel": {"type": "boolean", "default": False, "description": "Use temperature model"}
            }
        },
        {
            "id": "thickener",
            "name": "Thickener",
            "type": ComponentType.THICKENER,
            "icon": "thickener.svg",
            "inputs": ["sludge"],
            "outputs": ["thickened_sludge", "filtrate"],
            "parameters": {
                "vol_t": {"type": "float", "default": 1000.0, "description": "Thickener volume [m³]"},
                "area_t": {"type": "float", "default": 250.0, "description": "Thickener area [m²]"},
                "height_t": {"type": "float", "default": 4.0, "description": "Thickener height [m]"}
            }
        },
        {
            "id": "dewatering",
            "name": "Dewatering",
            "type": ComponentType.DEWATERING,
            "icon": "dewatering.svg",
            "inputs": ["sludge"],
            "outputs": ["dewatered_sludge", "filtrate"],
            "parameters": {
                "dry_solids": {"type": "float", "default": 0.25, "description": "Target dry solids content [-]"}
            }
        },
        {
            "id": "storage",
            "name": "Storage Tank",
            "type": ComponentType.STORAGE,
            "icon": "wastewater-storage.svg",
            "inputs": ["influent"],
            "outputs": ["effluent"],
            "parameters": {
                "vol_st": {"type": "float", "default": 6000.0, "description": "Storage volume [m³]"},
                "area_st": {"type": "float", "default": 1500.0, "description": "Storage area [m²]"},
                "height_st": {"type": "float", "default": 4.0, "description": "Storage height [m]"}
            }
        },
        {
            "id": "splitter",
            "name": "Splitter",
            "type": ComponentType.SPLITTER,
            "icon": "splitter.svg",
            "inputs": ["influent"],
            "outputs": ["output1", "output2"],
            "parameters": {
                "sp_type": {"type": "int", "default": 1, "description": "Splitter type (1 or 2)"}
            }
        },
        {
            "id": "combiner",
            "name": "Combiner",
            "type": ComponentType.COMBINER,
            "icon": "combiner.svg",
            "inputs": ["input1", "input2"],
            "outputs": ["combined"],
            "parameters": {}
        },
        {
            "id": "influent",
            "name": "Influent",
            "type": ComponentType.INFLUENT,
            "icon": "influent.svg",
            "inputs": [],
            "outputs": ["effluent"],
            "parameters": {
                "type": {"type": "select", "options": ["constant", "dynamic"], "default": "dynamic"},
                "file": {"type": "file", "description": "CSV file for dynamic influent"}
            }
        }
    ]
    return {"components": components}

@app.post("/api/simulation/start")
async def start_simulation(config: SimulationConfig):
    """Start a new simulation with the given configuration"""
    simulation_id = str(uuid.uuid4())
    
    try:
        # Create simulation engine
        engine = SimulationEngine(config, simulation_id)
        active_simulations[simulation_id] = engine
        
        # Save configuration to Supabase
        await supabase_client.save_simulation_config(simulation_id, config)
        
        return {
            "simulation_id": simulation_id,
            "status": "created",
            "message": "Simulation created successfully"
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to create simulation: {str(e)}")

@app.websocket("/api/simulation/ws/{simulation_id}")
async def simulation_websocket(websocket: WebSocket, simulation_id: str):
    """WebSocket endpoint for real-time simulation updates"""
    await websocket.accept()
    websocket_connections[simulation_id] = websocket
    
    if simulation_id not in active_simulations:
        await websocket.send_json({"error": "Simulation not found"})
        return
    
    engine = active_simulations[simulation_id]
    
    try:
        # Run simulation and stream progress
        await engine.run_simulation_async(websocket)
        
        # Save results to Supabase
        results = engine.get_results()
        await supabase_client.save_simulation_results(simulation_id, results)
        
    except WebSocketDisconnect:
        pass
    except Exception as e:
        await websocket.send_json({"error": str(e)})
    finally:
        if simulation_id in websocket_connections:
            del websocket_connections[simulation_id]

@app.get("/api/simulation/{simulation_id}/results")
async def get_simulation_results(simulation_id: str):
    """Get simulation results"""
    if simulation_id in active_simulations:
        engine = active_simulations[simulation_id]
        results = engine.get_results()
        return {"results": results}
    
    # Try to get from Supabase
    results = await supabase_client.get_simulation_results(simulation_id)
    if results:
        return {"results": results}
    
    raise HTTPException(status_code=404, detail="Simulation not found")

@app.get("/api/simulation/{simulation_id}/status")
async def get_simulation_status(simulation_id: str):
    """Get simulation status"""
    if simulation_id in active_simulations:
        engine = active_simulations[simulation_id]
        return {
            "status": engine.status,
            "progress": engine.progress,
            "current_time": engine.current_time
        }
    
    raise HTTPException(status_code=404, detail="Simulation not found")

@app.delete("/api/simulation/{simulation_id}")
async def stop_simulation(simulation_id: str):
    """Stop and remove a simulation"""
    if simulation_id in active_simulations:
        engine = active_simulations[simulation_id]
        engine.stop()
        del active_simulations[simulation_id]
        
        if simulation_id in websocket_connections:
            del websocket_connections[simulation_id]
        
        return {"message": "Simulation stopped"}
    
    raise HTTPException(status_code=404, detail="Simulation not found")

@app.get("/api/icons/{icon_name}")
async def get_icon(icon_name: str):
    """Serve component icons"""
    icon_path = repo_root / "docs" / "assets" / "icons" / "bsm2python" / icon_name
    if icon_path.exists():
        return FileResponse(icon_path)
    
    raise HTTPException(status_code=404, detail="Icon not found")

@app.get("/api/configurations")
async def get_saved_configurations(user_id: Optional[str] = None):
    """Get saved simulation configurations"""
    configs = await supabase_client.get_saved_configurations(user_id)
    return {"configurations": configs}

@app.post("/api/configurations/save")
async def save_configuration(config: Dict[str, Any]):
    """Save a simulation configuration"""
    config_id = await supabase_client.save_configuration(config)
    return {"config_id": config_id}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)