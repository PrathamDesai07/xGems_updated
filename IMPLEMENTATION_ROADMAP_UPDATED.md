# Updated Implementation Roadmap Based on Client Specifications

## Document Purpose
This document maps out **all changes needed** to align our current implementation with the new client specifications from README (2).md. Each phase and file is analyzed with specific action items.

**Date Created**: December 31, 2025  
**Based On**: README (2).md - Technical Specifications and Clarifications for CemGEMS Modeling

---

## 🎯 HIGH-LEVEL CHANGES REQUIRED

### Critical Infrastructure Changes

| Component | Current Status | Required Status | Priority |
|-----------|---------------|-----------------|----------|
| **Software** | Simplified Python model | CemGEMS/GEM-Selektor | 🔴 CRITICAL |
| **Database** | Cemdata18.1 (reference) | Cemdata20 (active) | 🔴 CRITICAL |
| **Thermodynamics** | Empirical rules | Full Gibbs Energy Minimization | 🔴 CRITICAL |
| **Input Data** | XRF oxides only | Rietveld XRD phases | 🟡 HIGH |
| **Gel Phases** | C-S-H_1.0 only | N-A-S-H, C-(N)-A-S-H | 🟡 HIGH |
| **Process Model** | Carbonation only | Hydration + Carbonation | 🟡 HIGH |
| **CO₂ Method** | Fixed pCO2 levels | Incremental stepwise | 🟠 MEDIUM |

---

## 📋 PHASE-BY-PHASE IMPLEMENTATION PLAN

### **PHASE 0: Critical Prerequisites (NEW PHASE)**

#### 0.1 Software Installation & Configuration
**Status**: ⚠️ NOT STARTED - BLOCKING ALL OTHER WORK

**Files to Create**:
```
scripts/
├── install_cemgems.sh          # Installation script
├── test_cemgems.py             # CemGEMS connectivity test
└── cemgems_wrapper.py          # Python wrapper for CemGEMS calls
```

**Action Items**:
- [ ] **Install CemGEMS/GEM-Selektor**
  - Download from: https://gems.web.psi.ch/GEMS3/
  - Install command-line version (no GUI needed)
  - Verify installation: `gems --version` or equivalent
  - Document installation path and executable name

- [ ] **Obtain Cemdata20 Database**
  - Download Cemdata20 from official source
  - Current: We have Cemdata18.1_08-01-19/
  - Required: Cemdata20 (latest version)
  - Install to: `database/Cemdata20/`
  - Verify database loading in CemGEMS

- [ ] **Create CemGEMS Test Case**
  ```python
  # scripts/test_cemgems.py
  # Test: Simple C3S + H2O hydration
  # Verify: Can call CemGEMS, parse output
  # Expected: Portlandite + C-S-H formation
  ```

**Deliverables**:
- Working CemGEMS installation
- Cemdata20 database accessible
- Python-to-CemGEMS interface functional
- Test case runs successfully

**Estimated Time**: 2-3 days (including troubleshooting)

---

#### 0.2 Obtain Missing Input Data
**Status**: ⚠️ DATA GAP - NEED CLIENT INPUT

**Currently Available**:
- ✅ XRF bulk oxide compositions (coal gangue, cement, fly ash)
- ✅ Sodium silicate composition

**Missing Critical Data**:

**A. Cement Clinker Phases (Rietveld XRD)**
```
Required format:
-----------------
C₃S (Alite):      55.0 wt%
C₂S (Belite):     20.0 wt%
C₃A (Aluminate):   8.0 wt%
C₄AF (Ferrite):    10.0 wt%
Gypsum:            5.0 wt%
Other:             2.0 wt%
Total:           100.0 wt%
```

**Options if unavailable**:
1. Use standard OPC composition (typical values)
2. Estimate from XRF using Bogue calculation
3. Request from client

**B. Fly Ash Mineralogy (Rietveld XRD)**
```
Required format:
-----------------
Amorphous glass:  70.0 wt%
Quartz:           15.0 wt%
Mullite:          10.0 wt%
Magnetite:         3.0 wt%
Hematite:          2.0 wt%
Total:           100.0 wt%
```

**C. Coal Gangue Mineralogy (Rietveld XRD)**
```
Required format:
-----------------
Quartz:           40.0 wt%
Clay minerals:    35.0 wt%  (kaolinite, illite, etc.)
Amorphous:        15.0 wt%
Iron oxides:       5.0 wt%
Other:             5.0 wt%
Total:           100.0 wt%
```

**Action Items**:
- [ ] Contact client for Rietveld XRD data
- [ ] If unavailable, prepare standard compositions as fallback
- [ ] Create data input format specification
- [ ] Update `config.py` to handle phase-based inputs

**File Changes Required**:
```python
# scripts/config.py - ADD NEW SECTIONS

# Cement clinker phase composition (Rietveld XRD)
CEMENT_PHASES = {
    'C3S': 0.55,      # wt fraction
    'C2S': 0.20,
    'C3A': 0.08,
    'C4AF': 0.10,
    'Gypsum': 0.05,
    'Other': 0.02
}

# Fly ash mineralogy (Rietveld XRD)
FLYASH_PHASES = {
    'Glass': 0.70,
    'Quartz': 0.15,
    'Mullite': 0.10,
    'Magnetite': 0.03,
    'Hematite': 0.02
}

# Coal gangue mineralogy (Rietveld XRD)
GANGUE_PHASES = {
    'Quartz': 0.40,
    'Kaolinite': 0.25,
    'Illite': 0.10,
    'Amorphous': 0.15,
    'Iron_oxides': 0.05,
    'Other': 0.05
}
```

---

### **PHASE 1: Environment Setup** (NEEDS MAJOR UPDATE)

**Current Status**: ✅ Partially complete (Python environment only)  
**Required Status**: CemGEMS integration complete

#### 1.1 Update `scripts/config.py`
**Current**: Basic configuration with XRF data  
**Required**: Add CemGEMS paths, Cemdata20, phase data

