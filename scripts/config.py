"""
Configuration module for xGEMS thermodynamic modeling project.
Contains all project paths, constants, and raw material compositions.
"""

import os
from pathlib import Path

# ============================================================================
# PROJECT PATHS
# ============================================================================
PROJECT_ROOT = Path(__file__).parent.parent
DATABASE_DIR = PROJECT_ROOT / "database"
CEMDATA_DIR = PROJECT_ROOT / "Cemdata18.1_08-01-19"
INPUTS_DIR = PROJECT_ROOT / "inputs"
INPUTS_TEMPLATES_DIR = INPUTS_DIR / "templates"
INPUTS_GENERATED_DIR = INPUTS_DIR / "generated"
RUNS_DIR = PROJECT_ROOT / "runs"
RUNS_EQUILIBRIUM_DIR = RUNS_DIR / "equilibrium"
RUNS_REACTION_PATH_DIR = RUNS_DIR / "reaction_path"
OUTPUTS_DIR = PROJECT_ROOT / "outputs"
OUTPUTS_RAW_DIR = OUTPUTS_DIR / "raw"
OUTPUTS_TABLES_DIR = OUTPUTS_DIR / "tables"
OUTPUTS_FIGURES_DIR = OUTPUTS_DIR / "figures"
OUTPUTS_LOGS_DIR = OUTPUTS_DIR / "logs"
SCRIPTS_DIR = PROJECT_ROOT / "scripts"

# ============================================================================
# THERMODYNAMIC CONDITIONS
# ============================================================================
TEMPERATURE_C = 25.0  # Celsius
TEMPERATURE_K = TEMPERATURE_C + 273.15  # Kelvin
TOTAL_PRESSURE_ATM = 1.0  # atm
TOTAL_PRESSURE_BAR = 1.01325  # bar

# ============================================================================
# INDEPENDENT VARIABLES (Full Factorial Design)
# ============================================================================

# Binder-to-aggregate ratio: (Cement + Fly ash) / Coal gangue
BINDER_AGGREGATE_RATIOS = [0.3, 0.6, 0.9, 1.2]

# Fly ash replacement ratio: Fly ash / (Cement + Fly ash)
FLY_ASH_REPLACEMENT_RATIOS = [0.0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0]

# CO2 concentration in gas phase (volume fraction)
CO2_CONCENTRATIONS = [0.00, 0.15, 0.20, 0.25, 0.30, 0.35, 0.40]

# Sodium silicate dosage: sodium silicate / total slurry mass
SODIUM_SILICATE_DOSAGES = [0.02, 0.03, 0.04, 0.05]

# Water-to-binder ratio: Water / (Cement + Fly ash)
WATER_BINDER_RATIOS = [1.1, 1.4, 1.7, 2.0]

# Total number of combinations
TOTAL_COMBINATIONS = (
    len(BINDER_AGGREGATE_RATIOS) * 
    len(FLY_ASH_REPLACEMENT_RATIOS) * 
    len(CO2_CONCENTRATIONS) * 
    len(SODIUM_SILICATE_DOSAGES) * 
    len(WATER_BINDER_RATIOS)
)

# ============================================================================
# RAW MATERIAL COMPOSITIONS (XRF, wt%)
# ============================================================================

# Coal Gangue composition (wt%)
COAL_GANGUE_COMPOSITION = {
    'SiO2': 57.74,
    'Al2O3': 20.58,
    'Fe2O3': 4.31,
    'CaO': 0.20,
    'MgO': 1.00,
    'K2O': 2.76,
}

# Cement composition (wt%)
CEMENT_COMPOSITION = {
    'SiO2': 19.76,
    'Al2O3': 11.47,
    'Fe2O3': 0.50,
    'CaO': 45.63,
    'MgO': 6.27,
    'SO3': 13.68,
}

# Fly Ash composition (wt%)
FLY_ASH_COMPOSITION = {
    'SiO2': 52.61,
    'Al2O3': 12.60,
    'Fe2O3': 8.24,
    'CaO': 18.23,
    'MgO': 1.47,
    'K2O': 1.44,
}

# Sodium Silicate (water glass) composition (wt%)
SODIUM_SILICATE_COMPOSITION = {
    'Na2O': 29.2,
    'SiO2': 29.2,
    'H2O': 41.6,
}

# Sodium silicate molar mass (g/mol)
SODIUM_SILICATE_MOLAR_MASS = 212.14

# ============================================================================
# OXIDE MOLAR MASSES (g/mol)
# ============================================================================
OXIDE_MOLAR_MASSES = {
    'CaO': 56.0774,
    'SiO2': 60.0843,
    'Al2O3': 101.9613,
    'Fe2O3': 159.6882,
    'MgO': 40.3044,
    'K2O': 94.1960,
    'Na2O': 61.9789,
    'SO3': 80.0632,
    'H2O': 18.01528,
    'CO2': 44.0095,
}

# ============================================================================
# ELEMENT ATOMIC MASSES (g/mol)
# ============================================================================
ELEMENT_ATOMIC_MASSES = {
    'Ca': 40.078,
    'Si': 28.0855,
    'Al': 26.9815,
    'Fe': 55.845,
    'Mg': 24.305,
    'K': 39.0983,
    'Na': 22.9898,
    'S': 32.065,
    'O': 15.9994,
    'H': 1.00794,
    'C': 12.0107,
}

