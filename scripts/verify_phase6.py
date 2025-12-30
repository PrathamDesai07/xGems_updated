#!/usr/bin/env python3
"""
Phase 6 Verification Script
Comprehensive validation of phase classification implementation
Verifies classification logic, consistency, and data integrity
NO mock functions - all real data validation
"""

import pandas as pd
import numpy as np
from pathlib import Path


def verify_file_existence():
    """Verify all expected output files exist"""
    print("="*70)
    print("VERIFICATION 1: FILE EXISTENCE")
    print("="*70)
    
    expected_files = [
        "outputs/tables/master_dataset_classified.csv",
        "outputs/tables/phase_statistics.csv",
        "scripts/phase_classifier.py"
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


def verify_classification_columns():
    """Verify all classification columns are present"""
    print("\n" + "="*70)
    print("VERIFICATION 2: CLASSIFICATION COLUMNS")
    print("="*70)
    
    df = pd.read_csv("outputs/tables/master_dataset_classified.csv")
    
    expected_cols = [
        'dominant_phase_by_mass',
        'dominant_phase_by_mole',
        'phase_assemblage',
        'carbonation_state',
        'csh_silica_class',
        'pH_regime',
        'phase_diagram_class'
    ]
    
    all_present = True
    for col in expected_cols:
        present = col in df.columns
        status = "✓" if present else "✗"
        print(f"{status} {col}")
        if not present:
            all_present = False
    
    if all_present:
        print(f"\n✓ All 7 classification columns present")
    else:
        print(f"\n✗ Some classification columns missing")
    
    print(f"\nTotal columns in classified dataset: {len(df.columns)}")
    print(f"Total rows: {len(df)}")
    
    return all_present


def verify_no_missing_values():
    """Verify no missing values in classification columns"""
    print("\n" + "="*70)
    print("VERIFICATION 3: MISSING VALUES")
    print("="*70)
    
    df = pd.read_csv("outputs/tables/master_dataset_classified.csv")
    
    classification_cols = [
        'dominant_phase_by_mass',
        'dominant_phase_by_mole',
        'phase_assemblage',
        'carbonation_state',
        'csh_silica_class',
        'pH_regime',
        'phase_diagram_class'
    ]
    
    no_missing = True
    for col in classification_cols:
        if col in df.columns:
            missing_count = df[col].isna().sum()
            status = "✓" if missing_count == 0 else "✗"
            print(f"{status} {col}: {missing_count} missing values")
            if missing_count > 0:
                no_missing = False
    
    if no_missing:
        print("\n✓ No missing values in classification columns")
    else:
        print("\n✗ Some classifications have missing values")
    
    return no_missing


def verify_dominant_phase_consistency():
    """Verify dominant phase classifications are consistent with actual data"""
    print("\n" + "="*70)
    print("VERIFICATION 4: DOMINANT PHASE CONSISTENCY")
    print("="*70)
    
    df = pd.read_csv("outputs/tables/master_dataset_classified.csv")
    
    # Check a sample of cases
    inconsistencies = 0
    sample_size = min(100, len(df))
    
    for idx in range(0, len(df), len(df) // sample_size):
        row = df.iloc[idx]
        
        # Get mass-based dominant phase from classification
        classified_phase = row['dominant_phase_by_mass']
        
        # Calculate actual dominant phase by mass
        phase_masses = {
            'C-S-H_1.0': row.get('C-S-H_1.0_kg', 0),
            'Calcite': row.get('Calcite_kg', 0),
            'Ettringite': row.get('Ettringite_kg', 0),
            'Hydrotalcite': row.get('Hydrotalcite_kg', 0),
            'Silica_gel': row.get('Silica_gel_kg', 0)
        }
        
        actual_dominant = max(phase_masses.items(), key=lambda x: x[1])[0]
        
        if classified_phase != actual_dominant:
            inconsistencies += 1
            if inconsistencies <= 3:  # Print first 3 inconsistencies
                print(f"  Inconsistency at row {idx}: classified={classified_phase}, actual={actual_dominant}")
    
    consistency_rate = (sample_size - inconsistencies) / sample_size * 100
    
    print(f"\nSampled {sample_size} cases")
    print(f"Inconsistencies found: {inconsistencies}")
    print(f"Consistency rate: {consistency_rate:.1f}%")
    
    consistent = inconsistencies == 0
    status = "✓" if consistent else "✗"
    print(f"\n{status} Dominant phase classification consistent: {consistent}")
    
    return consistent


def verify_carbonation_state_logic():
    """Verify carbonation state matches calcite amounts"""
    print("\n" + "="*70)
    print("VERIFICATION 5: CARBONATION STATE LOGIC")
    print("="*70)
    
    df = pd.read_csv("outputs/tables/master_dataset_classified.csv")
    
    # Check carbonation state boundaries
    carbonation_checks = {
        'Uncarbonated': (0.0, 0.0),
        'Low carbonation': (0.0, 0.005),
        'Medium carbonation': (0.005, 0.015),
        'High carbonation': (0.015, 0.025),
        'Very high carbonation': (0.025, 1.0)
    }
    
    total_errors = 0
    
    for state, (min_calcite, max_calcite) in carbonation_checks.items():
        subset = df[df['carbonation_state'] == state]
        
        if len(subset) > 0:
            calcite_amounts = subset['Calcite_mol']
            
            # Check if all values are in expected range
            if state == 'Uncarbonated':
                in_range = (calcite_amounts == 0.0).all()
            else:
                in_range = ((calcite_amounts >= min_calcite) & (calcite_amounts < max_calcite)).all()
            
            status = "✓" if in_range else "✗"
            print(f"{status} {state:.<30} {len(subset):>5} cases, "
                  f"calcite range: {calcite_amounts.min():.4f}-{calcite_amounts.max():.4f} mol")
            
            if not in_range:
                total_errors += 1
    
    logic_correct = total_errors == 0
    print(f"\n{'✓' if logic_correct else '✗'} Carbonation state logic correct: {logic_correct}")
    
    return logic_correct


def verify_assemblage_classification():
    """Verify phase assemblage classifications"""
    print("\n" + "="*70)
    print("VERIFICATION 6: PHASE ASSEMBLAGE CLASSIFICATION")
    print("="*70)
    
    df = pd.read_csv("outputs/tables/master_dataset_classified.csv")
    
    # Get unique assemblages
    unique_assemblages = df['phase_assemblage'].unique()
    
    print(f"Total unique assemblages: {len(unique_assemblages)}")
    
    # Count assemblages
    assemblage_counts = df['phase_assemblage'].value_counts()
    print(f"\nTop 5 most common assemblages:")
    for i, (assemblage, count) in enumerate(assemblage_counts.head(5).items(), 1):
        pct = count / len(df) * 100
        print(f"  {i}. {assemblage}")
        print(f"     {count} cases ({pct:.1f}%)")
    
    # Verify that assemblages contain valid phase names
    valid_phases = {'C-S-H_1.0', 'Calcite', 'Ettringite', 'Hydrotalcite', 'Silica_gel'}
    
    invalid_assemblages = 0
    for assemblage in unique_assemblages:
        phases_in_assemblage = set(assemblage.split(' + '))
        if assemblage != 'No major phases' and not phases_in_assemblage.issubset(valid_phases):
            invalid_assemblages += 1
            print(f"  Invalid assemblage: {assemblage}")
    
    assemblages_valid = invalid_assemblages == 0
    print(f"\n{'✓' if assemblages_valid else '✗'} All assemblages contain valid phases: {assemblages_valid}")
    
    return assemblages_valid


def verify_ph_regime_classification():
    """Verify pH regime classifications match actual pH values"""
    print("\n" + "="*70)
    print("VERIFICATION 7: pH REGIME CLASSIFICATION")
    print("="*70)
    
    df = pd.read_csv("outputs/tables/master_dataset_classified.csv")
    
    # Define pH regime boundaries
    ph_regimes = {
        'Neutral (pH<8.5)': (0, 8.5),
        'Slightly alkaline (8.5-9.0)': (8.5, 9.0),
        'Moderately alkaline (9.0-9.5)': (9.0, 9.5),
        'Alkaline (9.5-10.0)': (9.5, 10.0),
        'Highly alkaline (pH>10.0)': (10.0, 15.0)
    }
    
    total_errors = 0
    
    for regime, (min_pH, max_pH) in ph_regimes.items():
        subset = df[df['pH_regime'] == regime]
        
        if len(subset) > 0:
            pH_values = subset['pH']
            
            # Check if all values are in expected range
            in_range = ((pH_values >= min_pH) & (pH_values < max_pH)).all()
            
            status = "✓" if in_range else "✗"
            print(f"{status} {regime:.<40} {len(subset):>5} cases, "
                  f"pH range: {pH_values.min():.2f}-{pH_values.max():.2f}")
            
            if not in_range:
                total_errors += 1
    
    ph_logic_correct = total_errors == 0
    print(f"\n{'✓' if ph_logic_correct else '✗'} pH regime logic correct: {ph_logic_correct}")
    
    return ph_logic_correct


def verify_phase_diagram_classes():
    """Verify phase diagram classification distribution"""
    print("\n" + "="*70)
    print("VERIFICATION 8: PHASE DIAGRAM CLASSIFICATION")
    print("="*70)
    
    df = pd.read_csv("outputs/tables/master_dataset_classified.csv")
    
    # Get distribution
    diagram_classes = df['phase_diagram_class'].value_counts()
    
    print(f"Phase diagram classes:")
    for phase_class, count in diagram_classes.items():
        pct = count / len(df) * 100
        print(f"  {phase_class:.<40} {count:>5} ({pct:>5.1f}%)")
    
    # Check that we have reasonable distribution (no class dominates > 95%)
    max_pct = diagram_classes.max() / len(df) * 100
    well_distributed = max_pct < 95
    
    print(f"\nMaximum class percentage: {max_pct:.1f}%")
    print(f"{'✓' if well_distributed else '✗'} Classes well distributed (no single class >95%): {well_distributed}")
    
    return well_distributed


def verify_phase_statistics():
    """Verify phase statistics file"""
    print("\n" + "="*70)
    print("VERIFICATION 9: PHASE STATISTICS")
    print("="*70)
    
    stats_df = pd.read_csv("outputs/tables/phase_statistics.csv")
    
    print(f"Phase statistics table:")
    print(f"  Rows (phases): {len(stats_df)}")
    print(f"  Columns: {len(stats_df.columns)}")
    
    # Check for required columns
    required_cols = ['phase', 'present_count', 'present_percentage', 
                    'mean_mol', 'std_mol', 'min_mol', 'max_mol']
    
    all_cols_present = all(col in stats_df.columns for col in required_cols)
    
    print(f"\n{'✓' if all_cols_present else '✗'} All required columns present: {all_cols_present}")
    
    # Display statistics
    print(f"\nPhase statistics summary:")
    for _, row in stats_df.iterrows():
        print(f"  {row['phase']:.<20} present in {row['present_percentage']:>5.1f}% of cases, "
              f"mean={row['mean_mol']:.4f} mol")
    
    return all_cols_present


def verify_classification_correlations():
    """Verify correlations between different classification methods"""
    print("\n" + "="*70)
    print("VERIFICATION 10: CLASSIFICATION CORRELATIONS")
    print("="*70)
    
    df = pd.read_csv("outputs/tables/master_dataset_classified.csv")
    
    # Check correlation between carbonation state and CO2 concentration
    carbonation_order = {
        'Uncarbonated': 0,
        'Low carbonation': 1,
        'Medium carbonation': 2,
        'High carbonation': 3,
        'Very high carbonation': 4
    }
    
    df_corr = df.copy()
    df_corr['carbonation_numeric'] = df_corr['carbonation_state'].map(carbonation_order)
    
    correlation = df_corr['carbonation_numeric'].corr(df_corr['yCO2'])
    
    print(f"Correlation between carbonation state and yCO2: {correlation:.4f}")
    
    strong_correlation = correlation > 0.7
    print(f"{'✓' if strong_correlation else '✗'} Strong positive correlation (>0.7): {strong_correlation}")
    
    # Check consistency between dominant phase methods
    mass_vs_mole = (df['dominant_phase_by_mass'] == df['dominant_phase_by_mole']).sum()
    consistency_pct = mass_vs_mole / len(df) * 100
    
    print(f"\nDominant phase consistency:")
    print(f"  Mass-based = Mole-based: {mass_vs_mole}/{len(df)} ({consistency_pct:.1f}%)")
    
    return strong_correlation


def main():
    """Run all verifications"""
    print("\n" + "="*70)
    print("PHASE 6 COMPREHENSIVE VERIFICATION")
    print("="*70)
    
    results = {}
    
    # Run all verification tests
    results['file_existence'] = verify_file_existence()
    results['classification_columns'] = verify_classification_columns()
    results['no_missing_values'] = verify_no_missing_values()
    results['dominant_phase_consistency'] = verify_dominant_phase_consistency()
    results['carbonation_state_logic'] = verify_carbonation_state_logic()
    results['assemblage_classification'] = verify_assemblage_classification()
    results['ph_regime_classification'] = verify_ph_regime_classification()
    results['phase_diagram_classes'] = verify_phase_diagram_classes()
    results['phase_statistics'] = verify_phase_statistics()
    results['classification_correlations'] = verify_classification_correlations()
    
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
        print("PHASE 6 IS COMPLETE AND VERIFIED")
    else:
        print("✗✗✗ SOME VERIFICATIONS FAILED ✗✗✗")
        print("Please review failed tests above")
    print("="*70)
    
    return all_passed


if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
