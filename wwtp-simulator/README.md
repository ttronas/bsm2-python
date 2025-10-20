# WWTP Simulator

A web application for wastewater treatment plant simulation using BSM2-Python library.

## Architecture

- **Frontend**: Next.js + React Flow + TypeScript
- **Backend**: FastAPI + BSM2-Python 
- **Database**: Supabase for user data and simulation results

## Features

- Interactive flowsheet with drag-and-drop BSM2 components
- Real-time simulation progress monitoring
- Save/load simulation configurations and results
- Component configuration interface
- Results visualization dashboard

## Components

Built on top of BSM2-Python components:
- ASM1 Reactor (Activated Sludge)
- ADM1 Reactor (Anaerobic Digester)
- Primary Clarifier
- Settler (Secondary Clarifier)
- Thickener
- Dewatering
- Storage Tank
- Flow Combiner
- Flow Splitter
- Plant Performance Monitor

## Development

### Frontend
```bash
cd frontend
npm install
npm run dev
```

### Backend
```bash
cd backend
pip install -r requirements.txt
uvicorn main:app --reload
```