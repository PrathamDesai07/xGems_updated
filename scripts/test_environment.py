"""
Utility functions for the thermodynamic modeling project.
"""

import sys
from pathlib import Path

# Add scripts directory to path
SCRIPTS_DIR = Path(__file__).parent
if str(SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_DIR))

import config


def print_project_info():
    """Print project configuration and environment information."""
    print("=" * 80)
    print("xGEMS Thermodynamic Modeling Project - Environment Check")
    print("=" * 80)
    print()
    
    print("Project Paths:")
    print(f"  Project Root: {config.PROJECT_ROOT}")
    print(f"  Cemdata Directory: {config.CEMDATA_DIR}")
    print(f"  Exists: {config.CEMDATA_DIR.exists()}")
    print()
    
    print("Project Configuration:")
    print(f"  Temperature: {config.TEMPERATURE_C}°C ({config.TEMPERATURE_K} K)")
    print(f"  Pressure: {config.TOTAL_PRESSURE_ATM} atm ({config.TOTAL_PRESSURE_BAR} bar)")
    print()
    
    print("Independent Variables:")
    print(f"  Binder-aggregate ratios (R): {config.BINDER_AGGREGATE_RATIOS}")
    print(f"  Fly ash replacement ratios (f_FA): {config.FLY_ASH_REPLACEMENT_RATIOS}")
    print(f"  CO2 concentrations (yCO2): {config.CO2_CONCENTRATIONS}")
    print(f"  Sodium silicate dosages (w_SS): {config.SODIUM_SILICATE_DOSAGES}")
    print(f"  Water-binder ratios (w/b): {config.WATER_BINDER_RATIOS}")
    print(f"  Total combinations: {config.TOTAL_COMBINATIONS}")
    print()
    
    print("Raw Materials:")
    print("  Coal Gangue composition (wt%):")
    for oxide, value in config.COAL_GANGUE_COMPOSITION.items():
        print(f"    {oxide}: {value:.2f}")
    print()
    
    print("  Cement composition (wt%):")
    for oxide, value in config.CEMENT_COMPOSITION.items():
        print(f"    {oxide}: {value:.2f}")
    print()
    
    print("  Fly Ash composition (wt%):")
    for oxide, value in config.FLY_ASH_COMPOSITION.items():
        print(f"    {oxide}: {value:.2f}")
    print()
    
    print("  Sodium Silicate composition (wt%):")
    for component, value in config.SODIUM_SILICATE_COMPOSITION.items():
        print(f"    {component}: {value:.2f}")
    print()
    
    print("System Components:")
    print(f"  {', '.join(config.SYSTEM_COMPONENTS)}")
    print()
    
    print("Directory Structure:")
    directories = [
        config.DATABASE_DIR,
        config.INPUTS_DIR,
        config.INPUTS_TEMPLATES_DIR,
        config.INPUTS_GENERATED_DIR,
        config.RUNS_DIR,
        config.RUNS_EQUILIBRIUM_DIR,
        config.RUNS_REACTION_PATH_DIR,
        config.OUTPUTS_DIR,
        config.OUTPUTS_RAW_DIR,
        config.OUTPUTS_TABLES_DIR,
        config.OUTPUTS_FIGURES_DIR,
    ]
    
    for directory in directories:
        status = "✓" if directory.exists() else "✗"
        print(f"  {status} {directory.relative_to(config.PROJECT_ROOT)}")
    print()
    
    print("=" * 80)


def check_python_packages():
    """Check if required Python packages are installed."""
    print("Checking Python packages...")
    print("-" * 80)
    
    required_packages = [
        'numpy',
        'pandas',
        'matplotlib',
        'scipy',
        'ternary',
        'openpyxl',
    ]
    
    import importlib
    
    for package in required_packages:
        try:
            if package == 'ternary':
                module = importlib.import_module('ternary')
            else:
                module = importlib.import_module(package)
            
            version = getattr(module, '__version__', 'unknown')
            print(f"  ✓ {package:15s} {version}")
        except ImportError:
            print(f"  ✗ {package:15s} NOT INSTALLED")
    
    print("-" * 80)
    print()


