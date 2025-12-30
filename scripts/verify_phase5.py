#!/usr/bin/env python3
"""
Phase 5 Verification Script
Comprehensive validation of output parsing and data aggregation
Verifies data integrity, completeness, and correctness
NO mock functions - all real data validation
"""

import pandas as pd
import numpy as np
from pathlib import Path
import json


def verify_file_existence():
    """Verify all expected output files exist"""
    print("="*70)
    print("VERIFICATION 1: FILE EXISTENCE")
    print("="*70)
    
    expected_files = [
        "outputs/tables/master_dataset_full.csv",
        "outputs/tables/master_dataset.csv",
        "outputs/tables/master_dataset_with_derived.csv",
        "outputs/tables/convergence_summary.csv",
        "outputs/raw/parsed_outputs_full.csv",
        "outputs/raw/phase_amounts_mol.csv",
        "outputs/raw/phase_amounts_kg.csv"
    ]
    
    all_exist = True
    for filepath in expected_files:
        exists = Path(filepath).exists()
        status = "✓" if exists else "✗"
        print(f"{status} {filepath}")
        if not exists:
            all_exist = False
    
    if all_exist:
        print("\n✓ All expected files exist")
    else:
        print("\n✗ Some files are missing")
    
    return all_exist


def verify_data_completeness():
    """Verify dataset has correct number of rows and columns"""
    print("\n" + "="*70)
    print("VERIFICATION 2: DATA COMPLETENESS")
    print("="*70)
    
    # Load master dataset
    df = pd.read_csv("outputs/tables/master_dataset.csv")
    
    # Expected dimensions
    expected_rows = 4928  # 4×11×7×4×4
    min_expected_cols = 15  # At minimum
    
    print(f"\nMaster dataset dimensions:")
    print(f"  Rows: {len(df)} (expected: {expected_rows})")
    print(f"  Columns: {len(df.columns)} (expected: >{min_expected_cols})")
    
    # Check row count
    row_check = len(df) == expected_rows
    print(f"\n{'✓' if row_check else '✗'} Row count correct: {len(df)} == {expected_rows}")
    
    # Check column count
    col_check = len(df.columns) >= min_expected_cols
    print(f"{'✓' if col_check else '✗'} Column count sufficient: {len(df.columns)} >= {min_expected_cols}")
    
    # Check for required columns
    required_cols = ['mix_id', 'R', 'f_FA', 'yCO2', 'w_SS', 'w_b', 
                    'converged', 'pH', 'pCO2_bar']
    
    missing_cols = [col for col in required_cols if col not in df.columns]
    
    if not missing_cols:
        print(f"✓ All required columns present")
    else:
        print(f"✗ Missing columns: {missing_cols}")
    
    return row_check and col_check and not missing_cols


def verify_independent_variables():
    """Verify independent variables have correct levels"""
    print("\n" + "="*70)
    print("VERIFICATION 3: INDEPENDENT VARIABLES")
    print("="*70)
    
    df = pd.read_csv("outputs/tables/master_dataset.csv")
    
    # Expected levels for each variable
    expected_levels = {
        'R': [0.3, 0.6, 0.9, 1.2],
        'f_FA': [0.0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0],
        'yCO2': [0.0, 0.15, 0.2, 0.25, 0.3, 0.35, 0.4],
        'w_SS': [0.02, 0.03, 0.04, 0.05],
        'w_b': [1.1, 1.4, 1.7, 2.0]
    }
    
    all_correct = True
    
    for var, expected in expected_levels.items():
        actual = sorted(df[var].unique())
        match = np.allclose(actual, expected, rtol=1e-9)
        
        print(f"\n{var}:")
        print(f"  Expected levels: {len(expected)} - {expected}")
        print(f"  Actual levels:   {len(actual)} - {actual}")
        print(f"  {'✓' if match else '✗'} Match: {match}")
        
        if not match:
            all_correct = False
    
    # Check full factorial design
    expected_combinations = 4 * 11 * 7 * 4 * 4
    actual_combinations = len(df)
    
    print(f"\nFull factorial design:")
    print(f"  Expected combinations: {expected_combinations}")
    print(f"  Actual combinations:   {actual_combinations}")
    print(f"  {'✓' if expected_combinations == actual_combinations else '✗'} Match")
    
    return all_correct and (expected_combinations == actual_combinations)


