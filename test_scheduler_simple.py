#!/usr/bin/env python3
"""Simple test for the flowsheet scheduler without BSM dependencies."""

import sys
import os

# Import the scheduler directly
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src', 'bsm2_python'))
from flowsheet_scheduler import schedule_flowsheet, load_flowsheet

def main():
    # Test the scheduler on all JSON files
    configs = ['bsm1_simulation_config.json', 'bsm1_ol_double_simulation_config.json', 'bsm1_ol_2parallel_simulation_config.json']

    for config_file in configs:
        print(f'\n=== Testing scheduler on {config_file} ===')
        try:
            data = load_flowsheet(config_file)
            plan = schedule_flowsheet(data)
            
            print(f'Number of SCCs: {plan["num_components"]}')
            print(f'Number of stages: {len(plan["stages"])}')
            print(f'SCC execution order: {plan["comp_order"]}')
            
            for i, stage in enumerate(plan['stages']):
                stage_type = stage['type'] 
                nodes = stage['nodes']
                print(f'  Stage {i}: {stage_type} - nodes: {nodes}')
                if stage_type == 'loop':
                    print(f'    Tear edges: {stage.get("tear_edges", [])}')
                    print(f'    Internal order: {stage.get("internal_order", [])}')
                    
        except Exception as e:
            print(f'Error processing {config_file}: {e}')
            import traceback
            traceback.print_exc()

if __name__ == '__main__':
    main()