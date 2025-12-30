# Complete xGEMS Command-Line Coding Roadmap

## Project Overview
**Goal**: Complete thermodynamic modeling of carbonation equilibrium for fly ash + cement + sodium silicate + coal gangue + water + CO₂ system using xGEMS (command-line only, no GUI)

**Total Calculations**: 4,928 equilibrium cases (4×11×7×4×4 full factorial design)

---

## Phase 1: Environment Setup & xGEMS Configuration
**Goal**: Get xGEMS running via command line with proper database

### Tasks:
1. Install xGEMS/GEM-Selektor kernel (CLI version)
2. Locate and configure Cemdata18 thermodynamic database
3. Test basic xGEMS command-line execution
4. Set up Python environment:
   - `numpy`, `pandas`, `matplotlib`
   - `python-ternary` for ternary diagrams
   - `multiprocessing` for parallel execution

### Validation:
Run a simple test case and parse output successfully

### xGEMS Command-Line Usage:
```bash
# Typical xGEMS call
xgems -i input_file.inp -o output_file.out -d database.dat

# Batch mode
for f in inputs/*.inp; do
    xgems -i $f -o runs/$(basename $f .inp).out
done
```

---

## Phase 2: Input Chemistry Engine
**Goal**: Convert mix designs → bulk chemical composition

### Code Modules to Build:

#### `mix_design_generator.py`
- Generate all 4,928 combinations (4×11×7×4×4)
- Input: R, f_FA, yCO2, w_SS, w/b
- Output: Mass of each raw material (cement, fly ash, coal gangue, water, sodium silicate)

#### `oxide_calculator.py`
- Convert raw material masses → oxide masses using XRF data
- Convert oxide masses → moles
- Sum total system composition: Ca, Si, Al, Fe, Mg, K, Na, S, O, H, C
- Handle sodium silicate decomposition (Na₂O + SiO₂ + H₂O)
- Account for CO₂ addition based on gas phase specification

### Key Calculations:
```python
# For each mix:
cement_mass = (R * gangue_mass) * (1 - f_FA)
flyash_mass = (R * gangue_mass) * f_FA
water_mass = w_b * (cement_mass + flyash_mass) - water_from_SS
sodium_silicate_mass = w_SS * total_slurry_mass
```

### Validation:
Mass balance closure, reasonable mole ratios

---

## Phase 3: xGEMS Input File Generator
**Goal**: Automated creation of 4,928 xGEMS input files

### Code Modules:

#### `xgems_template.py`
- Create base template structure for xGEMS input
- Define system components (independent components: Ca, Si, Al, Fe, Mg, K, Na, S, O, H, C)
- Define phases to consider:
  - **Solid phases** (from Cemdata18: C-S-H, calcite, portlandite, ettringite, monosulfoaluminate, etc.)
  - **Aqueous solution**
  - **Gas phase** (CO₂, H₂O vapor)

#### `xgems_input_writer.py`
- For each mix design:
  - Write bulk composition (moles of each element)
  - Set temperature = 25°C = 298.15 K
  - Set total pressure = 1 atm = 1.01325 bar
  - Set gas phase composition: X(CO₂) = yCO2, X(N₂) = 1-yCO2 (or just fix pCO₂)
  - Set solver options (convergence criteria, max iterations)

### Output:
`inputs/generated/mix_XXXX.inp` (4,928 files)

---

## Phase 4: Batch Execution Controller
**Goal**: Run all 4,928 equilibrium calculations

### Code Modules:

#### `batch_runner.py`
```python
# Sequential or parallel execution
for each input_file:
    - Call xGEMS via subprocess: `xgems -i input.inp -o output.dat`
    - Capture stdout/stderr
    - Check for convergence
    - Log errors
    - Store output files
```

### Parallel Execution Option:
```python
from multiprocessing import Pool
# Run multiple xGEMS instances in parallel
```