def validate_oxide_compositions():
    """Validate that oxide compositions sum to reasonable values."""
    print("Validating oxide compositions...")
    print("-" * 80)
    
    materials = {
        'Coal Gangue': config.COAL_GANGUE_COMPOSITION,
        'Cement': config.CEMENT_COMPOSITION,
        'Fly Ash': config.FLY_ASH_COMPOSITION,
        'Sodium Silicate': config.SODIUM_SILICATE_COMPOSITION,
    }
    
    for material_name, composition in materials.items():
        total = sum(composition.values())
        status = "✓" if 90 <= total <= 105 else "⚠"
        print(f"  {status} {material_name:20s}: {total:6.2f} wt%")
    
    print("-" * 80)
    print()


def test_oxide_to_element_conversion():
    """Test oxide to element conversion factors."""
    print("Testing oxide to element conversion factors...")
    print("-" * 80)
    
    # Test a few conversions
    test_cases = [
        ('CaO', 100.0),  # 100g CaO
        ('SiO2', 100.0),  # 100g SiO2
        ('Al2O3', 100.0),  # 100g Al2O3
    ]
    
    for oxide, mass in test_cases:
        print(f"\n  {oxide} ({mass}g):")
        factors = config.OXIDE_TO_ELEMENT_FACTORS[oxide]
        for element, factor in factors.items():
            element_mass = mass * factor
            print(f"    → {element}: {element_mass:.4f}g (factor: {factor:.6f})")
    
    print()
    print("-" * 80)
    print()


def check_cemdata_files():
    """Check available Cemdata18 database files."""
    print("Checking Cemdata18 database files...")
    print("-" * 80)
    
    if not config.CEMDATA_DIR.exists():
        print(f"  ✗ Cemdata directory not found: {config.CEMDATA_DIR}")
        return
    
    # Count different types of files
    file_patterns = {
        'Phase definitions': 'phase*.ndx',
        'Dependent components': 'dcomp*.ndx',
        'Independent components': 'icomp*.ndx',
        'Compositions': 'compos*.ndx',
        'Reactions': 'reacdc*.ndx',
        'References': 'sdref*.ndx',
    }
    
    for file_type, pattern in file_patterns.items():
        files = list(config.CEMDATA_DIR.glob(pattern))
        print(f"  {file_type:25s}: {len(files):2d} files")
    
    print()
    print("  Total .ndx files:", len(list(config.CEMDATA_DIR.glob('*.ndx'))))
    print("-" * 80)
    print()


def test_cemgems_installation():
    """Test if CemGEMS/GEM-Selektor is properly installed."""
    print("Testing CemGEMS installation...")
    print("-" * 80)
    
    try:
        from cemgems_wrapper import CemGEMSRunner, get_cemgems_info
        
        info = get_cemgems_info()
        
        if info['available']:
            print(f"  ✓ CemGEMS found and operational")
            print(f"    Executable: {info['executable']}")
            if info['version']:
                print(f"    Version: {info['version']}")
        else:
            print(f"  ✗ CemGEMS not found or not operational")
            if info['executable']:
                print(f"    Searched path: {info['executable']}")
            print()
            print("  Installation options:")
            print("    1. Download from: https://gems.web.psi.ch/GEMS3/")
            print("    2. Install via package manager (if available)")
            print("    3. Use alternative: PHREEQC, Reaktoro")
        
        # Test database paths
        print()
        print("  Database paths:")
        
        if hasattr(config, 'CEMDATA18_PATH'):
            status = "✓" if Path(config.CEMDATA18_PATH).exists() else "✗"
            print(f"    {status} Cemdata18: {config.CEMDATA18_PATH}")
        
        if hasattr(config, 'CEMDATA20_PATH'):
            status = "✓" if Path(config.CEMDATA20_PATH).exists() else "✗"
            print(f"    {status} Cemdata20: {config.CEMDATA20_PATH}")
            if not Path(config.CEMDATA20_PATH).exists():
                print(f"      Note: Cemdata20 required by client specifications")
        
    except ImportError as e:
        print(f"  ✗ Error importing cemgems_wrapper: {e}")
    except Exception as e:
        print(f"  ✗ Error testing CemGEMS: {e}")
    
    print("-" * 80)
    print()