**Changes Needed**:
```python
# ADD: CemGEMS configuration
CEMGEMS_EXECUTABLE = "/path/to/gems3k"  # or equivalent
CEMDATA20_PATH = "/path/to/Cemdata20/"
CEMGEMS_WORKING_DIR = "runs/cemgems_temp/"

# ADD: Thermodynamic database selection
DATABASE = "Cemdata20"
DATABASE_VERSION = "20.1"  # Update based on actual version

# ADD: Phase selection for CemGEMS
ENABLED_PHASES = {
    'cement': [
        'C3S', 'C2S', 'C3A', 'C4AF',  # Clinker phases
        'Gypsum', 'Anhydrite'          # Sulfate phases
    ],
    'hydration_products': [
        'Portlandite',                  # Ca(OH)2
        'CSHQ_TobH',                    # C-S-H model from Cemdata
        'Ettringite', 'Monosulfoaluminate',  # AFt, AFm
        'Hydrotalcite',                 # LDH
        'Hydrogarnet'                   # Siliceous hydrogarnet
    ],
    'alkali_activated': [
        'NASH_gel',                     # N-A-S-H gel
        'CNASH_gel'                     # C-(N)-A-S-H gel
    ],
    'carbonation': [
        'Calcite', 'Aragonite', 'Vaterite',  # CaCO3 polymorphs
        'Monocarboaluminate'            # Carbonated AFm
    ],
    'silica': [
        'SiO2am', 'Quartz'             # Amorphous and crystalline silica
    ]
}

# ADD: Simulation mode configuration
SIMULATION_MODE = 'coupled_hydration_carbonation'  # New requirement
REACTION_PATH_ENABLED = True  # Incremental CO2 addition

# ADD: Time-dependent parameters (for hydration-carbonation coupling)
HYDRATION_TIME_STEPS = [0.1, 1, 7, 28, 90, 180, 365]  # days
CARBONATION_TIME_STEPS = [0, 30, 60, 90, 180, 365]    # days
```

**Priority**: 🔴 CRITICAL  
**Estimated Time**: 4-6 hours

---

#### 1.2 Create `scripts/cemgems_wrapper.py` (NEW FILE)
**Purpose**: Python interface to CemGEMS

**Contents**:
```python
"""
CemGEMS Python Wrapper
Handles interaction with CemGEMS/GEM-Selektor command-line tools
"""

import subprocess
import json
import os
from pathlib import Path
from typing import Dict, List, Optional

class CemGEMSRunner:
    """Wrapper for CemGEMS command-line execution"""
    
    def __init__(self, executable_path: str, database_path: str):
        self.executable = executable_path
        self.database = database_path
        self.validate_installation()
    
    def validate_installation(self):
        """Check if CemGEMS is properly installed"""
        # Check executable exists
        # Check database accessible
        # Run simple test case
        pass
    
    def create_input_file(self, 
                          bulk_composition: Dict[str, float],
                          temperature: float,
                          pressure: float,
                          phases_to_include: List[str],
                          output_path: str) -> str:
        """
        Generate CemGEMS input file
        
        Args:
            bulk_composition: Dict of element: moles
            temperature: K
            pressure: bar
            phases_to_include: List of phase names from database
            output_path: Where to write input file
        
        Returns:
            Path to created input file
        """
        pass
    
    def run_equilibrium(self, 
                        input_file: str,
                        output_file: str,
                        timeout: int = 300) -> Dict:
        """
        Run single equilibrium calculation
        
        Returns:
            Dict with:
                - converged: bool
                - phases: Dict[phase_name, amount]
                - pH: float
                - pe: float
                - ionic_strength: float
        """
        pass
    
    def run_reaction_path(self,
                          initial_composition: Dict,
                          co2_steps: List[float],
                          output_dir: str) -> List[Dict]:
        """
        Run stepwise CO2 addition (reaction path)
        
        Args:
            initial_composition: Starting bulk composition
            co2_steps: List of CO2 amounts to add incrementally
            output_dir: Where to save step outputs
        
        Returns:
            List of equilibrium states at each step
        """
        pass
    
    def parse_output(self, output_file: str) -> Dict:
        """Parse CemGEMS output file into structured data"""
        pass
    
    def run_coupled_hydration_carbonation(self,
                                          clinker_phases: Dict,
                                          water_amount: float,
                                          co2_schedule: List[tuple],
                                          output_dir: str) -> Dict:
        """
        Run coupled hydration-carbonation simulation
        
        Args:
            clinker_phases: Initial clinker phase amounts
            water_amount: moles of water
            co2_schedule: List of (time, co2_amount) tuples
            output_dir: Where to save results
        
        Returns:
            Time-series data of phase evolution
        """
        pass
```

**Priority**: 🔴 CRITICAL  
**Estimated Time**: 2-3 days

---

#### 1.3 Update `scripts/test_environment.py`
**Current**: Tests Python packages only  
**Required**: Add CemGEMS connectivity tests

**Add to existing file**:
```python
def test_cemgems_installation():
    """Test if CemGEMS is properly installed"""
    print("Testing CemGEMS installation...")
    
    # Test 1: Executable exists
    from config import CEMGEMS_EXECUTABLE
    if not Path(CEMGEMS_EXECUTABLE).exists():
        print("❌ CemGEMS executable not found")
        return False
    print(f"✓ Found CemGEMS at: {CEMGEMS_EXECUTABLE}")
    
    # Test 2: Can run help command
    try:
        result = subprocess.run([CEMGEMS_EXECUTABLE, '--help'], 
                                capture_output=True, timeout=10)
        print("✓ CemGEMS executable responds")
    except Exception as e:
        print(f"❌ Cannot run CemGEMS: {e}")
        return False
    
    # Test 3: Database accessible
    from config import CEMDATA20_PATH
    if not Path(CEMDATA20_PATH).exists():
        print("❌ Cemdata20 database not found")
        return False
    print(f"✓ Found Cemdata20 at: {CEMDATA20_PATH}")
    
    # Test 4: Run simple test case
    print("✓ Running simple C3S hydration test...")
    wrapper = CemGEMSRunner(CEMGEMS_EXECUTABLE, CEMDATA20_PATH)
    test_result = wrapper.run_equilibrium(
        input_file="tests/c3s_hydration_test.inp",
        output_file="tests/c3s_hydration_test.out"
    )
    
    if test_result['converged']:
        print("✓ Test calculation converged")
        print(f"  Found phases: {list(test_result['phases'].keys())}")
        return True
    else:
        print("❌ Test calculation did not converge")
        return False

def test_phase_database():
    """Test that required phases are in Cemdata20"""
    print("\nTesting phase database availability...")
    
    from config import ENABLED_PHASES
    required_phases = []
    for category in ENABLED_PHASES.values():
        required_phases.extend(category)
    
    # Query database for each phase
    wrapper = CemGEMSRunner(config.CEMGEMS_EXECUTABLE, config.CEMDATA20_PATH)
    available_phases = wrapper.list_available_phases()
    
    missing = []
    for phase in required_phases:
        if phase in available_phases:
            print(f"✓ {phase}")
        else:
            print(f"❌ {phase} - NOT FOUND")
            missing.append(phase)
    
    if missing:
        print(f"\n⚠️ Missing {len(missing)} required phases")
        print("Options:")
        print("  1. Update phase names to match Cemdata20")
        print("  2. Request alternative phases")
        return False
    
    print(f"\n✓ All {len(required_phases)} required phases available")
    return True
```