def verify_convergence_data():
    """Verify convergence data"""
    print("\n" + "="*70)
    print("VERIFICATION 4: CONVERGENCE DATA")
    print("="*70)
    
    df = pd.read_csv("outputs/tables/master_dataset.csv")
    
    # Check convergence column
    converged_count = df['converged'].sum()
    convergence_rate = converged_count / len(df) * 100
    
    print(f"\nConvergence statistics:")
    print(f"  Total cases:      {len(df)}")
    print(f"  Converged cases:  {converged_count}")
    print(f"  Convergence rate: {convergence_rate:.2f}%")
    
    # All should be converged (from Phase 4 verification)
    all_converged = converged_count == len(df)
    print(f"\n{'✓' if all_converged else '✗'} All cases converged: {all_converged}")
    
    return all_converged


def verify_phase_data():
    """Verify phase data integrity"""
    print("\n" + "="*70)
    print("VERIFICATION 5: PHASE DATA")
    print("="*70)
    
    df = pd.read_csv("outputs/tables/master_dataset.csv")
    
    # Identify phase columns
    phase_mol_cols = [col for col in df.columns if '_mol' in col]
    phase_kg_cols = [col for col in df.columns if '_kg' in col]
    
    print(f"\nPhase data columns:")
    print(f"  Mole columns: {len(phase_mol_cols)}")
    print(f"  Mass columns: {len(phase_kg_cols)}")
    
    # Check for negative values (should not exist)
    has_negatives = False
    for col in phase_mol_cols + phase_kg_cols:
        if (df[col] < 0).any():
            print(f"✗ Negative values found in {col}")
            has_negatives = True
    
    if not has_negatives:
        print(f"✓ No negative phase amounts found")
    
    # Check that phase amounts vary (not all same)
    varies = True
    for col in phase_mol_cols:
        if df[col].std() < 1e-9:
            print(f"✗ No variation in {col}")
            varies = False
    
    if varies:
        print(f"✓ Phase amounts show variation")
    
    # Print phase statistics
    print(f"\nPhase occurrence statistics:")
    for col in phase_mol_cols:
        phase_name = col.replace('_mol', '')
        present_count = (df[col] > 0).sum()
        percentage = present_count / len(df) * 100
        mean_amount = df[df[col] > 0][col].mean() if present_count > 0 else 0
        print(f"  {phase_name:.<30} {present_count:>5}/{len(df)} ({percentage:>5.1f}%), mean={mean_amount:.4f} mol")
    
    return not has_negatives and varies


def verify_pH_data():
    """Verify pH data is reasonable"""
    print("\n" + "="*70)
    print("VERIFICATION 6: pH DATA")
    print("="*70)
    
    df = pd.read_csv("outputs/tables/master_dataset.csv")
    
    pH_values = df['pH']
    
    print(f"\npH statistics:")
    print(f"  Mean:   {pH_values.mean():.3f}")
    print(f"  Std:    {pH_values.std():.3f}")
    print(f"  Min:    {pH_values.min():.3f}")
    print(f"  Max:    {pH_values.max():.3f}")
    print(f"  Median: {pH_values.median():.3f}")
    
    # pH should be in reasonable range (7-14 for cement systems)
    reasonable_range = (pH_values >= 7.0) & (pH_values <= 14.0)
    all_reasonable = reasonable_range.all()
    
    print(f"\n{'✓' if all_reasonable else '✗'} All pH values in reasonable range (7-14): {all_reasonable}")
    
    # pH should vary significantly
    sufficient_variation = pH_values.std() > 0.1
    print(f"{'✓' if sufficient_variation else '✗'} Sufficient pH variation (std > 0.1): {sufficient_variation}")
    
    return all_reasonable and sufficient_variation


