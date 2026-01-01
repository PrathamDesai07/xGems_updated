"""
Test Phase 2 Implementation
============================
Validates that phase-based mix design generation and oxide calculation
are working correctly with NO MOCK FUNCTIONS.

Tests:
1. Phase mass calculations are correct
2. Phase stoichiometry conversions are accurate
3. Mass balance is preserved
4. All 4,928 combinations processed successfully
5. Output files contain expected data

Author: Phase 2 Implementation Validation
Date: December 31, 2025
"""

import sys
from pathlib import Path

# Add scripts directory to path
SCRIPTS_DIR = Path(__file__).parent
if str(SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_DIR))

import numpy as np
import pandas as pd
import config
from mix_design_generator import MixDesignGenerator
from oxide_calculator import OxideCalculator


def test_phase_mass_calculations():
    """Test that phase masses sum correctly to total material mass."""
    
    print("\n" + "=" * 80)
    print("TEST 1: Phase Mass Calculations")
    print("=" * 80)
    
    generator = MixDesignGenerator()
    
    # Test cement phase masses
    cement_mass = 100.0  # g
    cement_phases = generator.calculate_clinker_phase_masses(cement_mass)
    
    print("\nCement phase breakdown (100g cement):")
    total_cement = 0.0
    for phase, mass in cement_phases.items():
        print(f"  {phase:12s}: {mass:8.4f} g")
        total_cement += mass
    
    print(f"  {'TOTAL':12s}: {total_cement:8.4f} g")
    
    if abs(total_cement - cement_mass) < 1e-6:
        print("  ✓ Mass balance OK")
    else:
        print(f"  ✗ Mass balance error: {abs(total_cement - cement_mass):.6f} g")
        return False
    
    # Test fly ash phase masses
    flyash_mass = 100.0  # g
    flyash_phases = generator.calculate_flyash_phase_masses(flyash_mass)
    
    print("\nFly ash phase breakdown (100g fly ash):")
    total_flyash = 0.0
    for phase, mass in flyash_phases.items():
        print(f"  {phase:12s}: {mass:8.4f} g")
        total_flyash += mass
    
    print(f"  {'TOTAL':12s}: {total_flyash:8.4f} g")
    
    if abs(total_flyash - flyash_mass) < 1e-6:
        print("  ✓ Mass balance OK")
    else:
        print(f"  ✗ Mass balance error: {abs(total_flyash - flyash_mass):.6f} g")
        return False
    
    # Test coal gangue phase masses
    gangue_mass = 100.0  # g
    gangue_phases = generator.calculate_gangue_phase_masses(gangue_mass)
    
    print("\nCoal gangue phase breakdown (100g gangue):")
    total_gangue = 0.0
    for phase, mass in gangue_phases.items():
        print(f"  {phase:12s}: {mass:8.4f} g")
        total_gangue += mass
    
    print(f"  {'TOTAL':12s}: {total_gangue:8.4f} g")
    
    if abs(total_gangue - gangue_mass) < 1e-6:
        print("  ✓ Mass balance OK")
    else:
        print(f"  ✗ Mass balance error: {abs(total_gangue - gangue_mass):.6f} g")
        return False
    
    print("\n✓ TEST 1 PASSED: All phase mass calculations correct")
    return True


