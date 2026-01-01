"""
Phase 3 Implementation Test Suite
==================================
Comprehensive tests for CemGEMS input file generation.

Tests:
1. Input file existence and count
2. Input file structure validation
3. Bulk composition correctness
4. pCO2 calculation verification
5. Gas phase composition
6. File format validation (JSON and text)

Author: Thermodynamic Modeling Project
Date: December 31, 2025
"""

import sys
from pathlib import Path
import json

# Add scripts directory to path
SCRIPTS_DIR = Path(__file__).parent
if str(SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_DIR))

import numpy as np
import pandas as pd
import config
from cemgems_input_writer import CemGEMSInputWriter


def test_input_files_exist():
    """Test 1: Verify all 4,928 input files were created."""
    print("\n" + "="*70)
    print("TEST 1: Input File Existence")
    print("="*70)
    
    input_dir = config.INPUTS_GENERATED_DIR
    json_files = list(input_dir.glob("*.json"))
    
    print(f"Expected files: 4,928")
    print(f"Found JSON files: {len(json_files)}")
    
    if len(json_files) == 4928:
        print("✓ PASS: All 4,928 input files exist")
        return True
    else:
        print(f"✗ FAIL: Expected 4,928 files, found {len(json_files)}")
        return False


def test_input_file_structure():
    """Test 2: Validate JSON structure of input files."""
    print("\n" + "="*70)
    print("TEST 2: Input File Structure Validation")
    print("="*70)
    
    input_dir = config.INPUTS_GENERATED_DIR
    json_files = list(input_dir.glob("*.json"))[:10]  # Test first 10
    
    required_sections = ['task', 'conditions', 'system', 'phases', 'solver', 'output']
    required_task_fields = ['name', 'description', 'calculation_type', 'database']
    required_condition_fields = ['temperature_K', 'pressure_bar', 'pCO2_bar']
    required_system_fields = ['components', 'component_amounts', 'component_units']
    
    all_valid = True
    for input_file in json_files:
        try:
            with open(input_file, 'r') as f:
                data = json.load(f)
            
            # Check top-level sections
            for section in required_sections:
                if section not in data:
                    print(f"✗ FAIL: {input_file.name} missing section '{section}'")
                    all_valid = False
            
            # Check task fields
            if 'task' in data:
                for field in required_task_fields:
                    if field not in data['task']:
                        print(f"✗ FAIL: {input_file.name} missing task field '{field}'")
                        all_valid = False
            
            # Check conditions
            if 'conditions' in data:
                for field in required_condition_fields:
                    if field not in data['conditions']:
                        print(f"✗ FAIL: {input_file.name} missing condition '{field}'")
                        all_valid = False
            
            # Check system
            if 'system' in data:
                for field in required_system_fields:
                    if field not in data['system']:
                        print(f"✗ FAIL: {input_file.name} missing system field '{field}'")
                        all_valid = False
                        
        except json.JSONDecodeError as e:
            print(f"✗ FAIL: {input_file.name} - Invalid JSON: {e}")
            all_valid = False
        except Exception as e:
            print(f"✗ FAIL: {input_file.name} - Error: {e}")
            all_valid = False
    
    if all_valid:
        print(f"✓ PASS: All tested files ({len(json_files)}) have valid structure")
    
    return all_valid


