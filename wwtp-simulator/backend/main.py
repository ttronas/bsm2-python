"""
WWTP Simulator Backend

FastAPI backend for wastewater treatment plant simulation using BSM2-Python.
Provides REST API endpoints for simulation configuration, execution, and results.
"""

from fastapi import FastAPI, HTTPException, BackgroundTasks, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import Dict, List, Optional, Any, Union
import asyncio
import uuid
import json
from datetime import datetime
import logging

# Import BSM2-Python components
try:
    from bsm2_python.bsm2.asm1_bsm2 import ASM1Reactor
    from bsm2_python.bsm2.adm1_bsm2 import ADM1Reactor
    from bsm2_python.bsm2.primclar_bsm2 import PrimaryClarifier
    from bsm2_python.bsm2.settler1d_bsm2 import Settler
    from bsm2_python.bsm2.thickener_bsm2 import Thickener
    from bsm2_python.bsm2.dewatering_bsm2 import Dewatering
    from bsm2_python.bsm2.storage_bsm2 import Storage
    from bsm2_python.bsm2.helpers_bsm2 import Combiner, Splitter
    from bsm2_python.bsm2.plantperformance import PlantPerformance
    BSM2_AVAILABLE = True
except ImportError as e:
    logging.warning(f"BSM2-Python not available: {e}")
    BSM2_AVAILABLE = False