### Error Handling:
- **Non-convergence**: log and skip or retry with relaxed criteria
- **Missing phases**: document which database phases are unavailable
- **Numerical instabilities**: adjust initial guesses

### Output:
`runs/equilibrium/mix_XXXX.out` (4,928 files)

---

## Phase 5: Output Parser & Data Extraction
**Goal**: Extract structured data from xGEMS outputs

### Code Modules:

#### `xgems_output_parser.py`
- Parse xGEMS output format (text file parsing)
- Extract for each run:
  - List of stable phases
  - Phase amounts (moles, mass, volume)
  - Phase compositions (if available)
  - Solution pH, pe (redox potential)
  - Aqueous species concentrations

#### `data_aggregator.py`
- Build master dataframe:
  - **Columns**: R, f_FA, yCO2, w_SS, w/b, Phase1_mass, Phase2_mass, ..., pH, convergence_flag
  - **One row per mix design**
- Save as CSV/Excel

### Validation:
Check for missing data, verify phase name consistency

---

## Phase 6: Phase Classification & Dominant Phase Logic
**Goal**: Identify dominant phase for phase diagrams

### Code Modules:

#### `phase_classifier.py`
```python
def classify_dominant_phase(phase_amounts):
    # Option 1: Maximum solid mass fraction
    # Option 2: Classify by assemblage (e.g., "calcite + C-S-H")
    # Option 3: Ternary classification based on Ca/Si/Al ratios
    return dominant_phase_label
```

### Output:
Add `dominant_phase` column to master dataset

---

## Phase 7: 2D Phase Map Generation (Type A)
**Goal**: Create phase stability maps

### Code Modules:

#### `phase_map_plotter.py`
```python
# Fix R = 0.6, w_SS = 3%, w/b = 1.4 (example)
# Create 2D grid: f_FA (11 levels) × yCO2 (7 levels)
# For each grid point, lookup dominant phase
# Create colored contour/scatter plot

import matplotlib.pyplot as plt
# Plot with X = f_FA, Y = yCO2, color = phase type
```

### Output:
PNG/PDF figures for different fixed R values

---

## Phase 8: Ternary Diagram Generation (Type B)
**Goal**: CaO-SiO₂-Al₂O₃ ternary phase diagrams

### Code Modules:

#### `ternary_diagram_plotter.py`
```python
import ternary

# Fix R and yCO2 (e.g., R=0.6, yCO2=20%)
# For all f_FA combinations at this R and yCO2:
#   Calculate normalized (CaO, SiO2, Al2O3) composition
#   Plot point colored by dominant phase

# Create ternary plot with phase region boundaries
```

### Composition Calculation:
- Use initial bulk oxide composition (normalized to CaO+SiO₂+Al₂O₃ = 100%)

### Output:
Ternary diagrams for selected sections

---

## Phase 9: Product Evolution Trend Curves
**Goal**: Plot phase amounts vs variables

### Code Modules:

#### `trend_plotter.py`

**Curve Set 1**: Calcite vs yCO2
```python
# Fix R, f_FA, w_SS, w/b
# Extract calcite amounts for all yCO2 values
# Plot: X = yCO2, Y = calcite_mass_fraction
```

**Curve Set 2**: Calcite vs f_FA
```python
# Fix R, yCO2, w_SS, w/b
# Extract calcite amounts for all f_FA values
# Plot: X = f_FA, Y = calcite_mass_fraction
```

### Additional Phases:
C-S-H, portlandite, silica gel, etc.

### Output:
Multi-panel figures showing trends

---

## Phase 10: Reaction-Path Simulations
**Goal**: Stepwise carbonation simulations for 2-3 representative mixes

### Approach:
Sequential equilibrium calculations with increasing CO₂

### Code Modules:

#### `reaction_path_runner.py`
```python
# Select 2-3 representative mixes:
# Mix 1: Low f_FA (e.g., 0.1)
# Mix 2: Medium f_FA (e.g., 0.5)
# Mix 3: High f_FA (e.g., 0.9)

for mix in representative_mixes:
    for step in range(n_steps):
        # Incrementally increase CO2 amount
        CO2_moles = initial_CO2 + step * delta_CO2
        
        # Write xGEMS input with updated CO2
        # Run xGEMS
        # Parse output
        # Record all phase amounts
        
    # Save evolution data
```

#### `reaction_path_plotter.py`
```python
# For each mix:
# Plot phase amounts vs CO2 added (or reaction progress ξ)
# Show phase appearance/disappearance points
```

### Output:
Evolution curves showing phase transformation sequences

---

## Phase 11: Validation & Quality Checks
**Goal**: Ensure results are physically reasonable

### Code Modules:

#### `validation.py`
```python
def check_mass_balance(input_composition, output_phases):
    # Verify: Σ(element_in) = Σ(element_out)
    
def check_carbon_balance(CO2_input, carbonate_phases):
    # Verify: CO2 → carbonate conversion is reasonable
    
def check_convergence_rate():
    # Report: How many runs converged vs failed
    
def check_phase_plausibility():
    # Flag unusual phase assemblages
```

---

## Phase 12: Data Export & Visualization Pipeline
**Goal**: Generate all required deliverables

### Deliverables:

1. **Master Dataset**:
   - `outputs/tables/master_dataset.csv` (4,928 rows)
   - Columns: all variables + all phase amounts + metadata

2. **Phase Diagrams**:
   - `outputs/figures/phase_map_R0.6.png`
   - `outputs/figures/ternary_R0.6_CO2_20pct.png`

3. **Trend Curves**:
   - `outputs/figures/calcite_vs_CO2.png`
   - `outputs/figures/CSH_vs_flyash.png`

4. **Reaction Paths**:
   - `outputs/tables/reaction_path_mix001.csv`
   - `outputs/figures/reaction_path_mix001.png`

5. **Scripts Package**:
   - All Python scripts with comments
   - README with execution instructions
   - `requirements.txt` for Python dependencies

6. **xGEMS Project Files**:
   - Template input file
   - Database files used
   - Configuration documentation

---

## Phase 13: Final Report Documentation

### Document in Report:

#### 1. Software & Database
- xGEMS version
- Cemdata18.1 database version
- Python version and key library versions

#### 2. Methodology
- CO₂ boundary condition implementation (fixed pCO₂ = yCO2 × 1 atm)
- Dominant phase criterion (e.g., max solid mass fraction)
- Ternary composition basis (initial bulk oxide composition)
- Phase amount normalization (e.g., per 100g binder)

#### 3. Assumptions & Limitations
- Closed system assumption
- Thermodynamic equilibrium (no kinetics)
- Database limitations (missing phases)
- Convergence issues encountered

#### 4. Results Summary
- Key findings from phase maps
- Major trends observed
- Reaction pathway insights

---

## Recommended Execution Timeline

1. **Week 1**: Phases 1-3 (Setup + Input generation)
2. **Week 2**: Phases 4-6 (Batch execution + Data extraction)
3. **Week 3**: Phases 7-9 (2D diagrams + Ternary + Trends)
4. **Week 4**: Phases 10-13 (Reaction paths + Validation + Documentation)

---

## Key Technical Considerations

### Database Selection
- Use **Cemdata18** (version 18.1 available in workspace)
- Contains C-S-H models, AFm/AFt phases, carbonates
- Check if all required elements (K, Na) are supported

### Gas Phase Handling
- Set CO₂ partial pressure: `pCO2 = yCO2 × 1.01325 bar`
- Include water vapor at equilibrium
- Or fix gas composition: `X_CO2 = yCO2, X_H2O = 1-yCO2`

### Convergence Strategy
- Start with simple cases (no CO₂, medium f_FA)
- If convergence fails, adjust:
  - Initial phase estimates
  - Solver tolerance
  - Maximum iterations

---

## Directory Structure