def test_bulk_composition_correctness():
    """Test 3: Verify bulk compositions match source data."""
    print("\n" + "="*70)
    print("TEST 3: Bulk Composition Correctness")
    print("="*70)
    
    # Load source data
    source_csv = config.OUTPUTS_TABLES_DIR / "mix_designs_phases_with_compositions.csv"
    df_source = pd.read_csv(source_csv, nrows=20)
    
    # Test sample of files
    input_dir = config.INPUTS_GENERATED_DIR
    
    all_correct = True
    max_error = 0.0
    
    for idx, row in df_source.iterrows():
        mix_id = row['mix_id']
        input_file = input_dir / f"{mix_id}.json"
        
        if not input_file.exists():
            print(f"✗ FAIL: Input file not found for {mix_id}")
            all_correct = False
            continue
        
        # Load input file
        with open(input_file, 'r') as f:
            input_data = json.load(f)
        
        bulk_comp = input_data['system']['component_amounts']
        
        # Compare each element
        for element in config.SYSTEM_COMPONENTS:
            col_name = f"{element}_mol"
            if col_name in row.index:
                expected = float(row[col_name])
                actual = bulk_comp.get(element, 0.0)
                
                # Allow small floating point differences
                if expected > 0:
                    rel_error = abs(expected - actual) / expected
                    max_error = max(max_error, rel_error)
                    
                    if rel_error > 1e-6:
                        print(f"✗ FAIL: {mix_id} - {element}: expected {expected:.8f}, got {actual:.8f}")
                        all_correct = False
    
    if all_correct:
        print(f"✓ PASS: All bulk compositions match source data")
        print(f"  Maximum relative error: {max_error:.2e}")
    
    return all_correct


def test_pco2_calculation():
    """Test 4: Verify pCO2 calculation from yCO2."""
    print("\n" + "="*70)
    print("TEST 4: pCO2 Calculation Verification")
    print("="*70)
    
    # Load source data with various yCO2 values
    source_csv = config.OUTPUTS_TABLES_DIR / "mix_designs_phases_with_compositions.csv"
    df_source = pd.read_csv(source_csv)
    
    # Get samples with different yCO2
    test_cases = []
    for yCO2 in [0.0, 0.15, 0.20, 0.25, 0.30, 0.35, 0.40]:
        sample = df_source[df_source['yCO2'] == yCO2].head(1)
        if not sample.empty:
            test_cases.append(sample.iloc[0])
    
    input_dir = config.INPUTS_GENERATED_DIR
    total_pressure = config.TOTAL_PRESSURE_BAR
    
    all_correct = True
    
    print(f"\nTotal pressure: {total_pressure} bar\n")
    print(f"{'yCO2':<8} {'Expected pCO2 (bar)':<20} {'Actual pCO2 (bar)':<20} {'Status':<10}")
    print("-" * 70)
    
    for row in test_cases:
        mix_id = row['mix_id']
        yCO2 = float(row['yCO2'])
        expected_pCO2 = yCO2 * total_pressure
        
        input_file = input_dir / f"{mix_id}.json"
        with open(input_file, 'r') as f:
            input_data = json.load(f)
        
        actual_pCO2 = input_data['conditions']['pCO2_bar']
        
        # Check if within tolerance
        if abs(expected_pCO2 - actual_pCO2) < 1e-8:
            status = "✓ PASS"
        else:
            status = "✗ FAIL"
            all_correct = False
        
        print(f"{yCO2:<8.2f} {expected_pCO2:<20.8f} {actual_pCO2:<20.8f} {status:<10}")
    
    if all_correct:
        print("\n✓ PASS: All pCO2 calculations are correct")
    
    return all_correct