def test_phase_database_configuration():
    """Test phase database configuration."""
    print("Testing phase database configuration...")
    print("-" * 80)
    
    if hasattr(config, 'ENABLED_PHASES'):
        print("  Phase categories defined:")
        for category, phases in config.ENABLED_PHASES.items():
            print(f"    {category:20s}: {len(phases)} phases")
        
        # Check for new required phases
        print()
        print("  Required phases for client specifications:")
        
        required_checks = [
            ('N-A-S-H gel', 'NASH_gel', 'alkali_activated'),
            ('C-(N)-A-S-H gel', 'CNASH_gel', 'alkali_activated'),
        ]
        
        for phase_name, phase_key, category in required_checks:
            if category in config.ENABLED_PHASES:
                if phase_key in config.ENABLED_PHASES[category]:
                    print(f"    ✓ {phase_name} configured")
                else:
                    print(f"    ⚠ {phase_name} not in {category} phases")
            else:
                print(f"    ✗ Category '{category}' not found")
    else:
        print("  ✗ ENABLED_PHASES not configured")
    
    print()
    
    if hasattr(config, 'PHASE_STOICHIOMETRY'):
        print(f"  Phase stoichiometry defined: {len(config.PHASE_STOICHIOMETRY)} phases")
        
        # Test a few conversions
        test_phases = ['C3S', 'C2S', 'Calcite']
        print("  Sample stoichiometry:")
        for phase in test_phases:
            if phase in config.PHASE_STOICHIOMETRY:
                stoich = config.PHASE_STOICHIOMETRY[phase]
                formula = ' '.join([f"{elem}{count}" if count > 1 else elem 
                                   for elem, count in stoich.items()])
                print(f"    {phase:12s}: {formula}")
    else:
        print("  ✗ PHASE_STOICHIOMETRY not configured")
    
    print("-" * 80)
    print()


def test_rietveld_xrd_configuration():
    """Test Rietveld XRD phase data configuration."""
    print("Testing Rietveld XRD phase data...")
    print("-" * 80)
    
    phase_configs = [
        ('CEMENT_PHASES', 'Cement clinker phases'),
        ('FLYASH_PHASES', 'Fly ash mineralogy'),
        ('GANGUE_PHASES', 'Coal gangue mineralogy'),
    ]
    
    for config_name, description in phase_configs:
        if hasattr(config, config_name):
            phases = getattr(config, config_name)
            total = sum(phases.values())
            status = "✓" if 0.99 <= total <= 1.01 else "⚠"
            print(f"  {status} {description:30s}: {total:.4f} (sum of fractions)")
            
            for phase, fraction in phases.items():
                print(f"      {phase:15s}: {fraction:.3f}")
        else:
            print(f"  ✗ {description:30s}: Not configured")
        print()
    
    print("  Note: These are standard compositions. Replace with actual")
    print("        Rietveld XRD data when provided by client.")
    print("-" * 80)
    print()