```
project/
│
├── database/
│   └── Cemdata18.1_08-01-19/
│
├── inputs/
│   ├── templates/
│   └── generated/          # 4,928 input files
│
├── runs/
│   ├── equilibrium/        # 4,928 output files
│   └── reaction_path/      # 2-3 reaction path outputs
│
├── outputs/
│   ├── raw/
│   ├── tables/             # CSV/Excel datasets
│   └── figures/            # All plots
│
├── scripts/
│   ├── mix_design_generator.py
│   ├── oxide_calculator.py
│   ├── xgems_template.py
│   ├── xgems_input_writer.py
│   ├── batch_runner.py
│   ├── xgems_output_parser.py
│   ├── data_aggregator.py
│   ├── phase_classifier.py
│   ├── phase_map_plotter.py
│   ├── ternary_diagram_plotter.py
│   ├── trend_plotter.py
│   ├── reaction_path_runner.py
│   ├── reaction_path_plotter.py
│   └── validation.py
│
├── requirements.txt
├── README.md
└── report/
```

---

## Independent Variables (Full Factorial Design)

1. **Binder-to-aggregate ratio (R)**:
   - Values: {0.3, 0.6, 0.9, 1.2} (4 levels)
   - Definition: (Cement + Fly ash) / Coal gangue

2. **Fly ash replacement ratio (f_FA)**:
   - Values: {0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0} (11 levels)
   - Definition: Fly ash / (Cement + Fly ash)

3. **CO₂ concentration (yCO2)**:
   - Values: {0%, 15%, 20%, 25%, 30%, 35%, 40%} (7 levels)
   - Definition: Volume fraction of CO₂ in gas phase

4. **Sodium silicate dosage (w_SS)**:
   - Values: {2%, 3%, 4%, 5%} (4 levels)
   - Definition: Sodium silicate / total slurry mass

5. **Water-to-binder ratio (w/b)**:
   - Values: {1.1, 1.4, 1.7, 2.0} (4 levels)
   - Definition: Water / (Cement + Fly ash)

**Total combinations**: 4 × 11 × 7 × 4 × 4 = **4,928 cases**

---

## Raw Material Compositions (XRF, wt%)

### Coal Gangue
- SiO₂: 57.74
- Al₂O₃: 20.58
- Fe₂O₃: 4.31
- CaO: 0.20
- MgO: 1.00
- K₂O: 2.76

### Cement
- SiO₂: 19.76
- Al₂O₃: 11.47
- Fe₂O₃: 0.50
- CaO: 45.63
- MgO: 6.27
- SO₃: 13.68

### Fly Ash
- SiO₂: 52.61
- Al₂O₃: 12.60
- Fe₂O₃: 8.24
- CaO: 18.23
- MgO: 1.47
- K₂O: 1.44

### Sodium Silicate (Water Glass)
- Mr = 212.14
- Na₂O: 29.2 wt%
- SiO₂: 29.2 wt%
- H₂O: 41.6 wt%
- Na₂O/SiO₂ molar ratio ≈ 1.03

---

## Required Outputs Summary

### 1. Stable Phase List & Amounts
For each of 4,928 cases:
- Names of all stable solid phases
- Phase amounts (mass or moles)

### 2. Type A Phase Maps
- Fix one R value (minimum R=0.6)
- 2D grid: X=f_FA, Y=yCO2
- Color by dominant phase

### 3. Type B Ternary Diagrams
- Fix R and yCO2
- CaO-SiO₂-Al₂O₃ ternary
- Color by phase assemblage

### 4. Product Evolution Trends
- Calcite (+ other phases) vs yCO2
- Calcite (+ other phases) vs f_FA

### 5. Reaction-Path Simulations
- 2-3 representative mixes
- Stepwise CO₂ addition
- Phase evolution curves

---

This roadmap provides a complete, coding-focused approach to completing the entire thermodynamic modeling project using xGEMS command-line tools with no GUI interaction required.