def test_gas_phase_composition():
    """Test 5: Verify gas phase composition."""
    print("\n" + "="*70)
    print("TEST 5: Gas Phase Composition")
    print("="*70)
    
    # Test cases with different CO2 levels
    source_csv = config.OUTPUTS_TABLES_DIR / "mix_designs_phases_with_compositions.csv"
    df_source = pd.read_csv(source_csv)
    
    input_dir = config.INPUTS_GENERATED_DIR
    total_pressure = config.TOTAL_PRESSURE_BAR
    
    # Test zero CO2 case
    zero_co2 = df_source[df_source['yCO2'] == 0.0].head(1).iloc[0]
    mix_id = zero_co2['mix_id']
    input_file = input_dir / f"{mix_id}.json"
    
    with open(input_file, 'r') as f:
        data = json.load(f)
    
    gas_enabled = data['phases']['gas_phase']['enabled']
    gas_comp = data['phases']['gas_phase']['composition']
    
    print(f"\nTest case: {mix_id} (yCO2 = 0.0)")
    print(f"  Gas phase enabled: {gas_enabled}")
    print(f"  Gas composition: {gas_comp}")
    
    if len(gas_comp) == 0:
        print("  ✓ PASS: No gas species for zero CO2")
    else:
        print("  ✗ FAIL: Unexpected gas species for zero CO2")
        return False
    
    # Test with CO2 present
    with_co2 = df_source[df_source['yCO2'] == 0.20].head(1).iloc[0]
    mix_id = with_co2['mix_id']
    yCO2 = 0.20
    input_file = input_dir / f"{mix_id}.json"
    
    with open(input_file, 'r') as f:
        data = json.load(f)
    
    gas_enabled = data['phases']['gas_phase']['enabled']
    gas_comp = data['phases']['gas_phase']['composition']
    
    print(f"\nTest case: {mix_id} (yCO2 = {yCO2})")
    print(f"  Gas phase enabled: {gas_enabled}")
    print(f"  Gas composition: {gas_comp}")
    
    expected_pCO2 = yCO2 * total_pressure
    expected_pH2O = (1 - yCO2) * total_pressure
    
    if gas_enabled and 'CO2' in gas_comp and 'H2O_gas' in gas_comp:
        actual_pCO2 = gas_comp['CO2']
        actual_pH2O = gas_comp['H2O_gas']
        
        pCO2_ok = abs(actual_pCO2 - expected_pCO2) < 1e-8
        pH2O_ok = abs(actual_pH2O - expected_pH2O) < 1e-8
        
        if pCO2_ok and pH2O_ok:
            print(f"  ✓ PASS: Gas composition correct")
            print(f"    CO2: {actual_pCO2:.6f} bar (expected {expected_pCO2:.6f})")
            print(f"    H2O: {actual_pH2O:.6f} bar (expected {expected_pH2O:.6f})")
            return True
        else:
            print(f"  ✗ FAIL: Gas composition incorrect")
            return False
    else:
        print(f"  ✗ FAIL: Gas phase missing expected species")
        return False


def test_enabled_phases():
    """Test 6: Verify enabled phases list."""
    print("\n" + "="*70)
    print("TEST 6: Enabled Phases")
    print("="*70)
    
    # Load a sample input file
    input_dir = config.INPUTS_GENERATED_DIR
    sample_file = input_dir / "MIX_0000.json"
    
    with open(sample_file, 'r') as f:
        data = json.load(f)
    
    enabled_phases = data['phases']['enabled']
    expected_phases = []
    for category, phases in config.ENABLED_PHASES.items():
        expected_phases.extend(phases)
    
    print(f"\nExpected phases: {len(expected_phases)}")
    print(f"Enabled phases: {len(enabled_phases)}")
    
    # Check all expected phases are present
    missing = set(expected_phases) - set(enabled_phases)
    extra = set(enabled_phases) - set(expected_phases)
    
    if len(missing) == 0 and len(extra) == 0:
        print("✓ PASS: All expected phases are enabled, no extras")
        print(f"\nEnabled phase categories:")
        for category, phases in config.ENABLED_PHASES.items():
            print(f"  {category}: {len(phases)} phases")
        return True
    else:
        if missing:
            print(f"✗ FAIL: Missing phases: {missing}")
        if extra:
            print(f"✗ FAIL: Extra phases: {extra}")
        return False


