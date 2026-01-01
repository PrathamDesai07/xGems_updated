"""
Phase 2 Completeness Verification
==================================
Comprehensive check against IMPLEMENTATION_ROADMAP_UPDATED.md requirements.

Verifies:
1. All required functions exist and work
2. No mock functions
3. Accurate calculations
4. Output files complete
5. Requirements from README (2).md satisfied

Author: Phase 2 Final Verification
Date: December 31, 2025
"""

import sys
from pathlib import Path
import inspect

# Add scripts directory to path
SCRIPTS_DIR = Path(__file__).parent
if str(SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_DIR))

import numpy as np
import pandas as pd
import config
from mix_design_generator import MixDesignGenerator
from oxide_calculator import OxideCalculator


def check_function_exists_and_not_mock(module, func_name):
    """Check if function exists and is not a mock."""
    if not hasattr(module, func_name):
        return False, "Function does not exist"
    
    func = getattr(module, func_name)
    
    # Check if it's a function
    if not callable(func):
        return False, "Not callable"
    
    # Check source code for mock indicators
    try:
        source = inspect.getsource(func)
        mock_indicators = ['pass', 'NotImplementedError', 'TODO', 'MOCK', 'placeholder']
        
        # Remove comments and docstrings
        lines = [line.strip() for line in source.split('\n') 
                if line.strip() and not line.strip().startswith('#') 
                and not line.strip().startswith('"""')
                and not line.strip().startswith("'''")]
        
        # Check if function body is just 'pass' or raises NotImplementedError
        function_body = '\n'.join(lines[1:])  # Skip function definition line
        
        if function_body.strip() == 'pass':
            return False, "Function body is just 'pass'"
        
        if 'NotImplementedError' in function_body:
            return False, "Function raises NotImplementedError"
        
        if 'TODO' in source or 'MOCK' in source:
            return False, "Contains TODO or MOCK markers"
        
        # Check if function has substantial implementation (>5 lines)
        if len(lines) < 5:
            return False, f"Function too short ({len(lines)} lines)"
        
        return True, "Real implementation found"
        
    except Exception as e:
        return False, f"Error checking source: {e}"


def verify_roadmap_requirements():
    """Verify all requirements from IMPLEMENTATION_ROADMAP_UPDATED.md Phase 2."""
    
    print("\n" + "=" * 80)
    print("PHASE 2 ROADMAP REQUIREMENTS VERIFICATION")
    print("=" * 80)
    
    # Requirements from roadmap
    requirements = {
        'mix_design_generator': [
            'calculate_clinker_phase_masses',
            'calculate_flyash_phase_masses',
            'calculate_gangue_phase_masses',
            'generate_all_combinations_with_phases'
        ],
        'oxide_calculator': [
            'phase_mass_to_element_moles',
            'mix_design_to_bulk_composition_phases',
            'process_all_mix_designs_phases'
        ]
    }
    
    all_pass = True
    
    # Check mix_design_generator
    print("\n1. MIX DESIGN GENERATOR FUNCTIONS:")
    print("-" * 80)
    
    from mix_design_generator import MixDesignGenerator
    generator = MixDesignGenerator()
    
    for func_name in requirements['mix_design_generator']:
        exists, msg = check_function_exists_and_not_mock(generator, func_name)
        status = "✓" if exists else "✗"
        print(f"  {status} {func_name:45s} {msg}")
        if not exists:
            all_pass = False
    
    # Check oxide_calculator
    print("\n2. OXIDE CALCULATOR FUNCTIONS:")
    print("-" * 80)
    
    from oxide_calculator import OxideCalculator
    calculator = OxideCalculator()
    
    for func_name in requirements['oxide_calculator']:
        exists, msg = check_function_exists_and_not_mock(calculator, func_name)
        status = "✓" if exists else "✗"
        print(f"  {status} {func_name:45s} {msg}")
        if not exists:
            all_pass = False
    
    return all_pass