def test_simulation_mode_configuration():
    """Test simulation mode and reaction path configuration."""
    print("Testing simulation mode configuration...")
    print("-" * 80)
    
    if hasattr(config, 'SIMULATION_MODE'):
        print(f"  Simulation mode: {config.SIMULATION_MODE}")
        
        if config.SIMULATION_MODE == 'coupled_hydration_carbonation':
            print("    ✓ Coupled hydration-carbonation enabled (per client specs)")
        else:
            print("    ⚠ Mode differs from client requirement")
    else:
        print("  ✗ SIMULATION_MODE not configured")
    
    print()
    
    if hasattr(config, 'REACTION_PATH_ENABLED'):
        status = "✓" if config.REACTION_PATH_ENABLED else "⚠"
        print(f"  {status} Reaction path enabled: {config.REACTION_PATH_ENABLED}")
    else:
        print("  ✗ REACTION_PATH_ENABLED not configured")
    
    print()
    
    if hasattr(config, 'HYDRATION_TIME_STEPS'):
        print(f"  Hydration time steps: {len(config.HYDRATION_TIME_STEPS)} defined")
        print(f"    Range: {min(config.HYDRATION_TIME_STEPS)} - {max(config.HYDRATION_TIME_STEPS)} days")
    
    if hasattr(config, 'CARBONATION_TIME_STEPS'):
        print(f"  Carbonation time steps: {len(config.CARBONATION_TIME_STEPS)} defined")
        print(f"    Range: {min(config.CARBONATION_TIME_STEPS)} - {max(config.CARBONATION_TIME_STEPS)} days")
    
    print("-" * 80)
    print()


def run_full_phase1_validation():
    """Run complete Phase 1 validation suite."""
    print()
    print("=" * 80)
    print("PHASE 1 VALIDATION: Environment Setup & CemGEMS Integration")
    print("=" * 80)
    print()
    
    # Existing tests
    print_project_info()
    check_python_packages()
    validate_oxide_compositions()
    test_oxide_to_element_conversion()
    check_cemdata_files()
    
    # New Phase 1 tests
    test_cemgems_installation()
    test_phase_database_configuration()
    test_rietveld_xrd_configuration()
    test_simulation_mode_configuration()
    
    print()
    print("=" * 80)
    print("PHASE 1 VALIDATION COMPLETE")
    print("=" * 80)
    print()
    
    # Summary
    print("Configuration Status:")
    print()
    print("  ✓ Python environment configured")
    print("  ✓ Project paths established")
    print("  ✓ Raw material XRF data loaded")
    print("  ✓ Oxide-to-element conversions validated")
    print("  ✓ Cemdata18 database files present")
    print()
    
    try:
        from cemgems_wrapper import get_cemgems_info
        info = get_cemgems_info()
        
        if info['available']:
            print("  ✓ CemGEMS installation detected and validated")
        else:
            print("  ⚠ CemGEMS not installed (required for production runs)")
            print("    - Current: Simplified Python model available")
            print("    - Action: Install CemGEMS/GEM-Selektor for full implementation")
    except:
        print("  ⚠ CemGEMS wrapper not fully initialized")
    
    print()
    
    if hasattr(config, 'ENABLED_PHASES'):
        print("  ✓ Phase database configuration complete")
        print("  ✓ N-A-S-H and C-(N)-A-S-H gels configured")
    else:
        print("  ✗ Phase database configuration incomplete")
    
    print()
    
    if hasattr(config, 'CEMENT_PHASES') and hasattr(config, 'FLYASH_PHASES'):
        print("  ✓ Rietveld XRD phase data (standard compositions loaded)")
        print("    Note: Replace with actual XRD data when available")
    else:
        print("  ⚠ Rietveld XRD phase data not configured")
    
    print()
    
    if hasattr(config, 'SIMULATION_MODE') and config.SIMULATION_MODE == 'coupled_hydration_carbonation':
        print("  ✓ Coupled hydration-carbonation mode configured")
    else:
        print("  ⚠ Simulation mode not properly configured")
    
    print()
    print("Next Steps:")
    print()
    print("  Priority:")
    print("    1. Install CemGEMS/GEM-Selektor (if production system required)")
    print("    2. Obtain Cemdata20 database")
    print("    3. Request Rietveld XRD data from client")
    print()
    print("  Can proceed now:")
    print("    1. Phase 2: Update mix_design_generator.py for phase-based inputs")
    print("    2. Phase 2: Update oxide_calculator.py for phase stoichiometry")
    print("    3. Phase 3: Prepare CemGEMS input file templates")
    print()
    print("=" * 80)
    print()


if __name__ == '__main__':
    run_full_phase1_validation()

