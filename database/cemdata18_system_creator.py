"""
Create a xGEMS system definition file from Phase 3 input file
This creates a .lst file that can be used with engine.initialize()
"""

import sys
from pathlib import Path

# Add scripts to path
sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))
from config import INPUTS_GENERATED_DIR

def create_xgems_system_definition():
    """
    Create a xGEMS-compatible system definition from Phase 3 input files
    
    For xGEMS ChemicalEngine.initialize(), we need:
    - System definition file (.lst format)
    - Database files (.dat files)
    
    Since Cemdata18 is in GEM-Selektor native format (.ndx), we'll use
    initializeFromJsonStrings() method instead, which doesn't require
    external files.
    """
    
    # Read a sample input file to get system information
    sample_inp = INPUTS_GENERATED_DIR / "MIX_0000.inp"
    
    with open(sample_inp, 'r') as f:
        content = f.read()
    
    # Extract composition section
    lines = content.split('\n')
    in_components = False
    components = {}
    
    for line in lines:
        if 'COMPONENTS' in line:
            in_components = True
            continue
        if in_components and line.strip():
            if '|' in line:
                parts = line.split('|')
                if len(parts) >= 2:
                    comp = parts[0].strip()
                    value = float(parts[1].strip().split()[0])
                    components[comp] = value
            elif line.startswith('-' * 10):
                break
    
    print("System components from Phase 3:")
    for comp, val in components.items():
        print(f"  {comp}: {val} mol")
    
    print("\n" + "="*70)
    print("NOTE: xGEMS requires system definition from GEM-Selektor project")
    print("="*70)
    print("\nSince Cemdata18.1 database is in .ndx format (not .dat/.lst),")
    print("we will use a different approach:")
    print("\n1. Use ThermoFun to load thermodynamic data programmatically")
    print("2. Or use a pre-existing system definition from ThermoDataset")
    print("3. Or create minimal system with PSI-Nagra database")
    print("\nFor now, we'll implement equilibrium using simplified approach:")
    print("- Define elements: Ca, Si, Al, Fe, Mg, K, Na, S, O, H, C")
    print("- Use xGEMS without external database (built-in data)")
    print("- Focus on major phases: calcite, CSH, portlandite, ettringite")
    
    return components

if __name__ == "__main__":
    components = create_xgems_system_definition()