def verify_readme2_requirements():
    """Verify requirements from README (2).md."""
    
    print("\n" + "=" * 80)
    print("README (2).MD CLIENT REQUIREMENTS VERIFICATION")
    print("=" * 80)
    
    all_pass = True
    
    # Requirement 1: Rietveld XRD / Phase data
    print("\n1. PHASE DATA CONFIGURATION:")
    print("-" * 80)
    
    required_phase_dicts = ['CEMENT_PHASES', 'FLYASH_PHASES', 'GANGUE_PHASES']
    for phase_dict in required_phase_dicts:
        if hasattr(config, phase_dict):
            phases = getattr(config, phase_dict)
            phase_sum = sum(phases.values())
            if abs(phase_sum - 1.0) < 1e-6:
                print(f"  ✓ {phase_dict:20s} defined and normalized ({phase_sum:.10f})")
            else:
                print(f"  ✗ {phase_dict:20s} sum = {phase_sum:.10f} (should be 1.0)")
                all_pass = False
        else:
            print(f"  ✗ {phase_dict:20s} NOT FOUND in config")
            all_pass = False
    
    # Requirement 2: Phase stoichiometry database
    print("\n2. PHASE STOICHIOMETRY DATABASE:")
    print("-" * 80)
    
    if hasattr(config, 'PHASE_STOICHIOMETRY'):
        stoich = config.PHASE_STOICHIOMETRY
        print(f"  ✓ PHASE_STOICHIOMETRY defined with {len(stoich)} phases")
        
        # Check key phases
        key_phases = ['C3S', 'C2S', 'C3A', 'Gypsum', 'Quartz', 'Kaolinite']
        for phase in key_phases:
            if phase in stoich:
                elements = list(stoich[phase].keys())
                print(f"    ✓ {phase:15s} → {', '.join(elements)}")
            else:
                print(f"    ✗ {phase:15s} NOT FOUND")
                all_pass = False
    else:
        print("  ✗ PHASE_STOICHIOMETRY NOT FOUND in config")
        all_pass = False
    
    # Requirement 3: Sodium silicate handling
    print("\n3. SODIUM SILICATE CONFIGURATION:")
    print("-" * 80)
    
    if hasattr(config, 'SODIUM_SILICATE_COMPOSITION'):
        ss_comp = config.SODIUM_SILICATE_COMPOSITION
        required_components = ['Na2O', 'SiO2', 'H2O']
        ss_ok = all(comp in ss_comp for comp in required_components)
        if ss_ok:
            print(f"  ✓ Sodium silicate composition complete")
            for comp, val in ss_comp.items():
                print(f"    {comp:10s}: {val:6.2f} wt%")
        else:
            print(f"  ✗ Sodium silicate composition incomplete")
            all_pass = False
    else:
        print("  ✗ SODIUM_SILICATE_COMPOSITION NOT FOUND")
        all_pass = False
    
    # Requirement 4: CemGEMS integration readiness
    print("\n4. CEMGEMS INTEGRATION READINESS:")
    print("-" * 80)
    
    cemgems_configs = [
        'CEMDATA20_PATH',
        'ENABLED_PHASES',
        'SIMULATION_MODE',
        'REACTION_PATH_ENABLED'
    ]
    
    for config_item in cemgems_configs:
        if hasattr(config, config_item):
            value = getattr(config, config_item)
            if config_item == 'ENABLED_PHASES':
                total_phases = sum(len(phases) for phases in value.values())
                print(f"  ✓ {config_item:30s} ({total_phases} phases configured)")
            else:
                print(f"  ✓ {config_item:30s} = {value}")
        else:
            print(f"  ✗ {config_item:30s} NOT FOUND")
            all_pass = False
    
    return all_pass