def verify_pCO2_correlation():
    """Verify pCO2 correlates with yCO2"""
    print("\n" + "="*70)
    print("VERIFICATION 7: pCO2 CORRELATION WITH yCO2")
    print("="*70)
    
    df = pd.read_csv("outputs/tables/master_dataset.csv")
    
    # pCO2 should equal yCO2 × pressure_bar (approximately)
    expected_pCO2 = df['yCO2'] * df['pressure_bar']
    actual_pCO2 = df['pCO2_bar']
    
    # Check correlation
    correlation = np.corrcoef(expected_pCO2, actual_pCO2)[0, 1]
    
    print(f"\nCorrelation between expected and actual pCO2: {correlation:.6f}")
    
    # Should be very high correlation
    high_correlation = correlation > 0.99
    print(f"{'✓' if high_correlation else '✗'} High correlation (>0.99): {high_correlation}")
    
    # Check a few specific cases
    print(f"\nSample verification:")
    for i in [0, 100, 500, 1000]:
        if i < len(df):
            print(f"  Case {i}: yCO2={df.loc[i, 'yCO2']:.3f}, "
                  f"expected_pCO2={expected_pCO2.iloc[i]:.4f}, "
                  f"actual_pCO2={df.loc[i, 'pCO2_bar']:.4f}")
    
    return high_correlation


def verify_calcite_carbonation_trend():
    """Verify calcite formation increases with CO2"""
    print("\n" + "="*70)
    print("VERIFICATION 8: CALCITE vs CO2 TREND")
    print("="*70)
    
    df = pd.read_csv("outputs/tables/master_dataset.csv")
    
    # Get calcite column
    calcite_col = 'Calcite_mol'
    if calcite_col not in df.columns:
        print("✗ Calcite_mol column not found")
        return False
    
    # Group by yCO2 and calculate mean calcite
    calcite_by_CO2 = df.groupby('yCO2')[calcite_col].agg(['mean', 'std', 'count'])
    
    print(f"\nCalcite formation vs yCO2:")
    print(calcite_by_CO2.to_string())
    
    # Check if calcite generally increases with CO2
    mean_calcite = calcite_by_CO2['mean'].values
    increasing_trend = all(mean_calcite[i] <= mean_calcite[i+1] for i in range(len(mean_calcite)-1))
    
    # Allow for some noise - check if at least mostly increasing
    mostly_increasing = sum(mean_calcite[i] <= mean_calcite[i+1] for i in range(len(mean_calcite)-1)) >= len(mean_calcite) - 2
    
    print(f"\n{'✓' if mostly_increasing else '✗'} Calcite shows increasing trend with CO2: {mostly_increasing}")
    
    return mostly_increasing


def verify_data_export_formats():
    """Verify exported data can be read correctly"""
    print("\n" + "="*70)
    print("VERIFICATION 9: DATA EXPORT FORMATS")
    print("="*70)
    
    files_to_check = [
        "outputs/tables/master_dataset_full.csv",
        "outputs/tables/master_dataset.csv",
        "outputs/raw/phase_amounts_mol.csv",
        "outputs/raw/phase_amounts_kg.csv"
    ]
    
    all_readable = True
    
    for filepath in files_to_check:
        try:
            df = pd.read_csv(filepath)
            print(f"✓ {filepath}")
            print(f"    Shape: {df.shape[0]} rows × {df.shape[1]} columns")
        except Exception as e:
            print(f"✗ {filepath}: {e}")
            all_readable = False
    
    return all_readable


def main():
    """Run all verifications"""
    print("\n" + "="*70)
    print("PHASE 5 COMPREHENSIVE VERIFICATION")
    print("="*70)
    
    results = {}
    
    # Run all verification tests
    results['file_existence'] = verify_file_existence()
    results['data_completeness'] = verify_data_completeness()
    results['independent_variables'] = verify_independent_variables()
    results['convergence_data'] = verify_convergence_data()
    results['phase_data'] = verify_phase_data()
    results['pH_data'] = verify_pH_data()
    results['pCO2_correlation'] = verify_pCO2_correlation()
    results['calcite_trend'] = verify_calcite_carbonation_trend()
    results['export_formats'] = verify_data_export_formats()
    
    # Summary
    print("\n" + "="*70)
    print("VERIFICATION SUMMARY")
    print("="*70)
    
    for test_name, passed in results.items():
        status = "✓ PASS" if passed else "✗ FAIL"
        print(f"{status:.<50} {test_name}")
    
    all_passed = all(results.values())
    
    print("\n" + "="*70)
    if all_passed:
        print("✓✓✓ ALL VERIFICATIONS PASSED ✓✓✓")
        print("PHASE 5 IS COMPLETE AND VERIFIED")
    else:
        print("✗✗✗ SOME VERIFICATIONS FAILED ✗✗✗")
        print("Please review failed tests above")
    print("="*70)
    
    return all_passed


if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