**Priority**: 🔴 CRITICAL  
**Estimated Time**: 2-3 hours

---

### **PHASE 2: Mix Design & Chemistry Engine** (MAJOR UPDATE NEEDED)

**Current Status**: ✅ Basic XRF-based mass calculations  
**Required Status**: Phase-based input for CemGEMS

#### 2.1 Update `scripts/mix_design_generator.py`
**Current**: Generates masses from XRF  
**Required**: Convert to phase-based inputs

**Changes Needed**:
```python
# KEEP existing functions for mass calculations
# ADD new functions for phase-based initialization

def calculate_clinker_phase_masses(cement_mass: float, 
                                    clinker_phases: Dict[str, float]) -> Dict[str, float]:
    """
    Convert cement mass to individual clinker phase masses
    
    Args:
        cement_mass: Total cement mass (kg)
        clinker_phases: Dict of phase: weight_fraction
    
    Returns:
        Dict of phase_name: mass (kg)
    """
    phase_masses = {}
    for phase, fraction in clinker_phases.items():
        phase_masses[phase] = cement_mass * fraction
    
    return phase_masses

def calculate_flyash_phase_masses(flyash_mass: float,
                                   flyash_phases: Dict[str, float]) -> Dict[str, float]:
    """
    Convert fly ash mass to phase masses (glass, quartz, mullite, etc.)
    """
    phase_masses = {}
    for phase, fraction in flyash_phases.items():
        phase_masses[phase] = flyash_mass * fraction
    
    return phase_masses

def calculate_gangue_phase_masses(gangue_mass: float,
                                   gangue_phases: Dict[str, float]) -> Dict[str, float]:
    """
    Convert coal gangue mass to phase masses
    """
    phase_masses = {}
    for phase, fraction in gangue_phases.items():
        phase_masses[phase] = gangue_mass * fraction
    
    return phase_masses

def generate_mix_designs_with_phases():
    """
    UPDATED: Generate mix designs with phase-based composition
    
    Output format:
        Each row contains:
        - R, f_FA, yCO2, w_SS, w/b (variables)
        - Individual phase masses (C3S, C2S, glass, quartz, etc.)
        - Water mass, sodium silicate components
    """
    
    mix_designs = []
    
    for R in config.R_VALUES:
        for f_FA in config.F_FA_VALUES:
            for yCO2 in config.YCO2_VALUES:
                for w_SS in config.W_SS_VALUES:
                    for w_b in config.W_B_VALUES:
                        
                        # Calculate raw material masses (existing code)
                        masses = calculate_raw_material_masses(R, f_FA, w_SS, w_b)
                        
                        # NEW: Convert to phase masses
                        cement_phases = calculate_clinker_phase_masses(
                            masses['cement'], config.CEMENT_PHASES
                        )
                        
                        flyash_phases = calculate_flyash_phase_masses(
                            masses['flyash'], config.FLYASH_PHASES
                        )
                        
                        gangue_phases = calculate_gangue_phase_masses(
                            masses['gangue'], config.GANGUE_PHASES
                        )
                        
                        # Combine into single dict
                        mix_design = {
                            'R': R,
                            'f_FA': f_FA,
                            'yCO2': yCO2,
                            'w_SS': w_SS,
                            'w_b': w_b,
                            **cement_phases,      # C3S, C2S, C3A, C4AF, etc.
                            **flyash_phases,      # Glass, Quartz, Mullite, etc.
                            **gangue_phases,      # Quartz, Clays, etc.
                            'water': masses['water'],
                            'sodium_silicate': masses['sodium_silicate']
                        }
                        
                        mix_designs.append(mix_design)
    
    return pd.DataFrame(mix_designs)
```

**Priority**: 🟡 HIGH  
**Estimated Time**: 6-8 hours

---

#### 2.2 Update `scripts/oxide_calculator.py`
**Current**: XRF to bulk oxides  
**Required**: Phase-based to element moles for CemGEMS

