"""
Mock BSM2 Simulation Web API for Development

This is a development version of the FastAPI application that provides
mock responses for testing the frontend without requiring full BSM2 dependencies.
"""

from fastapi import FastAPI, HTTPException, WebSocket, WebSocketDisconnect, File, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, Response
import uvicorn
import asyncio
import json
import uuid
from typing import Dict, List, Any, Optional
import os
import sys
from pathlib import Path

from models import (
    SimulationConfig,
    SimulationResult,
    NodeConfig,
    EdgeConfig,
    ComponentType,
    ComponentDefinition,
    ComponentParameter
)

app = FastAPI(
    title="BSM2 Simulation API (Mock)",
    description="Mock API for BSM2 wastewater treatment plant simulations",
    version="1.0.0-mock"
)

# Enable CORS for frontend communication
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # Next.js dev server
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mock components data
mock_components = [
    ComponentDefinition(
        id="asm1_reactor",
        name="ASM1 Reactor",
        type=ComponentType.ASM1_REACTOR,
        icon="activated-sludge-reactor.svg",
        inputs=["influent"],
        outputs=["effluent"],
        parameters={
            "kla": ComponentParameter(type="float", default=240.0, description="Oxygen transfer coefficient"),
            "volume": ComponentParameter(type="float", default=1333.0, description="Reactor volume (m³)"),
            "activate": ComponentParameter(type="boolean", default=True, description="Activate aeration")
        }
    ),
    ComponentDefinition(
        id="primary_clarifier",
        name="Primary Clarifier",
        type=ComponentType.PRIMARY_CLARIFIER,
        icon="primary-clarifier.svg",
        inputs=["influent"],
        outputs=["effluent", "sludge"],
        parameters={
            "area": ComponentParameter(type="float", default=1500.0, description="Clarifier area (m²)"),
            "depth": ComponentParameter(type="float", default=4.0, description="Clarifier depth (m)")
        }
    ),
    ComponentDefinition(
        id="adm1_reactor",
        name="ADM1 Digester",
        type=ComponentType.ADM1_REACTOR,
        icon="anerobic-digester.svg",
        inputs=["influent"],
        outputs=["effluent", "biogas"],
        parameters={
            "volume": ComponentParameter(type="float", default=3400.0, description="Digester volume (m³)"),
            "temperature": ComponentParameter(type="float", default=35.0, description="Temperature (°C)")
        }
    ),
    ComponentDefinition(
        id="settler",
        name="Secondary Clarifier",
        type=ComponentType.SETTLER,
        icon="settler.svg",
        inputs=["influent"],
        outputs=["effluent", "underflow"],
        parameters={
            "area": ComponentParameter(type="float", default=6000.0, description="Clarifier area (m²)"),
            "depth": ComponentParameter(type="float", default=4.0, description="Clarifier depth (m)")
        }
    ),
    ComponentDefinition(
        id="thickener",
        name="Thickener",
        type=ComponentType.THICKENER,
        icon="thickener.svg",
        inputs=["influent"],
        outputs=["effluent", "underflow"],
        parameters={
            "area": ComponentParameter(type="float", default=250.0, description="Thickener area (m²)"),
            "depth": ComponentParameter(type="float", default=3.0, description="Thickener depth (m)")
        }
    ),
    ComponentDefinition(
        id="dewatering",
        name="Dewatering",
        type=ComponentType.DEWATERING,
        icon="dewatering.svg",
        inputs=["influent"],
        outputs=["effluent", "cake"],
        parameters={
            "efficiency": ComponentParameter(type="float", default=0.95, description="Dewatering efficiency")
        }
    ),
    ComponentDefinition(
        id="storage",
        name="Storage Tank",
        type=ComponentType.STORAGE,
        icon="wastewater-storage.svg",
        inputs=["influent"],
        outputs=["effluent"],
        parameters={
            "volume": ComponentParameter(type="float", default=2000.0, description="Storage volume (m³)")
        }
    ),
    ComponentDefinition(
        id="splitter",
        name="Splitter",
        type=ComponentType.SPLITTER,
        icon="splitter.svg",
        inputs=["influent"],
        outputs=["effluent1", "effluent2"],
        parameters={
            "split_ratio": ComponentParameter(type="float", default=0.5, description="Split ratio (0-1)")
        }
    ),
    ComponentDefinition(
        id="combiner",
        name="Combiner",
        type=ComponentType.COMBINER,
        icon="combiner.svg",
        inputs=["influent1", "influent2"],
        outputs=["effluent"],
        parameters={}
    ),
    ComponentDefinition(
        id="influent",
        name="Influent",
        type=ComponentType.INFLUENT,
        icon="wastewater-storage.svg",
        inputs=[],
        outputs=["effluent"],
        parameters={
            "flow_rate": ComponentParameter(type="float", default=18446.0, description="Flow rate (m³/d)"),
            "cod": ComponentParameter(type="float", default=381.0, description="COD concentration (mg/L)"),
            "bod": ComponentParameter(type="float", default=200.0, description="BOD concentration (mg/L)")
        }
    )
]