# ============================================================================
# OXIDE TO ELEMENT CONVERSION FACTORS
# ============================================================================
# These factors convert oxide mass to element mass
# e.g., Ca mass = CaO mass * OXIDE_TO_ELEMENT_FACTORS['CaO']['Ca']

OXIDE_TO_ELEMENT_FACTORS = {
    'CaO': {
        'Ca': ELEMENT_ATOMIC_MASSES['Ca'] / OXIDE_MOLAR_MASSES['CaO'],
        'O': ELEMENT_ATOMIC_MASSES['O'] / OXIDE_MOLAR_MASSES['CaO']
    },
    'SiO2': {
        'Si': ELEMENT_ATOMIC_MASSES['Si'] / OXIDE_MOLAR_MASSES['SiO2'],
        'O': 2 * ELEMENT_ATOMIC_MASSES['O'] / OXIDE_MOLAR_MASSES['SiO2']
    },
    'Al2O3': {
        'Al': 2 * ELEMENT_ATOMIC_MASSES['Al'] / OXIDE_MOLAR_MASSES['Al2O3'],
        'O': 3 * ELEMENT_ATOMIC_MASSES['O'] / OXIDE_MOLAR_MASSES['Al2O3']
    },
    'Fe2O3': {
        'Fe': 2 * ELEMENT_ATOMIC_MASSES['Fe'] / OXIDE_MOLAR_MASSES['Fe2O3'],
        'O': 3 * ELEMENT_ATOMIC_MASSES['O'] / OXIDE_MOLAR_MASSES['Fe2O3']
    },
    'MgO': {
        'Mg': ELEMENT_ATOMIC_MASSES['Mg'] / OXIDE_MOLAR_MASSES['MgO'],
        'O': ELEMENT_ATOMIC_MASSES['O'] / OXIDE_MOLAR_MASSES['MgO']
    },
    'K2O': {
        'K': 2 * ELEMENT_ATOMIC_MASSES['K'] / OXIDE_MOLAR_MASSES['K2O'],
        'O': ELEMENT_ATOMIC_MASSES['O'] / OXIDE_MOLAR_MASSES['K2O']
    },
    'Na2O': {
        'Na': 2 * ELEMENT_ATOMIC_MASSES['Na'] / OXIDE_MOLAR_MASSES['Na2O'],
        'O': ELEMENT_ATOMIC_MASSES['O'] / OXIDE_MOLAR_MASSES['Na2O']
    },
    'SO3': {
        'S': ELEMENT_ATOMIC_MASSES['S'] / OXIDE_MOLAR_MASSES['SO3'],
        'O': 3 * ELEMENT_ATOMIC_MASSES['O'] / OXIDE_MOLAR_MASSES['SO3']
    },
    'H2O': {
        'H': 2 * ELEMENT_ATOMIC_MASSES['H'] / OXIDE_MOLAR_MASSES['H2O'],
        'O': ELEMENT_ATOMIC_MASSES['O'] / OXIDE_MOLAR_MASSES['H2O']
    },
    'CO2': {
        'C': ELEMENT_ATOMIC_MASSES['C'] / OXIDE_MOLAR_MASSES['CO2'],
        'O': 2 * ELEMENT_ATOMIC_MASSES['O'] / OXIDE_MOLAR_MASSES['CO2']
    },
}

# ============================================================================
# SYSTEM COMPONENTS (for GEM calculation)
# ============================================================================
# Independent components in the system
SYSTEM_COMPONENTS = ['Ca', 'Si', 'Al', 'Fe', 'Mg', 'K', 'Na', 'S', 'O', 'H', 'C']

# ============================================================================
# REFERENCE MASSES FOR NORMALIZATION
# ============================================================================
# Used to normalize amounts (e.g., per 100g binder, per kg water)
REFERENCE_GANGUE_MASS = 100.0  # grams
REFERENCE_BINDER_MASS = 100.0  # grams

# ============================================================================
# OUTPUT COLUMN NAMES
# ============================================================================
MIX_DESIGN_COLUMNS = [
    'mix_id',
    'R',  # Binder-to-aggregate ratio
    'f_FA',  # Fly ash replacement ratio
    'yCO2',  # CO2 concentration
    'w_SS',  # Sodium silicate dosage
    'w_b',  # Water-to-binder ratio
    'cement_mass_g',
    'flyash_mass_g',
    'gangue_mass_g',
    'water_mass_g',
    'sodium_silicate_mass_g',
    'total_mass_g',
]

# ============================================================================
# LOGGING CONFIGURATION
# ============================================================================
LOG_FORMAT = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
LOG_DATE_FORMAT = '%Y-%m-%d %H:%M:%S'

# ============================================================================
# GEMS/xGEMS CONFIGURATION
# ============================================================================
# Note: xGEMS is not installed. We will need to either:
# 1. Install GEM-Selektor/xGEMS
# 2. Use alternative thermodynamic modeling tools (e.g., PHREEQC, Reaktoro)
# 3. Implement direct Gibbs energy minimization

GEMS_EXECUTABLE = None  # To be configured after installation
GEMS_DATABASE = CEMDATA_DIR  # Cemdata18.1 database directory

# ============================================================================
# VALIDATION TOLERANCES
# ============================================================================
MASS_BALANCE_TOLERANCE = 1e-6  # Relative tolerance for mass balance check
CONVERGENCE_TOLERANCE = 1e-8  # Convergence tolerance for GEM solver

# ============================================================================
# PARALLEL EXECUTION SETTINGS
# ============================================================================
MAX_WORKERS = os.cpu_count() or 4  # Number of parallel workers