**Changes Needed**:
```python
# ADD: Phase stoichiometry database
PHASE_STOICHIOMETRY = {
    # Cement clinker phases
    'C3S': {'Ca': 3, 'Si': 1, 'O': 5},           # 3CaO·SiO2
    'C2S': {'Ca': 2, 'Si': 1, 'O': 4},           # 2CaO·SiO2
    'C3A': {'Ca': 3, 'Al': 2, 'O': 6},           # 3CaO·Al2O3
    'C4AF': {'Ca': 4, 'Al': 2, 'Fe': 2, 'O': 10}, # 4CaO·Al2O3·Fe2O3
    'Gypsum': {'Ca': 1, 'S': 1, 'O': 6, 'H': 4}, # CaSO4·2H2O
    
    # Fly ash phases
    'Quartz': {'Si': 1, 'O': 2},                 # SiO2
    'Mullite': {'Al': 6, 'Si': 2, 'O': 13},      # 3Al2O3·2SiO2
    'Magnetite': {'Fe': 3, 'O': 4},              # Fe3O4
    'Hematite': {'Fe': 2, 'O': 3},               # Fe2O3
    
    # For glass, use XRF composition
    
    # Coal gangue phases
    'Kaolinite': {'Al': 2, 'Si': 2, 'O': 9, 'H': 4},  # Al2Si2O5(OH)4
    'Illite': {'K': 1, 'Al': 4, 'Si': 7, 'O': 24, 'H': 8},  # Approx.
    
    # Add more as needed
}

def phase_mass_to_element_moles(phase_name: str, 
                                 phase_mass: float) -> Dict[str, float]:
    """
    Convert phase mass to elemental moles
    
    Args:
        phase_name: Name of phase (must be in PHASE_STOICHIOMETRY)
        phase_mass: Mass of phase (kg)
    
    Returns:
        Dict of element: moles
    """
    if phase_name not in PHASE_STOICHIOMETRY:
        raise ValueError(f"Unknown phase: {phase_name}")
    
    stoich = PHASE_STOICHIOMETRY[phase_name]
    
    # Calculate phase molar mass
    molar_mass = sum(
        config.ELEMENT_MASSES[elem] * count 
        for elem, count in stoich.items()
    )
    
    # Convert mass to moles of phase
    phase_moles = (phase_mass * 1000) / molar_mass  # kg to g
    
    # Convert to element moles
    element_moles = {}
    for elem, count in stoich.items():
        element_moles[elem] = phase_moles * count
    
    return element_moles

def mix_design_to_bulk_composition(mix_design_row: Dict) -> Dict[str, float]:
    """
    Convert full mix design with phases to bulk elemental composition
    
    Args:
        mix_design_row: Row from mix_designs DataFrame with all phase masses
    
    Returns:
        Dict of element: total_moles (for CemGEMS input)
    """
    
    bulk_composition = {}
    
    # Process each phase in the mix
    phase_columns = [col for col in mix_design_row.keys() 
                     if col not in ['R', 'f_FA', 'yCO2', 'w_SS', 'w_b']]
    
    for phase_col in phase_columns:
        phase_mass = mix_design_row[phase_col]
        
        if phase_mass > 0:
            if phase_col == 'Glass':
                # Special handling for amorphous glass (use XRF)
                elem_moles = glass_xrf_to_elements(phase_mass, 'flyash')
            else:
                # Use stoichiometry
                elem_moles = phase_mass_to_element_moles(phase_col, phase_mass)
            
            # Add to bulk
            for elem, moles in elem_moles.items():
                bulk_composition[elem] = bulk_composition.get(elem, 0) + moles
    
    return bulk_composition
```

**Priority**: 🟡 HIGH  
**Estimated Time**: 6-8 hours

---

### **PHASE 3: CemGEMS Input Generation** (COMPLETE REWRITE)

**Current Status**: ❌ Does not exist (we used simplified model)  
**Required Status**: Generate proper CemGEMS input files

#### 3.1 Create `scripts/cemgems_input_writer.py` (NEW FILE)
**Purpose**: Generate CemGEMS/GEMS input files

**Contents**:
```python
"""
CemGEMS Input File Generator
Creates input files for CemGEMS equilibrium calculations
"""

import json
from pathlib import Path
from typing import Dict, List
import config

class CemGEMSInputWriter:
    """Generate CemGEMS input files from mix design data"""
    
    def __init__(self, database_path: str, output_dir: str):
        self.database = database_path
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
    
    def write_equilibrium_input(self,
                                 mix_id: str,
                                 bulk_composition: Dict[str, float],
                                 temperature: float,
                                 pressure: float,
                                 pCO2: float,
                                 phases_to_include: List[str]) -> str:
        """
        Write single equilibrium calculation input
        
        Format depends on CemGEMS/GEMS input specification
        May be JSON, XML, or custom text format
        """
        
        input_file = self.output_dir / f"{mix_id}.inp"
        
        # Example structure (adjust to actual CemGEMS format)
        input_data = {
            "problem_name": mix_id,
            "database": self.database,
            "temperature": temperature,  # K
            "pressure": pressure,        # bar
            "bulk_composition": bulk_composition,  # element: moles
            "phases": {
                "include": phases_to_include,
                "suppress": []
            },
            "gas_phase": {
                "CO2": pCO2,
                "H2O": pressure - pCO2  # Assuming CO2 + H2O gas
            },
            "solver_options": {
                "max_iterations": 500,
                "tolerance": 1e-6,
                "gibbs_method": "IPM"  # Interior Point Method
            }
        }
        
        with open(input_file, 'w') as f:
            json.dump(input_data, f, indent=2)
        
        return str(input_file)
    
    def write_reaction_path_input(self,
                                   mix_id: str,
                                   initial_composition: Dict[str, float],
                                   co2_steps: List[float],
                                   temperature: float,
                                   pressure: float) -> str:
        """
        Write reaction-path input for stepwise CO2 addition
        
        Args:
            mix_id: Unique identifier
            initial_composition: Starting bulk composition
            co2_steps: List of CO2 amounts to add at each step (moles)
            temperature: K
            pressure: bar
        
        Returns:
            Path to input file
        """
        
        input_file = self.output_dir / f"{mix_id}_rxpath.inp"
        
        input_data = {
            "problem_name": f"{mix_id}_reaction_path",
            "database": self.database,
            "mode": "reaction_path",
            "initial_conditions": {
                "temperature": temperature,
                "pressure": pressure,
                "bulk_composition": initial_composition
            },
            "reaction_steps": [
                {
                    "step": i,
                    "add_component": "CO2",
                    "amount": co2_amount,
                    "unit": "moles"
                }
                for i, co2_amount in enumerate(co2_steps)
            ],
            "phases": {
                "include": config.ENABLED_PHASES
            }
        }
        
        with open(input_file, 'w') as f:
            json.dump(input_data, f, indent=2)
        
        return str(input_file)
    
    def write_coupled_hydration_carbonation_input(self,
                                                   mix_id: str,
                                                   clinker_phases: Dict[str, float],
                                                   water_amount: float,
                                                   co2_schedule: List[tuple],
                                                   temperature: float,
                                                   pressure: float) -> str:
        """
        Write input for coupled hydration-carbonation simulation
        
        Args:
            mix_id: Unique identifier
            clinker_phases: Dict of phase: initial_amount (moles)
            water_amount: moles of water
            co2_schedule: List of (time_days, co2_partial_pressure) tuples
            temperature: K
            pressure: bar
        
        Returns:
            Path to input file
        """
        
        input_file = self.output_dir / f"{mix_id}_coupled.inp"
        
        input_data = {
            "problem_name": f"{mix_id}_hydration_carbonation",
            "database": self.database,
            "mode": "time_dependent_equilibrium",
            "initial_phases": clinker_phases,
            "initial_aqueous": {
                "H2O": water_amount
            },
            "time_schedule": [
                {
                    "time": time,
                    "unit": "days",
                    "temperature": temperature,
                    "pressure": pressure,
                    "pCO2": pco2
                }
                for time, pco2 in co2_schedule
            ],
            "phases": {
                "include": [
                    *config.ENABLED_PHASES['cement'],
                    *config.ENABLED_PHASES['hydration_products'],
                    *config.ENABLED_PHASES['alkali_activated'],
                    *config.ENABLED_PHASES['carbonation']
                ]
            }
        }
        
        with open(input_file, 'w') as f:
            json.dump(input_data, f, indent=2)
        
        return str(input_file)

def generate_all_inputs():
    """
    Generate all 4,928 input files
    """
    
    # Load mix designs
    mix_designs = pd.read_csv('outputs/tables/mix_designs_with_phases.csv')
    
    writer = CemGEMSInputWriter(
        database_path=config.CEMDATA20_PATH,
        output_dir='inputs/generated/'
    )
    
    for idx, row in mix_designs.iterrows():
        
        mix_id = f"mix_{idx:04d}"
        
        # Convert to bulk composition
        bulk_comp = oxide_calculator.mix_design_to_bulk_composition(row)
        
        # Calculate pCO2
        pCO2 = row['yCO2'] * config.PRESSURE  # bar
        
        # Write input file
        input_file = writer.write_equilibrium_input(
            mix_id=mix_id,
            bulk_composition=bulk_comp,
            temperature=config.TEMPERATURE,
            pressure=config.PRESSURE,
            pCO2=pCO2,
            phases_to_include=config.ENABLED_PHASES
        )
        
        print(f"Created: {input_file}")
    
    print(f"\nTotal: {len(mix_designs)} input files generated")
```