# Global storage for active simulations
active_simulations: Dict[str, dict] = {}
websocket_connections: List[WebSocket] = []

@app.get("/")
async def root():
    return {"message": "BSM2 Simulation API (Mock)", "version": "1.0.0-mock"}

@app.get("/api/components", response_model=List[ComponentDefinition])
async def get_components():
    """Get all available BSM2 components"""
    return mock_components

@app.post("/api/simulations")
async def create_simulation(config: SimulationConfig):
    """Create and start a new simulation"""
    simulation_id = str(uuid.uuid4())
    
    # Mock simulation data
    active_simulations[simulation_id] = {
        "config": config,
        "status": "running",
        "progress": 0,
        "created_at": "2024-01-01T00:00:00Z"
    }
    
    # Start mock simulation process
    asyncio.create_task(mock_simulation_progress(simulation_id))
    
    return {"simulation_id": simulation_id}

@app.get("/api/simulations/{simulation_id}/status")
async def get_simulation_status(simulation_id: str):
    """Get simulation status"""
    if simulation_id not in active_simulations:
        raise HTTPException(status_code=404, detail="Simulation not found")
    
    return active_simulations[simulation_id]

@app.get("/api/simulations/{simulation_id}/result")
async def get_simulation_result(simulation_id: str):
    """Get simulation results"""
    if simulation_id not in active_simulations:
        raise HTTPException(status_code=404, detail="Simulation not found")
    
    simulation = active_simulations[simulation_id]
    if simulation["status"] != "completed":
        raise HTTPException(status_code=400, detail="Simulation not completed")
    
    # Mock result data
    return {
        "simulation_id": simulation_id,
        "config": simulation["config"],
        "components": [
            {
                "component_id": "mock_component",
                "component_name": "Mock Component",
                "outputs": {
                    "effluent": [[1.0, 2.0, 3.0], [1.1, 2.1, 3.1]]
                },
                "time": [0, 1]
            }
        ],
        "metadata": {"total_time": 2.0}
    }

@app.post("/api/validate-influent")
async def validate_influent(file: UploadFile = File(...)):
    """Validate influent CSV file"""
    try:
        content = await file.read()
        text = content.decode('utf-8')
        lines = text.strip().split('\n')
        
        if not lines:
            return {"valid": False, "message": "File is empty"}
        
        first_line = lines[0]
        column_count = len(first_line.split(','))
        
        if column_count != 14:
            return {
                "valid": False, 
                "message": f"Invalid number of columns. Expected 14, got {column_count}"
            }
        
        return {
            "valid": True,
            "column_count": column_count,
            "row_count": len(lines)
        }
    except Exception as e:
        return {"valid": False, "message": f"Error reading file: {str(e)}"}

@app.get("/api/icons/{icon_name}")
async def get_icon(icon_name: str):
    """Serve component icons"""
    icon_path = Path(__file__).parent.parent.parent / "docs" / "assets" / "icons" / "bsm2python" / icon_name
    if icon_path.exists():
        return FileResponse(icon_path)
    else:
        # Return a placeholder SVG
        placeholder_svg = '''<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect x="3" y="3" width="18" height="18" rx="2" ry="2"/></svg>'''
        return Response(content=placeholder_svg, media_type="image/svg+xml")

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """WebSocket endpoint for real-time simulation updates"""
    await websocket.accept()
    websocket_connections.append(websocket)
    
    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        websocket_connections.remove(websocket)

async def mock_simulation_progress(simulation_id: str):
    """Mock simulation progress updates"""
    simulation = active_simulations[simulation_id]
    
    for progress in range(0, 101, 10):
        simulation["progress"] = progress
        
        # Send progress update via WebSocket
        message = {
            "simulation_id": simulation_id,
            "progress": progress,
            "current_time": progress / 100 * 7.0,  # 7 days simulation
            "status": "running",
            "message": f"Simulation progress: {progress}%"
        }
        
        # Send to all connected WebSocket clients
        for ws in websocket_connections:
            try:
                await ws.send_text(json.dumps(message))
            except:
                pass
        
        await asyncio.sleep(1)  # 1 second per 10% progress
    
    # Mark simulation as completed
    simulation["status"] = "completed"
    simulation["progress"] = 100
    
    # Send completion message
    completion_message = {
        "simulation_id": simulation_id,
        "progress": 100,
        "current_time": 7.0,
        "status": "completed",
        "message": "Simulation completed successfully"
    }
    
    for ws in websocket_connections:
        try:
            await ws.send_text(json.dumps(completion_message))
        except:
            pass

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)