def test_phase_stoichiometry_conversion():
    """Test that phase-to-element conversion is accurate."""
    
    print("\n" + "=" * 80)
    print("TEST 2: Phase Stoichiometry Conversion")
    print("=" * 80)
    
    calculator = OxideCalculator()
    
    # Test C3S: 3CaO·SiO2 = Ca3SiO5
    # Molar mass: 3*40.08 + 28.09 + 5*16.00 = 228.31 g/mol
    c3s_mass = 228.31  # 1 mole of C3S
    c3s_moles = calculator.phase_mass_to_element_moles('C3S', c3s_mass)
    
    print("\nC3S conversion (228.31g = 1 mol):")
    print(f"  Expected: Ca=3.0 mol, Si=1.0 mol, O=5.0 mol")
    print(f"  Calculated: Ca={c3s_moles.get('Ca', 0):.4f} mol, " +
          f"Si={c3s_moles.get('Si', 0):.4f} mol, " +
          f"O={c3s_moles.get('O', 0):.4f} mol")
    
    if (abs(c3s_moles.get('Ca', 0) - 3.0) < 0.01 and 
        abs(c3s_moles.get('Si', 0) - 1.0) < 0.01 and 
        abs(c3s_moles.get('O', 0) - 5.0) < 0.01):
        print("  ✓ C3S stoichiometry correct")
    else:
        print("  ✗ C3S stoichiometry error")
        return False
    
    # Test Gypsum: CaSO4·2H2O = CaSO6H4
    # Molar mass: 40.08 + 32.07 + 6*16.00 + 4*1.008 = 172.18 g/mol
    gypsum_mass = 172.18  # 1 mole of gypsum
    gypsum_moles = calculator.phase_mass_to_element_moles('Gypsum', gypsum_mass)
    
    print("\nGypsum conversion (172.18g = 1 mol):")
    print(f"  Expected: Ca=1.0 mol, S=1.0 mol, O=6.0 mol, H=4.0 mol")
    print(f"  Calculated: Ca={gypsum_moles.get('Ca', 0):.4f} mol, " +
          f"S={gypsum_moles.get('S', 0):.4f} mol, " +
          f"O={gypsum_moles.get('O', 0):.4f} mol, " +
          f"H={gypsum_moles.get('H', 0):.4f} mol")
    
    if (abs(gypsum_moles.get('Ca', 0) - 1.0) < 0.01 and 
        abs(gypsum_moles.get('S', 0) - 1.0) < 0.01 and 
        abs(gypsum_moles.get('O', 0) - 6.0) < 0.01 and
        abs(gypsum_moles.get('H', 0) - 4.0) < 0.01):
        print("  ✓ Gypsum stoichiometry correct")
    else:
        print("  ✗ Gypsum stoichiometry error")
        return False
    
    # Test Quartz: SiO2
    # Molar mass: 28.09 + 2*16.00 = 60.09 g/mol
    quartz_mass = 60.09  # 1 mole of quartz
    quartz_moles = calculator.phase_mass_to_element_moles('Quartz', quartz_mass)
    
    print("\nQuartz conversion (60.09g = 1 mol):")
    print(f"  Expected: Si=1.0 mol, O=2.0 mol")
    print(f"  Calculated: Si={quartz_moles.get('Si', 0):.4f} mol, " +
          f"O={quartz_moles.get('O', 0):.4f} mol")
    
    if (abs(quartz_moles.get('Si', 0) - 1.0) < 0.01 and 
        abs(quartz_moles.get('O', 0) - 2.0) < 0.01):
        print("  ✓ Quartz stoichiometry correct")
    else:
        print("  ✗ Quartz stoichiometry error")
        return False
    
    print("\n✓ TEST 2 PASSED: Phase stoichiometry conversions accurate")
    return True


def test_output_files_exist():
    """Test that all expected output files were created."""
    
    print("\n" + "=" * 80)
    print("TEST 3: Output File Validation")
    print("=" * 80)
    
    expected_files = [
        'mix_designs.csv',
        'mix_designs_with_phases.csv',
        'mix_designs_with_compositions.csv',
        'mix_designs_phases_with_compositions.csv'
    ]
    
    all_exist = True
    for filename in expected_files:
        filepath = config.OUTPUTS_TABLES_DIR / filename
        if filepath.exists():
            # Check file size
            size_mb = filepath.stat().st_size / (1024 * 1024)
            print(f"  ✓ {filename:45s} ({size_mb:.2f} MB)")
        else:
            print(f"  ✗ {filename:45s} (NOT FOUND)")
            all_exist = False
    
    if all_exist:
        print("\n✓ TEST 3 PASSED: All output files created")
        return True
    else:
        print("\n✗ TEST 3 FAILED: Some output files missing")
        return False


def test_data_completeness():
    """Test that all 4,928 combinations are in the datasets."""
    
    print("\n" + "=" * 80)
    print("TEST 4: Data Completeness")
    print("=" * 80)
    
    # Load phase-based dataset
    df_phases = pd.read_csv(config.OUTPUTS_TABLES_DIR / 'mix_designs_phases_with_compositions.csv')
    
    print(f"\n  Total rows: {len(df_phases)}")
    print(f"  Expected:   4928")
    
    if len(df_phases) == 4928:
        print("  ✓ Correct number of mix designs")
    else:
        print(f"  ✗ Wrong number of mix designs")
        return False
    
    # Check for missing values
    print(f"\n  Missing values:")
    missing = df_phases.isnull().sum().sum()
    print(f"    Total: {missing}")
    
    if missing == 0:
        print("  ✓ No missing values")
    else:
        print("  ⚠ Some missing values present")
    
    # Check key columns exist
    required_cols = ['mix_id', 'R', 'f_FA', 'yCO2', 'w_SS', 'w_b',
                     'Ca_mol', 'Si_mol', 'Al_mol', 'O_mol', 'H_mol']
    
    print(f"\n  Required columns:")
    all_present = True
    for col in required_cols:
        if col in df_phases.columns:
            print(f"    ✓ {col}")
        else:
            print(f"    ✗ {col} (MISSING)")
            all_present = False
    
    if all_present:
        print("\n✓ TEST 4 PASSED: Data complete")
        return True
    else:
        print("\n✗ TEST 4 FAILED: Some columns missing")
        return False