**Priority**: 🔴 CRITICAL  
**Estimated Time**: 2-3 days

---

### **PHASE 4: Batch Execution** (NEW - REPLACES SIMPLIFIED MODEL)

**Current Status**: ❌ Used Python calculations  
**Required Status**: Call CemGEMS for each case

#### 4.1 Create `scripts/cemgems_batch_controller.py` (NEW FILE)

**Contents**:
```python
"""
Batch CemGEMS Execution Controller
Runs 4,928 equilibrium calculations using CemGEMS
"""

import subprocess
import multiprocessing as mp
from pathlib import Path
from typing import List, Dict
import pandas as pd
from tqdm import tqdm
import config
from cemgems_wrapper import CemGEMSRunner

class BatchController:
    """Control batch execution of CemGEMS calculations"""
    
    def __init__(self, input_dir: str, output_dir: str, n_workers: int = 4):
        self.input_dir = Path(input_dir)
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.n_workers = n_workers
        
        self.runner = CemGEMSRunner(
            executable_path=config.CEMGEMS_EXECUTABLE,
            database_path=config.CEMDATA20_PATH
        )
    
    def run_single_case(self, input_file: str) -> Dict:
        """
        Run single CemGEMS calculation
        
        Returns:
            Dict with results and status
        """
        
        mix_id = Path(input_file).stem
        output_file = self.output_dir / f"{mix_id}.out"
        
        try:
            result = self.runner.run_equilibrium(
                input_file=str(input_file),
                output_file=str(output_file),
                timeout=300  # 5 minutes per case
            )
            
            result['mix_id'] = mix_id
            result['status'] = 'success'
            return result
            
        except subprocess.TimeoutExpired:
            return {
                'mix_id': mix_id,
                'status': 'timeout',
                'error': 'Calculation exceeded 5 minutes'
            }
        except Exception as e:
            return {
                'mix_id': mix_id,
                'status': 'error',
                'error': str(e)
            }
    
    def run_all_sequential(self) -> pd.DataFrame:
        """Run all calculations sequentially (safe but slow)"""
        
        input_files = list(self.input_dir.glob("*.inp"))
        results = []
        
        print(f"Running {len(input_files)} calculations sequentially...")
        
        for input_file in tqdm(input_files):
            result = self.run_single_case(input_file)
            results.append(result)
        
        return pd.DataFrame(results)
    
    def run_all_parallel(self) -> pd.DataFrame:
        """Run calculations in parallel (faster but uses more resources)"""
        
        input_files = list(self.input_dir.glob("*.inp"))
        
        print(f"Running {len(input_files)} calculations using {self.n_workers} workers...")
        
        with mp.Pool(processes=self.n_workers) as pool:
            results = list(tqdm(
                pool.imap(self.run_single_case, input_files),
                total=len(input_files)
            ))
        
        return pd.DataFrame(results)
    
    def analyze_convergence(self, results_df: pd.DataFrame):
        """Analyze convergence statistics"""
        
        total = len(results_df)
        success = len(results_df[results_df['status'] == 'success'])
        timeout = len(results_df[results_df['status'] == 'timeout'])
        error = len(results_df[results_df['status'] == 'error'])
        
        print("\n" + "="*60)
        print("CONVERGENCE ANALYSIS")
        print("="*60)
        print(f"Total cases:      {total}")
        print(f"Successful:       {success} ({success/total*100:.1f}%)")
        print(f"Timeouts:         {timeout} ({timeout/total*100:.1f}%)")
        print(f"Errors:           {error} ({error/total*100:.1f}%)")
        print("="*60)
        
        if error > 0:
            print("\nError summary:")
            error_cases = results_df[results_df['status'] == 'error']
            print(error_cases[['mix_id', 'error']])

if __name__ == '__main__':
    
    controller = BatchController(
        input_dir='inputs/generated/',
        output_dir='runs/equilibrium/',
        n_workers=4  # Adjust based on available cores
    )
    
    # Run calculations
    results = controller.run_all_parallel()
    
    # Save results summary
    results.to_csv('outputs/tables/batch_execution_summary.csv', index=False)
    
    # Analyze convergence
    controller.analyze_convergence(results)
```

