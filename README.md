# xGEMS Thermodynamic Modeling Project

## Project Overview
Complete thermodynamic modeling of carbonation equilibrium for a composite binder system:
- **Fly ash + Cement + Sodium silicate + Coal gangue + Water + CO₂**
- **4,928 equilibrium calculations** (4×11×7×4×4 full factorial design)

## Phase 1: Environment Setup - ✓ COMPLETE

### Completed Tasks

#### 1. Directory Structure ✓
```
project/
├── database/                    # For processed database files
├── Cemdata18.1_08-01-19/       # Original Cemdata18 database (34 .ndx files)
├── inputs/
│   ├── templates/              # Input file templates
│   └── generated/              # Generated input files (will contain 4,928)
├── runs/
│   ├── equilibrium/            # Equilibrium calculation outputs
│   └── reaction_path/          # Reaction path outputs
├── outputs/
│   ├── raw/                    # Raw output data
│   ├── tables/                 # CSV/Excel tables
│   └── figures/                # All plots and diagrams
├── scripts/                    # Python scripts
│   ├── config.py              # ✓ Configuration module
│   └── test_environment.py    # ✓ Environment validation
├── requirements.txt            # ✓ Python dependencies
└── README.md                   # This file
```

#### 2. Python Environment ✓
All required packages installed:
- ✓ numpy 1.26.4
- ✓ pandas 2.1.4
- ✓ matplotlib 3.8.2
- ✓ scipy 1.11.4
- ✓ python-ternary 1.0.8
- ✓ openpyxl 3.1.5

#### 3. Configuration Module ✓
Created `scripts/config.py` with:
- All project paths
- Thermodynamic conditions (25°C, 1 atm)
- Independent variable arrays
- Raw material XRF compositions
- Oxide and element molar masses
- Conversion factors (oxide → element)
- System component definitions

#### 4. Database Files ✓
Cemdata18.1 (08-01-19) available with:
- 13 phase definition files
- 7 dependent component files
- 3 independent component files
- 5 composition files
- 4 reaction files
- 2 reference files

### Validation Results

Running `python3 scripts/test_environment.py`:
```
✓ All directories created
✓ All Python packages installed
✓ Configuration loaded successfully
✓ Oxide-to-element conversions verified
✓ 34 Cemdata18 database files found
```

**Note**: Coal gangue composition sums to 86.59 wt% (missing LOI/other components - acceptable)

## Critical Issue: xGEMS Not Available

### Status
- ❌ xGEMS/GEM-Selektor **NOT installed** on system
- ✓ Cemdata18 database files available (binary .ndx format)
- ✓ Python environment ready

### Options to Proceed

#### Option 1: Install GEM-Selektor/xGEMS (Recommended)
**Advantages**:
- Direct use of Cemdata18 database
- Robust GEM solver
- Designed for cement chemistry

**Steps**:
1. Download GEM-Selektor from: https://gems.web.psi.ch/
2. Install command-line tools
3. Configure database path
4. Test with simple case

#### Option 2: Use PHREEQC
**Advantages**:
- Widely used geochemical modeling code
- Python interface available (phreeqpy)
- Can import thermodynamic data

**Disadvantages**:
- Need to convert Cemdata18 → PHREEQC format
- May not have all C-S-H models

#### Option 3: Use Reaktoro
**Advantages**:
- Modern C++/Python interface
- Can use GEMS databases
- Good for automation

**Disadvantages**:
- Requires database conversion
- Learning curve

#### Option 4: Direct Gibbs Energy Minimization
**Advantages**:
- Full control over implementation
- No external dependencies

**Disadvantages**:
- Need to extract/convert Cemdata18 thermodynamic data
- Must implement GEM solver
- Complex and time-consuming

### Recommended Path Forward

**Immediate**: Proceed with Phase 2 (mix design and oxide calculation) - these are **independent** of the solver choice.

**Parallel**: Research and install xGEMS/GEM-Selektor (Option 1) as it's the most straightforward path for using Cemdata18.

## Phase 2 Preview: What's Next

Phase 2 can proceed **NOW** without xGEMS:

### 2.1 Mix Design Generator
Create `scripts/mix_design_generator.py`:
- Generate all 4,928 variable combinations
- Calculate raw material masses
- Export to CSV

### 2.2 Oxide Calculator
Create `scripts/oxide_calculator.py`:
- Convert material masses → oxide masses (using XRF data)
- Convert oxides → elemental moles
- Handle sodium silicate decomposition
- Account for CO₂ in gas phase
- Validate mass balance

These modules will produce the **bulk compositions** needed for any thermodynamic solver.

## Running the Environment Test

```bash
cd /teamspace/studios/this_studio
python3 scripts/test_environment.py
```

This validates:
- ✓ Directory structure
- ✓ Python packages
- ✓ Configuration loading
- ✓ Oxide composition data
- ✓ Conversion factors
- ✓ Database files

## Project Variables Summary

### Independent Variables (Full Factorial)
- **R** (Binder/aggregate): 0.3, 0.6, 0.9, 1.2 (4 levels)
- **f_FA** (Fly ash replacement): 0.0 to 1.0 in steps of 0.1 (11 levels)
- **yCO2** (CO₂ concentration): 0%, 15%, 20%, 25%, 30%, 35%, 40% (7 levels)
- **w_SS** (Sodium silicate): 2%, 3%, 4%, 5% (4 levels)
- **w/b** (Water/binder): 1.1, 1.4, 1.7, 2.0 (4 levels)

**Total**: 4 × 11 × 7 × 4 × 4 = **4,928 combinations**

### Fixed Conditions
- Temperature: 25°C (298.15 K)
- Total pressure: 1 atm (1.01325 bar)
- System: Closed (constant total composition)

### System Components
Ca, Si, Al, Fe, Mg, K, Na, S, O, H, C (11 elements)

## Raw Material Data

All XRF compositions loaded in `config.py`:
- Coal gangue (6 oxides)
- Cement (6 oxides)
- Fly ash (6 oxides)
- Sodium silicate (Na₂O, SiO₂, H₂O)

## Contact & Notes

**Current Status**: Phase 1 COMPLETE ✓

**Blockers**: 
- Need xGEMS installation for Phase 3+ (or choose alternative solver)

**Can Proceed Immediately**:
- Phase 2: Mix design generator
- Phase 2: Oxide calculator

**Date**: December 27, 2025