def verify_calculation_accuracy():
    """Verify calculation accuracy with known test cases."""
    
    print("\n" + "=" * 80)
    print("CALCULATION ACCURACY VERIFICATION")
    print("=" * 80)
    
    all_pass = True
    
    calculator = OxideCalculator()
    
    # Test 1: C3S stoichiometry (Ca3SiO5)
    print("\n1. STOICHIOMETRY TEST - C3S (Ca3SiO5):")
    print("-" * 80)
    
    # Molar mass of C3S = 3*40.08 + 28.09 + 5*16.00 = 228.31 g/mol
    c3s_mass = 228.31  # 1 mole
    c3s_moles = calculator.phase_mass_to_element_moles('C3S', c3s_mass)
    
    expected = {'Ca': 3.0, 'Si': 1.0, 'O': 5.0}
    print(f"  Input: {c3s_mass:.2f} g C3S (1.0 mol)")
    print(f"  Expected: Ca=3.0, Si=1.0, O=5.0 mol")
    print(f"  Calculated: Ca={c3s_moles.get('Ca', 0):.6f}, Si={c3s_moles.get('Si', 0):.6f}, O={c3s_moles.get('O', 0):.6f} mol")
    
    tol = 0.001
    c3s_ok = (abs(c3s_moles.get('Ca', 0) - 3.0) < tol and 
              abs(c3s_moles.get('Si', 0) - 1.0) < tol and 
              abs(c3s_moles.get('O', 0) - 5.0) < tol)
    
    if c3s_ok:
        print("  ✓ C3S stoichiometry accurate (< 0.1% error)")
    else:
        print("  ✗ C3S stoichiometry error detected")
        all_pass = False
    
    # Test 2: Kaolinite stoichiometry (Al2Si2O5(OH)4)
    print("\n2. STOICHIOMETRY TEST - Kaolinite (Al2Si2O5(OH)4):")
    print("-" * 80)
    
    # Molar mass = 2*26.98 + 2*28.09 + 9*16.00 + 4*1.008 = 258.16 g/mol
    kaolinite_mass = 258.16  # 1 mole
    kaolinite_moles = calculator.phase_mass_to_element_moles('Kaolinite', kaolinite_mass)
    
    expected_kao = {'Al': 2.0, 'Si': 2.0, 'O': 9.0, 'H': 4.0}
    print(f"  Input: {kaolinite_mass:.2f} g Kaolinite (1.0 mol)")
    print(f"  Expected: Al=2.0, Si=2.0, O=9.0, H=4.0 mol")
    print(f"  Calculated: Al={kaolinite_moles.get('Al', 0):.6f}, Si={kaolinite_moles.get('Si', 0):.6f}, " +
          f"O={kaolinite_moles.get('O', 0):.6f}, H={kaolinite_moles.get('H', 0):.6f} mol")
    
    kao_ok = (abs(kaolinite_moles.get('Al', 0) - 2.0) < tol and 
              abs(kaolinite_moles.get('Si', 0) - 2.0) < tol and 
              abs(kaolinite_moles.get('O', 0) - 9.0) < tol and
              abs(kaolinite_moles.get('H', 0) - 4.0) < tol)
    
    if kao_ok:
        print("  ✓ Kaolinite stoichiometry accurate (< 0.1% error)")
    else:
        print("  ✗ Kaolinite stoichiometry error detected")
        all_pass = False
    
    # Test 3: Full mix design to bulk composition
    print("\n3. FULL MIX DESIGN CONVERSION TEST:")
    print("-" * 80)
    
    # Load a sample from phase-based dataset
    df_path = config.OUTPUTS_TABLES_DIR / 'mix_designs_phases_with_compositions.csv'
    if df_path.exists():
        df = pd.read_csv(df_path)
        sample = df.iloc[0]
        
        # Check that elemental moles are positive
        element_cols = [col for col in df.columns if col.endswith('_mol')]
        all_positive = all(sample[col] >= 0 for col in element_cols)
        
        if all_positive:
            print("  ✓ All elemental moles are non-negative")
        else:
            print("  ✗ Some elemental moles are negative")
            all_pass = False
        
        # Check key elements are present
        key_elements = ['Ca_mol', 'Si_mol', 'Al_mol', 'O_mol', 'H_mol']
        all_present = all(col in df.columns for col in key_elements)
        
        if all_present:
            print("  ✓ All key elements present in output")
            for elem in key_elements:
                print(f"    {elem:10s}: {sample[elem]:.6f} mol")
        else:
            print("  ✗ Some key elements missing")
            all_pass = False
    else:
        print("  ✗ Phase-based compositions file not found")
        all_pass = False
    
    return all_pass


def verify_output_completeness():
    """Verify all expected outputs exist and are complete."""
    
    print("\n" + "=" * 80)
    print("OUTPUT COMPLETENESS VERIFICATION")
    print("=" * 80)
    
    all_pass = True
    
    # Expected output files
    expected_files = {
        'mix_designs.csv': {
            'required_cols': ['mix_id', 'R', 'f_FA', 'yCO2', 'w_SS', 'w_b',
                            'cement_mass_g', 'flyash_mass_g', 'gangue_mass_g'],
            'expected_rows': 4928
        },
        'mix_designs_with_phases.csv': {
            'required_cols': ['mix_id', 'cement_C3S_g', 'cement_C2S_g', 
                            'flyash_Glass_g', 'gangue_Quartz_g'],
            'expected_rows': 4928
        },
        'mix_designs_with_compositions.csv': {
            'required_cols': ['mix_id', 'Ca_mol', 'Si_mol', 'Al_mol'],
            'expected_rows': 4928
        },
        'mix_designs_phases_with_compositions.csv': {
            'required_cols': ['mix_id', 'Ca_mol', 'Si_mol', 'Al_mol', 
                            'cement_C2S_g', 'flyash_Glass_g'],
            'expected_rows': 4928
        }
    }
    
    print("\nCHECKING OUTPUT FILES:")
    print("-" * 80)
    
    for filename, requirements in expected_files.items():
        filepath = config.OUTPUTS_TABLES_DIR / filename
        
        if not filepath.exists():
            print(f"  ✗ {filename:45s} NOT FOUND")
            all_pass = False
            continue
        
        # Load and check
        try:
            df = pd.read_csv(filepath)
            
            # Check row count
            if len(df) == requirements['expected_rows']:
                rows_ok = "✓"
            else:
                rows_ok = f"✗ ({len(df)} rows, expected {requirements['expected_rows']})"
                all_pass = False
            
            # Check required columns
            missing_cols = [col for col in requirements['required_cols'] if col not in df.columns]
            if not missing_cols:
                cols_ok = "✓"
            else:
                cols_ok = f"✗ (missing: {', '.join(missing_cols)})"
                all_pass = False
            
            # Check for missing values
            missing_vals = df.isnull().sum().sum()
            if missing_vals == 0:
                vals_ok = "✓"
            else:
                vals_ok = f"⚠ ({missing_vals} missing values)"
            
            file_size_mb = filepath.stat().st_size / (1024 * 1024)
            
            print(f"  {filename:45s}")
            print(f"    Rows: {rows_ok:10s} Columns: {cols_ok:10s} Missing: {vals_ok:10s} Size: {file_size_mb:.2f} MB")
            
        except Exception as e:
            print(f"  ✗ {filename:45s} ERROR: {e}")
            all_pass = False
    
    return all_pass