**Priority**: 🔴 CRITICAL  
**Estimated Time**: 1-2 days  
**Note**: Execution time for 4,928 cases depends on hardware (estimate 10-50 hours total)

---

### **PHASE 5: Output Parsing** (MAJOR UPDATE)

**Current Status**: ❌ Parsed simplified model output  
**Required Status**: Parse CemGEMS output format

#### 5.1 Create `scripts/cemgems_output_parser.py` (NEW FILE)

**Contents**:
```python
"""
CemGEMS Output Parser
Extract structured data from CemGEMS output files
"""

import re
import json
from pathlib import Path
from typing import Dict, List
import pandas as pd

class CemGEMSOutputParser:
    """Parse CemGEMS output files"""
    
    def __init__(self):
        # Will depend on actual CemGEMS output format
        self.phase_pattern = re.compile(r'Phase:\s+(\w+)\s+Amount:\s+([\d.e+-]+)')
        self.element_pattern = re.compile(r'Element:\s+(\w+)\s+Moles:\s+([\d.e+-]+)')
    
    def parse_output_file(self, output_file: str) -> Dict:
        """
        Parse single CemGEMS output file
        
        Returns:
            Dict with:
                - converged: bool
                - phases: Dict[phase_name: amount_mol]
                - elements: Dict[element: moles]
                - pH: float
                - pe: float (redox potential)
                - ionic_strength: float
                - aqueous_species: Dict[species: molality]
                - gas_phase: Dict[gas: partial_pressure]
        """
        
        result = {
            'converged': False,
            'phases': {},
            'elements': {},
            'pH': None,
            'pe': None,
            'ionic_strength': None,
            'aqueous_species': {},
            'gas_phase': {}
        }
        
        with open(output_file, 'r') as f:
            content = f.read()
        
        # Check convergence (format depends on CemGEMS)
        if 'CONVERGED' in content or 'Gibbs energy minimized' in content:
            result['converged'] = True
        
        # Parse phases
        for match in self.phase_pattern.finditer(content):
            phase_name = match.group(1)
            amount = float(match.group(2))
            result['phases'][phase_name] = amount
        
        # Parse pH
        ph_match = re.search(r'pH:\s+([\d.]+)', content)
        if ph_match:
            result['pH'] = float(ph_match.group(1))
        
        # Parse ionic strength
        is_match = re.search(r'Ionic strength:\s+([\d.e+-]+)', content)
        if is_match:
            result['ionic_strength'] = float(is_match.group(1))
        
        # Add more parsing as needed for specific output format
        
        return result
    
    def parse_reaction_path_output(self, output_file: str) -> List[Dict]:
        """
        Parse reaction-path output with multiple steps
        
        Returns:
            List of equilibrium states at each CO2 addition step
        """
        
        # Implementation depends on CemGEMS reaction-path output format
        pass
    
    def extract_key_phases(self, phases_dict: Dict[str, float]) -> Dict[str, float]:
        """
        Extract and classify key phases of interest
        
        Args:
            phases_dict: All phases from CemGEMS
        
        Returns:
            Dict with standardized phase categories
        """
        
        key_phases = {
            # C-S-H phases (may have multiple types in Cemdata20)
            'CSH_total': 0.0,
            'Calcite': 0.0,
            'Aragonite': 0.0,
            'Vaterite': 0.0,
            'Portlandite': 0.0,
            'Ettringite': 0.0,
            'Monosulfoaluminate': 0.0,
            'Hydrotalcite': 0.0,
            'Silica_gel': 0.0,
            'NASH_gel': 0.0,
            'CNASH_gel': 0.0
        }
        
        for phase_name, amount in phases_dict.items():
            
            # Map CemGEMS phase names to standardized names
            if 'CSH' in phase_name or 'Tobermorite' in phase_name:
                key_phases['CSH_total'] += amount
            elif phase_name == 'Calcite':
                key_phases['Calcite'] = amount
            elif phase_name == 'Aragonite':
                key_phases['Aragonite'] = amount
            elif phase_name == 'Portlandite' or 'CH' in phase_name:
                key_phases['Portlandite'] = amount
            elif 'Ettringite' in phase_name or 'AFt' in phase_name:
                key_phases['Ettringite'] = amount
            elif 'Monosulfo' in phase_name or phase_name == 'AFm':
                key_phases['Monosulfoaluminate'] = amount
            elif 'Hydrotalcite' in phase_name or 'LDH' in phase_name:
                key_phases['Hydrotalcite'] = amount
            elif 'SiO2' in phase_name and 'am' in phase_name:
                key_phases['Silica_gel'] = amount
            elif 'NASH' in phase_name:
                key_phases['NASH_gel'] = amount
            elif 'CNASH' in phase_name:
                key_phases['CNASH_gel'] = amount
        
        return key_phases

def parse_all_outputs():
    """
    Parse all output files and create master dataset
    """
    
    parser = CemGEMSOutputParser()
    output_dir = Path('runs/equilibrium/')
    
    all_results = []
    
    print("Parsing output files...")
    for output_file in output_dir.glob("*.out"):
        
        mix_id = output_file.stem
        
        try:
            result = parser.parse_output_file(str(output_file))
            
            # Extract key phases
            key_phases = parser.extract_key_phases(result['phases'])
            
            # Combine into single record
            record = {
                'mix_id': mix_id,
                'converged': result['converged'],
                'pH': result['pH'],
                **key_phases,  # Add all key phase amounts
                'total_phases': len(result['phases'])
            }
            
            all_results.append(record)
            
        except Exception as e:
            print(f"Error parsing {mix_id}: {e}")
            continue
    
    # Create DataFrame
    df = pd.DataFrame(all_results)
    
    # Merge with original mix design variables
    mix_designs = pd.read_csv('outputs/tables/mix_designs_full_factorial.csv')
    df = df.merge(mix_designs, on='mix_id')
    
    # Save master dataset
    df.to_csv('outputs/tables/master_dataset_cemgems.csv', index=False)
    
    print(f"\nParsed {len(df)} output files")
    print(f"Convergence rate: {df['converged'].sum() / len(df) * 100:.1f}%")
    
    return df
```

**Priority**: 🔴 CRITICAL  
**Estimated Time**: 2-3 days

---

### **PHASE 6-9: Visualization** (MINOR UPDATES)

