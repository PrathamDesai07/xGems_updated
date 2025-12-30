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


if __name__ == '__main__':
    print_project_info()
    check_python_packages()
    validate_oxide_compositions()
    test_oxide_to_element_conversion()
    check_cemdata_files()
    
    print()
    print("=" * 80)
    print("Phase 1 Environment Setup: COMPLETE")
    print("=" * 80)
    print()
    print("Next Steps:")
    print("  1. Install xGEMS/GEM-Selektor or choose alternative solver")
    print("  2. Begin Phase 2: Implement mix design generator")
    print("  3. Begin Phase 2: Implement oxide calculator")
    print()