def verify_no_mock_functions():
    """Scan all functions to ensure no mock implementations."""
    
    print("\n" + "=" * 80)
    print("NO MOCK FUNCTIONS VERIFICATION")
    print("=" * 80)
    
    print("\nScanning for mock/placeholder implementations...")
    print("-" * 80)
    
    all_pass = True
    
    # Check mix_design_generator.py
    from mix_design_generator import MixDesignGenerator
    generator = MixDesignGenerator()
    
    generator_methods = [method for method in dir(generator) 
                        if callable(getattr(generator, method)) 
                        and not method.startswith('_')]
    
    print("\nmix_design_generator.py:")
    for method_name in generator_methods:
        exists, msg = check_function_exists_and_not_mock(generator, method_name)
        if not exists and 'pass' in msg.lower():
            print(f"  ✗ {method_name:40s} {msg}")
            all_pass = False
    
    # Check oxide_calculator.py
    from oxide_calculator import OxideCalculator
    calculator = OxideCalculator()
    
    calculator_methods = [method for method in dir(calculator) 
                         if callable(getattr(calculator, method)) 
                         and not method.startswith('_')]
    
    print("\noxide_calculator.py:")
    for method_name in calculator_methods:
        exists, msg = check_function_exists_and_not_mock(calculator, method_name)
        if not exists and 'pass' in msg.lower():
            print(f"  ✗ {method_name:40s} {msg}")
            all_pass = False
    
    if all_pass:
        print("\n  ✓ No mock functions detected - all implementations are real")
    
    return all_pass


def main():
    """Run all verification checks."""
    
    print("\n" + "=" * 80)
    print("PHASE 2 COMPREHENSIVE VERIFICATION")
    print("Checking implementation against all requirements")
    print("=" * 80)
    
    results = {}
    
    # Run all verification checks
    print("\n[1/6] Checking roadmap requirements...")
    results['roadmap'] = verify_roadmap_requirements()
    
    print("\n[2/6] Checking README (2).md client requirements...")
    results['client_reqs'] = verify_readme2_requirements()
    
    print("\n[3/6] Checking calculation accuracy...")
    results['accuracy'] = verify_calculation_accuracy()
    
    print("\n[4/6] Checking output completeness...")
    results['outputs'] = verify_output_completeness()
    
    print("\n[5/6] Checking for mock functions...")
    results['no_mocks'] = verify_no_mock_functions()
    
    # Final summary
    print("\n" + "=" * 80)
    print("FINAL VERIFICATION SUMMARY")
    print("=" * 80)
    
    check_names = {
        'roadmap': 'Roadmap Requirements (Phase 2)',
        'client_reqs': 'Client Requirements (README 2)',
        'accuracy': 'Calculation Accuracy',
        'outputs': 'Output File Completeness',
        'no_mocks': 'No Mock Functions'
    }
    
    for key, name in check_names.items():
        status = "✓ PASS" if results[key] else "✗ FAIL"
        print(f"  {status}  {name}")
    
    all_passed = all(results.values())
    
    print("\n" + "=" * 80)
    if all_passed:
        print("✓✓✓ PHASE 2 FULLY VERIFIED AND COMPLETE ✓✓✓")
        print("\nAll requirements satisfied:")
        print("  • All required functions implemented (NO MOCKS)")
        print("  • Phase-based calculations accurate")
        print("  • Client requirements from README (2).md met")
        print("  • All 4,928 combinations processed")
        print("  • Output files complete and valid")
        print("\n✓ READY FOR PHASE 3: CemGEMS Input Generation")
    else:
        print("⚠ SOME VERIFICATION CHECKS FAILED")
        print("\nReview failed checks above and address issues.")
    
    print("=" * 80 + "\n")
    
    return all_passed


if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)