from simulation_engine import SimulationEngine
from models import *

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# FastAPI app initialization
app = FastAPI(
    title="WWTP Simulator API",
    description="Wastewater Treatment Plant Simulation API using BSM2-Python",
    version="1.0.0",
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global state
simulation_engine = SimulationEngine()
active_simulations: Dict[str, Dict] = {}
websocket_connections: Dict[str, WebSocket] = {}

@app.get("/")
async def root():
    """Root endpoint with API information."""
    return {
        "message": "WWTP Simulator API",
        "version": "1.0.0",
        "bsm2_available": BSM2_AVAILABLE,
        "status": "running"
    }

@app.get("/api/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "bsm2_available": BSM2_AVAILABLE,
        "active_simulations": len(active_simulations),
        "timestamp": datetime.now().isoformat()
    }

@app.get("/api/components")
async def get_available_components():
    """Get list of available BSM2 components."""
    if not BSM2_AVAILABLE:
        raise HTTPException(status_code=500, detail="BSM2-Python library not available")
    
    components = [
        {
            "id": "asm1-reactor",
            "name": "ASM1 Reactor",
            "description": "Activated Sludge Model No. 1 reactor",
            "inputs": ["inlet"],
            "outputs": ["outlet"],
            "parameters": ["volume", "kla", "tempmodel", "activate"]
        },
        {
            "id": "adm1-reactor", 
            "name": "ADM1 Reactor",
            "description": "Anaerobic Digestion Model No. 1",
            "inputs": ["inlet"],
            "outputs": ["outlet", "gas"],
            "parameters": ["volume", "temperature"]
        },
        {
            "id": "primary-clarifier",
            "name": "Primary Clarifier",
            "description": "Primary sedimentation tank",
            "inputs": ["inlet"],
            "outputs": ["effluent", "sludge"],
            "parameters": ["area", "height"]
        },
        {
            "id": "settler",
            "name": "Settler",
            "description": "Secondary clarifier",
            "inputs": ["inlet"],
            "outputs": ["effluent", "underflow"],
            "parameters": ["area", "height"]
        },
        {
            "id": "thickener",
            "name": "Thickener",
            "description": "Sludge thickening tank",
            "inputs": ["inlet"],
            "outputs": ["overflow", "underflow"],
            "parameters": ["area", "height"]
        },
        {
            "id": "dewatering",
            "name": "Dewatering",
            "description": "Sludge dewatering unit",
            "inputs": ["inlet"],
            "outputs": ["filtrate", "cake"],
            "parameters": ["capture_efficiency", "cake_dryness"]
        },
        {
            "id": "storage",
            "name": "Storage Tank",
            "description": "Storage tank for wastewater or sludge",
            "inputs": ["inlet"],
            "outputs": ["outlet"],
            "parameters": ["volume", "delay"]
        },
        {
            "id": "combiner",
            "name": "Combiner",
            "description": "Combines multiple streams into one",
            "inputs": ["inlet1", "inlet2"],
            "outputs": ["outlet"],
            "parameters": []
        },
        {
            "id": "splitter",
            "name": "Splitter",
            "description": "Splits one stream into multiple streams",
            "inputs": ["inlet"],
            "outputs": ["outlet1", "outlet2"],
            "parameters": ["split_fraction"]
        }
    ]
    
    return {"components": components}

@app.post("/api/simulation/run")
async def run_simulation(config: SimulationConfig, background_tasks: BackgroundTasks):
    """Start a new simulation with the given configuration."""
    if not BSM2_AVAILABLE:
        raise HTTPException(status_code=500, detail="BSM2-Python library not available")
    
    # Generate simulation ID
    simulation_id = str(uuid.uuid4())
    
    # Validate configuration
    try:
        simulation_engine.validate_configuration(config)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Invalid configuration: {str(e)}")
    
    # Initialize simulation state
    active_simulations[simulation_id] = {
        "id": simulation_id,
        "config": config,
        "status": "initializing",
        "progress": 0,
        "results": {},
        "created_at": datetime.now().isoformat(),
        "error": None
    }
    
    # Start simulation in background
    background_tasks.add_task(run_simulation_task, simulation_id, config)
    
    return {
        "simulation_id": simulation_id,
        "status": "started",
        "message": "Simulation initiated successfully"
    }

@app.get("/api/simulation/{simulation_id}/status")
async def get_simulation_status(simulation_id: str):
    """Get the current status of a simulation."""
    if simulation_id not in active_simulations:
        raise HTTPException(status_code=404, detail="Simulation not found")
    
    sim = active_simulations[simulation_id]
    return {
        "id": simulation_id,
        "status": sim["status"],
        "progress": sim["progress"],
        "created_at": sim["created_at"],
        "completed_at": sim.get("completed_at"),
        "error": sim["error"]
    }

@app.get("/api/simulation/{simulation_id}/results")
async def get_simulation_results(simulation_id: str):
    """Get the results of a completed simulation."""
    if simulation_id not in active_simulations:
        raise HTTPException(status_code=404, detail="Simulation not found")
    
    sim = active_simulations[simulation_id]
    if sim["status"] != "completed":
        raise HTTPException(status_code=400, detail="Simulation not completed yet")
    
    return {
        "simulation_id": simulation_id,
        "results": sim["results"],
        "config": sim["config"],
        "status": sim["status"]
    }

@app.delete("/api/simulation/{simulation_id}")
async def cancel_simulation(simulation_id: str):
    """Cancel a running simulation."""
    if simulation_id not in active_simulations:
        raise HTTPException(status_code=404, detail="Simulation not found")
    
    sim = active_simulations[simulation_id]
    if sim["status"] == "running":
        sim["status"] = "cancelled"
        sim["error"] = "Simulation cancelled by user"
    
    return {"message": "Simulation cancelled"}

@app.post("/api/config/save")
async def save_configuration(config: SimulationConfig):
    """Save a simulation configuration."""
    # For now, just return success - in production this would save to database
    config_id = str(uuid.uuid4())
    return {
        "config_id": config_id,
        "message": "Configuration saved successfully"
    }

@app.get("/api/config/list")
async def list_configurations():
    """List saved simulation configurations."""
    # Mock data - in production this would come from database
    return {"configurations": []}

@app.websocket("/ws/simulation/{simulation_id}")
async def websocket_simulation_progress(websocket: WebSocket, simulation_id: str):
    """WebSocket endpoint for real-time simulation progress updates."""
    await websocket.accept()
    websocket_connections[simulation_id] = websocket
    
    try:
        # Send initial status
        if simulation_id in active_simulations:
            sim = active_simulations[simulation_id]
            await websocket.send_text(json.dumps({
                "type": "status_update",
                "simulation_id": simulation_id,
                "status": sim["status"],
                "progress": sim["progress"],
                "timestamp": datetime.now().isoformat()
            }))
        
        # Keep connection alive and send updates
        while True:
            await asyncio.sleep(1)
            if simulation_id in active_simulations:
                sim = active_simulations[simulation_id]
                await websocket.send_text(json.dumps({
                    "type": "progress_update",
                    "simulation_id": simulation_id,
                    "status": sim["status"],
                    "progress": sim["progress"],
                    "timestamp": datetime.now().isoformat()
                }))
                
                # Close connection if simulation is finished
                if sim["status"] in ["completed", "failed", "cancelled"]:
                    break
            else:
                break
                
    except WebSocketDisconnect:
        logger.info(f"WebSocket disconnected for simulation {simulation_id}")
    finally:
        if simulation_id in websocket_connections:
            del websocket_connections[simulation_id]

async def run_simulation_task(simulation_id: str, config: SimulationConfig):
    """Background task to run the actual simulation."""
    sim = active_simulations[simulation_id]
    
    try:
        sim["status"] = "running"
        
        # Run simulation using the simulation engine
        results = await simulation_engine.run_simulation(
            config, 
            progress_callback=lambda p: update_simulation_progress(simulation_id, p)
        )
        
        # Store results
        sim["results"] = results
        sim["status"] = "completed"
        sim["completed_at"] = datetime.now().isoformat()
        sim["progress"] = 100
        
        logger.info(f"Simulation {simulation_id} completed successfully")
        
    except Exception as e:
        sim["status"] = "failed"
        sim["error"] = str(e)
        sim["completed_at"] = datetime.now().isoformat()
        logger.error(f"Simulation {simulation_id} failed: {e}")

def update_simulation_progress(simulation_id: str, progress: float):
    """Update simulation progress and notify WebSocket clients."""
    if simulation_id in active_simulations:
        active_simulations[simulation_id]["progress"] = progress
        
        # Notify WebSocket clients
        if simulation_id in websocket_connections:
            websocket = websocket_connections[simulation_id]
            try:
                asyncio.create_task(websocket.send_text(json.dumps({
                    "type": "progress_update",
                    "simulation_id": simulation_id,
                    "progress": progress,
                    "timestamp": datetime.now().isoformat()
                })))
            except Exception:
                # WebSocket connection may be closed
                pass

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)