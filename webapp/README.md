# BSM2 Simulator Web Application

A web-based simulation platform for wastewater treatment plant modeling using the BSM2 (Benchmark Simulation Model No. 2) framework.

## Overview

This application provides a visual interface for creating, configuring, and running dynamic simulations of wastewater treatment plants. It combines a React Flow-based frontend with a FastAPI Python backend that utilizes the existing BSM2-Python modules.

## Architecture

```
webapp/
├── frontend/           # Next.js + React Flow frontend
│   ├── src/
│   │   ├── app/        # Next.js app router
│   │   ├── components/ # React components
│   │   ├── lib/        # Utility functions and API client
│   │   └── types/      # TypeScript type definitions
│   ├── package.json
│   └── next.config.js
├── backend/            # FastAPI Python backend
│   ├── main.py         # Main FastAPI application
│   ├── models.py       # Pydantic data models
│   ├── simulation_engine.py  # Simulation execution logic
│   ├── supabase_client.py    # Database integration
│   └── requirements.txt
└── test_configs/       # Example simulation configurations
```

## Features

### Frontend Features
- **Visual Flowsheet Designer**: Drag-and-drop interface for creating wastewater treatment plant layouts
- **Component Library**: Pre-configured BSM2 components (reactors, clarifiers, digesters, etc.)
- **Four-Tab Sidebar**:
  - **Components**: Available components for drag-and-drop
  - **Details**: Configuration panel for selected components
  - **Simulation**: Settings for timestep, duration, and influent data
  - **Results**: Interactive charts and data visualization
- **Import/Export**: Save and load flowsheet configurations as JSON files
- **Real-time Simulation**: WebSocket-based progress updates during simulation runs

### Backend Features
- **Simulation Engine**: Implements Kahn's algorithm for execution order with loop handling
- **BSM2 Integration**: Direct integration with existing BSM2-Python modules
- **Dynamic Configuration**: Runtime creation of simulation workflows from frontend configurations
- **Data Persistence**: Supabase integration for storing configurations and results
- **RESTful API**: Clean API design for frontend-backend communication

### Supported Components
- **ASM1 Reactor**: Activated sludge modeling
- **ADM1 Reactor**: Anaerobic digestion modeling
- **Primary Clarifier**: Primary sedimentation
- **Secondary Clarifier (Settler)**: Secondary sedimentation with 1D settling model
- **Thickener**: Sludge thickening
- **Dewatering**: Sludge dewatering
- **Storage Tank**: Wastewater storage
- **Splitter/Combiner**: Flow distribution utilities
- **Influent**: Configurable influent source (constant or dynamic)

## Getting Started

### Prerequisites
- Node.js 18+ and npm
- Python 3.8+
- The BSM2-Python package (already installed in this repository)

### Frontend Setup
```bash
cd webapp/frontend
npm install
npm run dev
```

The frontend will be available at `http://localhost:3000`

### Backend Setup
```bash
cd webapp/backend
pip install -r requirements.txt
python main.py
```

The backend API will be available at `http://localhost:8000`

### Database Setup (Optional)
To enable data persistence, configure Supabase:

1. Create a Supabase project
2. Set environment variables:
   ```bash
   export SUPABASE_URL="your_supabase_url"
   export SUPABASE_ANON_KEY="your_supabase_anon_key"
   ```
3. Create the following tables in your Supabase database:
   - `simulation_configs`
   - `simulation_results`
   - `saved_configurations`

## Usage

1. **Design Flowsheet**: Drag components from the Components tab to the main canvas
2. **Connect Components**: Draw connections between component inputs and outputs
3. **Configure Components**: Select components to modify their parameters in the Details tab
4. **Set Simulation Parameters**: Use the Simulation tab to configure timestep, duration, and influent data
5. **Run Simulation**: Click "Run Simulation" to execute the model
6. **View Results**: Analyze results in the Results tab with interactive charts

## Example Configurations

Test configurations based on the original BSM2-Python test files are available in `webapp/test_configs/`:
- `asm1_test.json`: Simple ASM1 reactor test case
- Additional test cases can be created based on other files in the `tests/` directory

## API Documentation

The backend provides a comprehensive REST API. When running locally, visit `http://localhost:8000/docs` for interactive API documentation.

### Key Endpoints
- `GET /api/components`: Get available component definitions
- `POST /api/simulation/start`: Start a new simulation
- `WebSocket /api/simulation/ws/{simulation_id}`: Real-time simulation updates
- `GET /api/simulation/{simulation_id}/results`: Get simulation results
- `POST /api/configurations/save`: Save flowsheet configuration

## Technical Details

### Simulation Execution
The simulation engine uses Kahn's algorithm to determine the execution order of components:
1. Build dependency graph from component connections
2. Topologically sort components
3. Handle cycles by iterating through them only once per timestep
4. Execute components in order for each timestep
5. Stream progress updates to frontend via WebSocket

### Data Flow
1. Frontend sends simulation configuration to backend
2. Backend creates component instances and execution order
3. Simulation runs asynchronously with progress updates
4. Results are returned to frontend and optionally stored in database
5. Frontend displays results in interactive charts and tables

### Component Integration
Each BSM2 component is wrapped with a standardized interface:
- Consistent parameter handling
- Standardized input/output definitions
- Error handling and validation
- Time series data collection

## Development

### Adding New Components
1. Add component type to `ComponentType` enum in `types/index.ts`
2. Add component definition to backend `get_available_components()` function
3. Add component initialization logic to `SimulationEngine._create_component()`
4. Update frontend component library display

### Testing
Test configurations can be validated against original BSM2-Python test files to ensure accuracy of the simulation engine.

## Future Enhancements
- User authentication and project management
- Advanced result analysis and reporting
- Performance optimization for large-scale simulations
- Additional BSM2 component types
- Simulation template library
- Collaborative editing features