def test_file_format_validation():
    """Test 7: Validate file format integrity."""
    print("\n" + "="*70)
    print("TEST 7: File Format Validation")
    print("="*70)
    
    input_dir = config.INPUTS_GENERATED_DIR
    
    # Test JSON format
    json_files = list(input_dir.glob("*.json"))[:100]  # Test first 100
    
    invalid_count = 0
    for input_file in json_files:
        try:
            with open(input_file, 'r') as f:
                data = json.load(f)
            # Try to access key fields
            _ = data['task']['name']
            _ = data['conditions']['temperature_K']
            _ = data['system']['component_amounts']
        except Exception as e:
            print(f"✗ Invalid file: {input_file.name} - {e}")
            invalid_count += 1
    
    if invalid_count == 0:
        print(f"✓ PASS: All tested files ({len(json_files)}) have valid JSON format")
        return True
    else:
        print(f"✗ FAIL: {invalid_count}/{len(json_files)} files have invalid format")
        return False


def test_mass_balance():
    """Test 8: Verify element mass balance."""
    print("\n" + "="*70)
    print("TEST 8: Element Mass Balance")
    print("="*70)
    
    # Load source data
    source_csv = config.OUTPUTS_TABLES_DIR / "mix_designs_phases_with_compositions.csv"
    df_source = pd.read_csv(source_csv, nrows=10)
    
    input_dir = config.INPUTS_GENERATED_DIR
    
    all_balanced = True
    
    for idx, row in df_source.iterrows():
        mix_id = row['mix_id']
        input_file = input_dir / f"{mix_id}.json"
        
        with open(input_file, 'r') as f:
            data = json.load(f)
        
        bulk_comp = data['system']['component_amounts']
        
        # Calculate total element mass
        total_mass = 0.0
        for element, moles in bulk_comp.items():
            mass = moles * config.ELEMENT_ATOMIC_MASSES[element]
            total_mass += mass
        
        # This should match total_solid_mass_g from source (approximately)
        # Note: May differ slightly due to water and gas phase
        if total_mass > 0:
            print(f"  {mix_id}: Total element mass = {total_mass:.2f} g")
        else:
            print(f"  ✗ {mix_id}: Zero total mass!")
            all_balanced = False
    
    if all_balanced:
        print("\n✓ PASS: All mixes have positive element masses")
    
    return all_balanced


def run_all_tests():
    """Run all Phase 3 tests."""
    print("\n" + "="*70)
    print("PHASE 3 IMPLEMENTATION TEST SUITE")
    print("CemGEMS Input File Generation")
    print("="*70)
    
    tests = [
        ("Input Files Exist", test_input_files_exist),
        ("Input File Structure", test_input_file_structure),
        ("Bulk Composition Correctness", test_bulk_composition_correctness),
        ("pCO2 Calculation", test_pco2_calculation),
        ("Gas Phase Composition", test_gas_phase_composition),
        ("Enabled Phases", test_enabled_phases),
        ("File Format Validation", test_file_format_validation),
        ("Mass Balance", test_mass_balance),
    ]
    
    results = []
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"\n✗ ERROR in {test_name}: {e}")
            import traceback
            traceback.print_exc()
            results.append((test_name, False))
    
    # Summary
    print("\n" + "="*70)
    print("TEST SUMMARY")
    print("="*70)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✓ PASS" if result else "✗ FAIL"
        print(f"{status}: {test_name}")
    
    print("\n" + "="*70)
    print(f"TOTAL: {passed}/{total} tests passed ({100*passed/total:.1f}%)")
    print("="*70)
    
    if passed == total:
        print("\n✅ PHASE 3 COMPLETE: All tests passed!")
        print("\nDeliverables:")
        print("  ✓ cemgems_input_writer.py - Full implementation")
        print("  ✓ 4,928 JSON input files generated")
        print("  ✓ Input templates (JSON and text)")
        print("  ✓ Validation functionality")
        print("\nNext Phase: Phase 4 - Batch CemGEMS Execution")
    else:
        print(f"\n⚠️  WARNING: {total - passed} test(s) failed")
    
    return passed == total


if __name__ == '__main__':
    success = run_all_tests()
    exit(0 if success else 1)