**Current Status**: ✅ Visualization code mostly OK  
**Required Status**: Update data source from simplified to CemGEMS results

**Files to Update**:
- `scripts/phase_map_plotter.py` - Update to use CemGEMS phase names
- `scripts/ternary_diagram_plotter.py` - No changes needed
- `scripts/trend_plotter.py` - Update phase names
- `scripts/reaction_path_plotter.py` - Update to handle CemGEMS reaction-path output

**Changes Needed**:
```python
# In each plotting script, update phase name mappings

# OLD (simplified model):
PHASE_NAMES = ['C-S-H_1.0', 'Calcite', 'Ettringite', 'Hydrotalcite', 'Silica_gel']

# NEW (CemGEMS/Cemdata20):
PHASE_NAMES = {
    'CSH_total': 'C-S-H',
    'Calcite': 'Calcite',
    'Ettringite': 'Ettringite',
    'Monosulfoaluminate': 'AFm',
    'Hydrotalcite': 'Hydrotalcite',
    'Silica_gel': 'Silica gel',
    'NASH_gel': 'N-A-S-H',     # NEW
    'CNASH_gel': 'C-(N)-A-S-H'  # NEW
}

# Update data loading:
# OLD:
df = pd.read_csv('outputs/tables/master_dataset_classified.csv')

# NEW:
df = pd.read_csv('outputs/tables/master_dataset_cemgems.csv')
```

**Priority**: 🟠 MEDIUM  
**Estimated Time**: 4-6 hours total

---

### **PHASE 10: Reaction-Path Simulations** (MAJOR UPDATE)

**Current Status**: ⚠️ Used discrete CO2 levels  
**Required Status**: True incremental stepwise addition

#### 10.1 Update `scripts/reaction_path_plotter.py`

**Changes Needed**:
```python
def run_reaction_path_cemgems(mix_design: Dict, 
                               n_co2_steps: int = 20) -> pd.DataFrame:
    """
    Run true reaction-path simulation with incremental CO2 addition
    
    Args:
        mix_design: Single mix design with phase masses
        n_co2_steps: Number of CO2 addition steps
    
    Returns:
        DataFrame with phase evolution at each step
    """
    
    # Calculate initial bulk composition
    bulk_comp = oxide_calculator.mix_design_to_bulk_composition(mix_design)
    
    # Calculate total CO2 to add
    final_yCO2 = mix_design['yCO2']
    total_co2_to_add = calculate_total_co2_moles(bulk_comp, final_yCO2)
    
    # Create CO2 addition schedule
    co2_increments = [total_co2_to_add / n_co2_steps] * n_co2_steps
    
    # Write reaction-path input
    writer = CemGEMSInputWriter(config.CEMDATA20_PATH, 'inputs/reaction_paths/')
    input_file = writer.write_reaction_path_input(
        mix_id=f"rxpath_{mix_design['mix_id']}",
        initial_composition=bulk_comp,
        co2_steps=co2_increments,
        temperature=config.TEMPERATURE,
        pressure=config.PRESSURE
    )
    
    # Run CemGEMS
    runner = CemGEMSRunner(config.CEMGEMS_EXECUTABLE, config.CEMDATA20_PATH)
    results = runner.run_reaction_path(
        input_file=input_file,
        output_dir='runs/reaction_paths/'
    )
    
    # Parse results
    df_steps = []
    for step, result in enumerate(results):
        record = {
            'step': step,
            'CO2_added': sum(co2_increments[:step+1]),
            'pH': result['pH'],
            **result['phases']
        }
        df_steps.append(record)
    
    return pd.DataFrame(df_steps)
```

**Priority**: 🟡 HIGH  
**Estimated Time**: 8-10 hours

---

### **PHASE 11: Validation** (UPDATE FOR CEMGEMS)

**Current Status**: ✅ Validation logic OK  
**Required Status**: Update to check CemGEMS-specific issues

#### 11.1 Update `scripts/validation.py`

**Add new validation checks**:
```python
def check_phase_compatibility():
    """
    Check if phase assemblages are thermodynamically compatible
    
    CemGEMS should prevent incompatible phases, but verify
    """
    
    df = pd.read_csv('outputs/tables/master_dataset_cemgems.csv')
    
    incompatible_pairs = [
        ('Portlandite', 'high_CO2'),  # CH shouldn't exist at high pCO2
        ('C3S', 'any'),               # C3S should hydrate completely
        ('C2S', 'any')                # C2S should hydrate completely
    ]
    
    issues = []
    for idx, row in df.iterrows():
        if row['Portlandite'] > 0.001 and row['yCO2'] > 0.25:
            issues.append(f"Mix {row['mix_id']}: Portlandite at high CO2")
    
    return issues

def check_alkali_activation():
    """
    Verify N-A-S-H and C-(N)-A-S-H formation in high sodium silicate cases
    """
    
    df = pd.read_csv('outputs/tables/master_dataset_cemgems.csv')
    
    # High sodium silicate cases should show N-A-S-H
    high_ss = df[df['w_SS'] >= 0.04]
    
    nash_formation_rate = (high_ss['NASH_gel'] > 0.001).sum() / len(high_ss)
    
    print(f"N-A-S-H formation rate in high Na₂SiO₃ cases: {nash_formation_rate*100:.1f}%")
    
    if nash_formation_rate < 0.5:
        print("⚠️ Warning: N-A-S-H formation lower than expected")

def check_cemgems_convergence():
    """
    Analyze CemGEMS convergence patterns
    """
    
    df = pd.read_csv('outputs/tables/master_dataset_cemgems.csv')
    
    convergence_by_var = {}
    
    for var in ['R', 'f_FA', 'yCO2', 'w_SS', 'w_b']:
        conv_rates = df.groupby(var)['converged'].mean()
        convergence_by_var[var] = conv_rates
        
        print(f"\nConvergence by {var}:")
        print(conv_rates)
    
    return convergence_by_var
```

**Priority**: 🟠 MEDIUM  
**Estimated Time**: 4-6 hours

---

### **PHASE 12-13: Documentation** (MAJOR UPDATE)

**Required Updates**:

1. **Update `report/FINAL_TECHNICAL_REPORT.md`**:
   - Replace "Simplified thermodynamic model" with "CemGEMS/Gibbs Energy Minimization"
   - Add Cemdata20 database documentation
   - Document Rietveld XRD phase inputs
   - Add N-A-S-H and C-(N)-A-S-H gel descriptions
   - Document coupled hydration-carbonation approach
   - Update assumptions section

2. **Update `report/METHODOLOGY_DETAILED.md`**:
   - Replace empirical rules with GEM methodology
   - Add CemGEMS algorithm description
   - Document phase selection criteria
   - Add reaction-path methodology
   - Document time-dependent coupling approach

3. **Create `CEMGEMS_SETUP_GUIDE.md`** (NEW):
   - Installation instructions
   - Database configuration
   - Input file format specification
   - Output file parsing guide
   - Troubleshooting common issues

**Priority**: 🟡 HIGH  
**Estimated Time**: 2-3 days

---

## 📊 SUMMARY: EFFORT ESTIMATION

### Critical Path (Must Complete)

| Phase | Task | Estimated Time | Priority |
|-------|------|----------------|----------|
| 0.1 | Install CemGEMS + Cemdata20 | 2-3 days | 🔴 CRITICAL |
| 0.2 | Obtain Rietveld XRD data | 1-2 days | 🟡 HIGH |
| 1 | Update config.py | 4-6 hours | 🔴 CRITICAL |
| 1 | Create cemgems_wrapper.py | 2-3 days | 🔴 CRITICAL |
| 2 | Update mix design for phases | 6-8 hours | 🟡 HIGH |
| 2 | Update oxide calculator | 6-8 hours | 🟡 HIGH |
| 3 | Create cemgems_input_writer.py | 2-3 days | 🔴 CRITICAL |
| 4 | Create batch controller | 1-2 days | 🔴 CRITICAL |
| 4 | **RUN 4,928 calculations** | **10-50 hours** | 🔴 CRITICAL |
| 5 | Create output parser | 2-3 days | 🔴 CRITICAL |
| 6-9 | Update visualization | 4-6 hours | 🟠 MEDIUM |
| 10 | Update reaction paths | 8-10 hours | 🟡 HIGH |
| 11 | Update validation | 4-6 hours | 🟠 MEDIUM |
| 12-13 | Update documentation | 2-3 days | 🟡 HIGH |

**Total Development Time**: ~20-30 days  
**Plus Computation Time**: 10-50 hours (depending on hardware)

---

## ⚠️ CRITICAL DEPENDENCIES

### Must Have Before Starting:
1. ✅ CemGEMS/GEM-Selektor installed and working
2. ✅ Cemdata20 database accessible
3. ⚠️ Rietveld XRD data OR standard compositions approved

### Can Proceed Without (use fallbacks):
- Rietveld XRD → Use Bogue calculation + standard compositions
- Coupled hydration-carbonation → Start with equilibrium snapshots

---

## 🎯 RECOMMENDED IMPLEMENTATION STRATEGY

### Option A: Full Implementation (Client's Ideal)
**Timeline**: 4-6 weeks  
**Approach**: Implement everything as specified  
**Risk**: High - many unknowns (CemGEMS setup, XRD data availability)

### Option B: Phased Approach (Recommended)
**Phase 1 (Week 1-2)**:
- Install CemGEMS
- Get basic equilibrium calculations working
- Use XRF + standard phases initially

**Phase 2 (Week 3-4)**:
- Implement full 4,928 batch runs
- Create visualizations with CemGEMS data
- Validate against simplified model for sanity check

**Phase 3 (Week 5-6)**:
- Add Rietveld XRD inputs (if available)
- Implement reaction-path simulations
- Add coupled hydration-carbonation (if feasible)
- Complete documentation

### Option C: Hybrid Approach
- Use CemGEMS for critical cases (validation)
- Keep simplified model for rapid screening
- Document differences and limitations

---

## 📝 DELIVERABLES CHECKLIST

### Software Components
- [ ] CemGEMS installation verified
- [ ] Cemdata20 database configured
- [ ] Python-CemGEMS wrapper functional
- [ ] Input file generator complete
- [ ] Batch execution controller working
- [ ] Output parser validated

### Data Files
- [ ] 4,928 CemGEMS input files generated
- [ ] 4,928 CemGEMS output files produced
- [ ] Master dataset with CemGEMS results
- [ ] Reaction-path data for representative cases

### Visualizations
- [ ] Phase maps (Type A) - updated with CemGEMS data
- [ ] Ternary diagrams (Type B) - updated
- [ ] Trend curves - updated with N-A-S-H, C-(N)-A-S-H
- [ ] Reaction-path curves - true incremental CO2

### Documentation
- [ ] Technical report updated for CemGEMS
- [ ] Methodology document updated
- [ ] CemGEMS setup guide created
- [ ] Assumptions/limitations clearly stated

---

## 🚦 GO/NO-GO DECISION POINTS

### Can We Proceed?

**Phase 0 Checkpoint**: Before starting any coding
- ❓ Is CemGEMS installation feasible? (licensing, system requirements)
- ❓ Can we obtain Cemdata20? (licensing, cost)
- ❓ Timeline acceptable? (4-6 weeks vs immediate need)

**Phase 1 Checkpoint**: After CemGEMS test
- ❓ Does CemGEMS work as expected?
- ❓ Can we parse output format?
- ❓ Is Cemdata20 compatible?

**Phase 4 Checkpoint**: After first 100 calculations
- ❓ Is convergence rate acceptable? (target >90%)
- ❓ Is computation time reasonable? (target <10 min per case)
- ❓ Are results physically plausible?

---

## 💡 FINAL RECOMMENDATION

**If client requires actual CemGEMS**:
→ Follow this roadmap, start with Phase 0

**If simplified model is acceptable**:
→ Keep current implementation, add detailed limitations section to documentation

**Best approach**:
→ Present current work as "Phase 1: Proof of Concept"
→ Propose this roadmap as "Phase 2: Production Implementation with CemGEMS"
→ Get client approval and timeline extension before proceeding

**The choice depends on**:
1. Client's flexibility on methodology
2. Available budget/time
3. Access to CemGEMS and Cemdata20
4. Availability of Rietveld XRD data

---

**Document Version**: 1.0  
**Created**: December 31, 2025  
**Status**: Ready for review and decision
