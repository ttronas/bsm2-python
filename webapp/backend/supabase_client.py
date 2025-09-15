"""
Supabase client for storing simulation configurations and results
"""

import os
import json
from typing import Dict, List, Any, Optional
from datetime import datetime
from supabase import create_client, Client
from webapp.backend.models import SimulationConfig


class SupabaseClient:
    """Client for interacting with Supabase database"""
    
    def __init__(self):
        # Initialize Supabase client
        # In production, these should be environment variables
        supabase_url = os.getenv("SUPABASE_URL", "your_supabase_url_here")
        supabase_key = os.getenv("SUPABASE_ANON_KEY", "your_supabase_anon_key_here")
        
        if supabase_url == "your_supabase_url_here":
            print("Warning: Supabase not configured. Using mock client.")
            self.client = None
        else:
            self.client: Client = create_client(supabase_url, supabase_key)
    
    async def save_simulation_config(self, simulation_id: str, config: SimulationConfig):
        """Save simulation configuration to database"""
        if not self.client:
            print(f"Mock: Saving simulation config {simulation_id}")
            return
        
        try:
            data = {
                "simulation_id": simulation_id,
                "name": config.name,
                "config": config.dict(),
                "user_id": config.user_id,
                "created_at": datetime.utcnow().isoformat()
            }
            
            result = self.client.table("simulation_configs").insert(data).execute()
            return result
        
        except Exception as e:
            print(f"Error saving simulation config: {e}")
            return None
    
    async def save_simulation_results(self, simulation_id: str, results: Dict[str, Any]):
        """Save simulation results to database"""
        if not self.client:
            print(f"Mock: Saving simulation results {simulation_id}")
            return
        
        try:
            data = {
                "simulation_id": simulation_id,
                "results": results,
                "created_at": datetime.utcnow().isoformat()
            }
            
            result = self.client.table("simulation_results").insert(data).execute()
            return result
        
        except Exception as e:
            print(f"Error saving simulation results: {e}")
            return None
    
    async def get_simulation_results(self, simulation_id: str):
        """Get simulation results from database"""
        if not self.client:
            print(f"Mock: Getting simulation results {simulation_id}")
            return None
        
        try:
            result = self.client.table("simulation_results").select("*").eq("simulation_id", simulation_id).execute()
            
            if result.data:
                return result.data[0]["results"]
            return None
        
        except Exception as e:
            print(f"Error getting simulation results: {e}")
            return None
    
    async def get_saved_configurations(self, user_id: Optional[str] = None):
        """Get saved simulation configurations"""
        if not self.client:
            print("Mock: Getting saved configurations")
            return []
        
        try:
            query = self.client.table("simulation_configs").select("*")
            
            if user_id:
                query = query.eq("user_id", user_id)
            
            result = query.execute()
            return result.data
        
        except Exception as e:
            print(f"Error getting saved configurations: {e}")
            return []
    
    async def save_configuration(self, config: Dict[str, Any]):
        """Save a configuration"""
        if not self.client:
            print("Mock: Saving configuration")
            return "mock_config_id"
        
        try:
            data = {
                "name": config.get("name", "Untitled"),
                "config": config,
                "user_id": config.get("user_id"),
                "created_at": datetime.utcnow().isoformat()
            }
            
            result = self.client.table("saved_configurations").insert(data).execute()
            return result.data[0]["id"]
        
        except Exception as e:
            print(f"Error saving configuration: {e}")
            return None