def test_phase_columns_present():
    """Test that phase-based dataset has all phase columns."""
    
    print("\n" + "=" * 80)
    print("TEST 5: Phase Columns Validation")
    print("=" * 80)
    
    # Load phase-based dataset
    df_phases = pd.read_csv(config.OUTPUTS_TABLES_DIR / 'mix_designs_with_phases.csv')
    
    # Expected cement phase columns
    cement_phase_cols = [f'cement_{phase}_g' for phase in config.CEMENT_PHASES.keys()]
    
    print("\n  Cement phase columns:")
    cement_ok = True
    for col in cement_phase_cols:
        if col in df_phases.columns:
            print(f"    ✓ {col}")
        else:
            print(f"    ✗ {col} (MISSING)")
            cement_ok = False
    
    # Expected fly ash phase columns
    flyash_phase_cols = [f'flyash_{phase}_g' for phase in config.FLYASH_PHASES.keys()]
    
    print("\n  Fly ash phase columns:")
    flyash_ok = True
    for col in flyash_phase_cols:
        if col in df_phases.columns:
            print(f"    ✓ {col}")
        else:
            print(f"    ✗ {col} (MISSING)")
            flyash_ok = False
    
    # Expected gangue phase columns
    gangue_phase_cols = [f'gangue_{phase}_g' for phase in config.GANGUE_PHASES.keys()]
    
    print("\n  Coal gangue phase columns:")
    gangue_ok = True
    for col in gangue_phase_cols:
        if col in df_phases.columns:
            print(f"    ✓ {col}")
        else:
            print(f"    ✗ {col} (MISSING)")
            gangue_ok = False
    
    if cement_ok and flyash_ok and gangue_ok:
        print("\n✓ TEST 5 PASSED: All phase columns present")
        return True
    else:
        print("\n✗ TEST 5 FAILED: Some phase columns missing")
        return False


def main():
    """Run all Phase 2 validation tests."""
    
    print("\n" + "=" * 80)
    print("PHASE 2 IMPLEMENTATION VALIDATION")
    print("Testing phase-based mix design and oxide calculation")
    print("=" * 80)
    
    tests = [
        ("Phase Mass Calculations", test_phase_mass_calculations),
        ("Phase Stoichiometry Conversion", test_phase_stoichiometry_conversion),
        ("Output Files Exist", test_output_files_exist),
        ("Data Completeness", test_data_completeness),
        ("Phase Columns Present", test_phase_columns_present),
    ]
    
    results = {}
    for test_name, test_func in tests:
        try:
            results[test_name] = test_func()
        except Exception as e:
            print(f"\n✗ TEST FAILED with exception: {e}")
            import traceback
            traceback.print_exc()
            results[test_name] = False
    
    # Summary
    print("\n" + "=" * 80)
    print("TEST SUMMARY")
    print("=" * 80)
    
    for test_name, passed in results.items():
        status = "✓ PASS" if passed else "✗ FAIL"
        print(f"  {status}  {test_name}")
    
    total_tests = len(results)
    passed_tests = sum(results.values())
    
    print(f"\nTotal: {passed_tests}/{total_tests} tests passed")
    
    if passed_tests == total_tests:
        print("\n" + "=" * 80)
        print("✓ ALL TESTS PASSED - PHASE 2 IMPLEMENTATION VALIDATED")
        print("=" * 80)
        print("\nPhase 2 is COMPLETE with NO MOCK FUNCTIONS:")
        print("  • Phase-based mix design generation working")
        print("  • Phase stoichiometry conversions accurate")
        print("  • All 4,928 combinations processed")
        print("  • Output files generated successfully")
        print("\nReady for Phase 3: CemGEMS Input Generation")
        print("=" * 80 + "\n")
        return True
    else:
        print("\n" + "=" * 80)
        print("⚠ SOME TESTS FAILED - REVIEW IMPLEMENTATION")
        print("=" * 80 + "\n")
        return False


if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)
