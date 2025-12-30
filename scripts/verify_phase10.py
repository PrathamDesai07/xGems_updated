#!/usr/bin/env python3
"""
PHASE 10 VERIFICATION: REACTION-PATH SIMULATIONS
=================================================
Comprehensive verification of Phase 10 deliverables.

This script verifies:
1. All reaction path figures generated
2. All reaction path data CSV files generated
3. Representative mixes selected correctly
4. Phase evolution data quality
5. pH evolution data quality
6. Consistency with requirements (section 4.4)

NO mock functions - all verification uses real generated outputs.
"""

import sys
import pandas as pd
import numpy as np
from pathlib import Path
import matplotlib.pyplot as plt
import matplotlib.image as mpimg

# Add project root to path
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from config import OUTPUTS_FIGURES_DIR, OUTPUTS_TABLES_DIR


def verify_reaction_path_figures():
    """
    Verify all required reaction path figures are generated.
    
    Returns:
        bool: True if all figures exist, False otherwise
    """
    print("="*70)
    print("1. VERIFYING REACTION PATH FIGURES")
    print("="*70)
    
    reaction_paths_dir = OUTPUTS_FIGURES_DIR / "reaction_paths"
    
    if not reaction_paths_dir.exists():
        print("ERROR: Reaction paths directory does not exist!")
        return False
    
    # Expected figures
    expected_figures = [
        # Individual paths with pH
        "reaction_path_R0.6_fFA0.1_pH.png",
        "reaction_path_R0.6_fFA0.5_pH.png",
        "reaction_path_R0.6_fFA0.9_pH.png",
        # Individual paths (phases only)
        "reaction_path_R0.6_fFA0.1_phases.png",
        "reaction_path_R0.6_fFA0.5_phases.png",
        "reaction_path_R0.6_fFA0.9_phases.png",
        # Comparison
        "reaction_paths_comparison_R0.6.png"
    ]
    
    all_present = True
    missing_figures = []
    
    for filename in expected_figures:
        fig_path = reaction_paths_dir / filename
        
        if fig_path.exists():
            # Check file size
            file_size = fig_path.stat().st_size
            print(f"  ✓ {filename} ({file_size/1024:.1f} KB)")
            
            if file_size < 10000:  # Less than 10 KB is suspicious
                print(f"    WARNING: File size is very small!")
        else:
            print(f"  ✗ {filename} - MISSING")
            missing_figures.append(filename)
            all_present = False
    
    print()
    print(f"Figure verification: {len(expected_figures) - len(missing_figures)}/{len(expected_figures)} present")
    
    if all_present:
        print("✓ All reaction path figures generated successfully")
    else:
        print(f"✗ Missing {len(missing_figures)} figures:")
        for fig in missing_figures:
            print(f"    - {fig}")
    
    return all_present


def verify_reaction_path_data():
    """
    Verify reaction path data CSV files and their contents.
    
    Returns:
        bool: True if all data files are valid, False otherwise
    """
    print()
    print("="*70)
    print("2. VERIFYING REACTION PATH DATA FILES")
    print("="*70)
    
    data_dir = OUTPUTS_TABLES_DIR / "reaction_paths"
    
    if not data_dir.exists():
        print("ERROR: Reaction paths data directory does not exist!")
        return False
    
    # Expected data files
    expected_files = [
        "reaction_path_data_R0.6_fFA0.1.csv",
        "reaction_path_data_R0.6_fFA0.5.csv",
        "reaction_path_data_R0.6_fFA0.9.csv"
    ]
    
    all_valid = True
    
    for filename in expected_files:
        file_path = data_dir / filename
        
        if not file_path.exists():
            print(f"  ✗ {filename} - MISSING")
            all_valid = False
            continue
        
        # Load and verify data
        try:
            df = pd.read_csv(file_path)
            
            # Expected columns
            required_cols = ['R', 'f_FA', 'yCO2', 'w_SS', 'w_b', 'pH',
                           'C-S-H_1.0_kg', 'Calcite_kg', 'Silica_gel_kg',
                           'Ettringite_kg', 'Hydrotalcite_kg']
            
            missing_cols = [col for col in required_cols if col not in df.columns]
            
            if missing_cols:
                print(f"  ✗ {filename} - Missing columns: {missing_cols}")
                all_valid = False
                continue
            
            # Check data quality
            n_rows = len(df)
            yCO2_range = (df['yCO2'].min(), df['yCO2'].max())
            pH_range = (df['pH'].min(), df['pH'].max())
            
            print(f"  ✓ {filename}")
            print(f"      Rows: {n_rows}")
            print(f"      yCO2 range: {yCO2_range[0]:.2f} → {yCO2_range[1]:.2f}")
            print(f"      pH range: {pH_range[0]:.2f} → {pH_range[1]:.2f}")
            
            # Check for expected CO₂ steps (should be 7: 0%, 15%, 20%, 25%, 30%, 35%, 40%)
            if n_rows != 7:
                print(f"      WARNING: Expected 7 CO₂ steps, found {n_rows}")
                all_valid = False
            
            # Check pH evolution (should decrease with carbonation)
            if df['pH'].iloc[-1] >= df['pH'].iloc[0]:
                print(f"      WARNING: pH should decrease with carbonation!")
                all_valid = False
            
        except Exception as e:
            print(f"  ✗ {filename} - Error reading: {e}")
            all_valid = False
    
    print()
    if all_valid:
        print("✓ All reaction path data files valid")
    else:
        print("✗ Some data files have issues")
    
    return all_valid


def verify_phase_evolution():
    """
    Verify phase evolution patterns are chemically reasonable.
    
    Returns:
        bool: True if phase evolution is reasonable, False otherwise
    """
    print()
    print("="*70)
    print("3. VERIFYING PHASE EVOLUTION PATTERNS")
    print("="*70)
    
    data_dir = OUTPUTS_TABLES_DIR / "reaction_paths"
    
    all_reasonable = True
    
    for f_FA in [0.1, 0.5, 0.9]:
        filename = f"reaction_path_data_R0.6_fFA{f_FA}.csv"
        file_path = data_dir / filename
        
        if not file_path.exists():
            continue
        
        df = pd.read_csv(file_path)
        
        print(f"\nf_FA = {f_FA}:")
        
        # Check Calcite evolution (should increase with carbonation)
        calcite_initial = df['Calcite_kg'].iloc[0]
        calcite_final = df['Calcite_kg'].iloc[-1]
        calcite_change = calcite_final - calcite_initial
        
        print(f"  Calcite: {calcite_initial:.4f} → {calcite_final:.4f} kg (Δ = {calcite_change:+.4f})")
        
        if calcite_change < 0:
            print(f"    ✗ WARNING: Calcite should increase with CO₂ addition!")
            all_reasonable = False
        else:
            print(f"    ✓ Calcite increases with carbonation (expected)")
        
        # Check C-S-H evolution (may decrease due to decalcification)
        csh_initial = df['C-S-H_1.0_kg'].iloc[0]
        csh_final = df['C-S-H_1.0_kg'].iloc[-1]
        csh_change = csh_final - csh_initial
        
        print(f"  C-S-H: {csh_initial:.4f} → {csh_final:.4f} kg (Δ = {csh_change:+.4f})")
        
        if csh_change > 0:
            print(f"    ? C-S-H increased (unusual but may occur)")
        else:
            print(f"    ✓ C-S-H decreased or stable (typical decalcification)")
        
        # Check Silica gel evolution (may increase from C-S-H decalcification)
        silica_initial = df['Silica_gel_kg'].iloc[0]
        silica_final = df['Silica_gel_kg'].iloc[-1]
        silica_change = silica_final - silica_initial
        
        print(f"  Silica gel: {silica_initial:.4f} → {silica_final:.4f} kg (Δ = {silica_change:+.4f})")
        
        if silica_change < 0:
            print(f"    ? Silica gel decreased (unusual)")
        else:
            print(f"    ✓ Silica gel increased (expected from C-S-H decalcification)")
        
        # Check pH evolution (should decrease with carbonation)
        pH_initial = df['pH'].iloc[0]
        pH_final = df['pH'].iloc[-1]
        pH_change = pH_final - pH_initial
        
        print(f"  pH: {pH_initial:.2f} → {pH_final:.2f} (Δ = {pH_change:+.2f})")
        
        if pH_change >= 0:
            print(f"    ✗ WARNING: pH should decrease with carbonation!")
            all_reasonable = False
        else:
            print(f"    ✓ pH decreased with carbonation (expected)")
    
    print()
    if all_reasonable:
        print("✓ All phase evolution patterns are chemically reasonable")
    else:
        print("✗ Some phase evolution patterns are questionable")
    
    return all_reasonable


def verify_representative_mixes():
    """
    Verify that representative mixes span the required range.
    
    Returns:
        bool: True if mixes are representative, False otherwise
    """
    print()
    print("="*70)
    print("4. VERIFYING REPRESENTATIVE MIX SELECTION")
    print("="*70)
    
    data_dir = OUTPUTS_TABLES_DIR / "reaction_paths"
    
    # Check f_FA range
    f_FA_values = []
    
    for f_FA in [0.1, 0.5, 0.9]:
        filename = f"reaction_path_data_R0.6_fFA{f_FA}.csv"
        file_path = data_dir / filename
        
        if file_path.exists():
            f_FA_values.append(f_FA)
    
    print(f"Selected f_FA values: {f_FA_values}")
    
    all_good = True
    
    # Check coverage
    if len(f_FA_values) < 3:
        print(f"  ✗ WARNING: Need at least 3 representative mixes, found {len(f_FA_values)}")
        all_good = False
    else:
        print(f"  ✓ Number of mixes: {len(f_FA_values)}")
    
    # Check if they span low/medium/high range
    if min(f_FA_values) > 0.2:
        print(f"  ✗ WARNING: No low f_FA mix (cement-dominated)")
        all_good = False
    else:
        print(f"  ✓ Low f_FA mix present: {min(f_FA_values)}")
    
    if max(f_FA_values) < 0.7:
        print(f"  ✗ WARNING: No high f_FA mix (fly ash-dominated)")
        all_good = False
    else:
        print(f"  ✓ High f_FA mix present: {max(f_FA_values)}")
    
    # Check if there's a balanced mix
    has_balanced = any(0.3 < val < 0.7 for val in f_FA_values)
    if not has_balanced:
        print(f"  ✗ WARNING: No balanced f_FA mix")
        all_good = False
    else:
        balanced_val = [val for val in f_FA_values if 0.3 < val < 0.7][0]
        print(f"  ✓ Balanced f_FA mix present: {balanced_val}")
    
    print()
    if all_good:
        print("✓ Representative mixes span full range (low/medium/high)")
    else:
        print("✗ Representative mix selection has gaps")
    
    return all_good


def verify_requirements_compliance():
    """
    Verify compliance with requirements document section 4.4.
    
    Returns:
        bool: True if all requirements met, False otherwise
    """
    print()
    print("="*70)
    print("5. VERIFYING REQUIREMENTS COMPLIANCE (Section 4.4)")
    print("="*70)
    
    all_compliant = True
    
    # Requirement 1: 2-3 representative mixes
    data_dir = OUTPUTS_TABLES_DIR / "reaction_paths"
    n_mixes = len(list(data_dir.glob("reaction_path_data_*.csv")))
    
    print(f"\nRequirement 1: Select 2-3 representative mixes")
    print(f"  Found: {n_mixes} mixes")
    if 2 <= n_mixes <= 3:
        print(f"  ✓ Requirement met")
    else:
        print(f"  ✗ Expected 2-3 mixes, found {n_mixes}")
        all_compliant = False
    
    # Requirement 2: Stepwise carbonation
    print(f"\nRequirement 2: Stepwise carbonation (gradually increase CO₂)")
    
    for f_FA in [0.1, 0.5, 0.9]:
        filename = f"reaction_path_data_R0.6_fFA{f_FA}.csv"
        file_path = data_dir / filename
        
        if file_path.exists():
            df = pd.read_csv(file_path)
            yCO2_values = df['yCO2'].values
            
            # Check if yCO2 is monotonically increasing
            is_increasing = all(yCO2_values[i] < yCO2_values[i+1] for i in range(len(yCO2_values)-1))
            
            print(f"  f_FA={f_FA}: yCO2 steps = {len(yCO2_values)}, range = [{yCO2_values[0]:.2f}, {yCO2_values[-1]:.2f}]")
            
            if is_increasing:
                print(f"    ✓ Stepwise increase verified")
            else:
                print(f"    ✗ yCO2 not monotonically increasing!")
                all_compliant = False
    
    # Requirement 3: Phase transformation sequence
    print(f"\nRequirement 3: Observe phase transformation sequence")
    
    figures_dir = OUTPUTS_FIGURES_DIR / "reaction_paths"
    phase_figures = list(figures_dir.glob("reaction_path_*_phases.png"))
    pH_figures = list(figures_dir.glob("reaction_path_*_pH.png"))
    
    print(f"  Phase evolution figures: {len(phase_figures)}")
    print(f"  Phase + pH figures: {len(pH_figures)}")
    print(f"  Comparison figure: {'✓' if (figures_dir / 'reaction_paths_comparison_R0.6.png').exists() else '✗'}")
    
    if len(phase_figures) >= 3 and len(pH_figures) >= 3:
        print(f"  ✓ Phase transformation visualization complete")
    else:
        print(f"  ✗ Insufficient phase transformation figures")
        all_compliant = False
    
    # Requirement 4: Cover different fly ash levels
    print(f"\nRequirement 4: Cover low/medium/high fly ash levels")
    
    f_FA_covered = []
    for f_FA in [0.1, 0.5, 0.9]:
        filename = f"reaction_path_data_R0.6_fFA{f_FA}.csv"
        if (data_dir / filename).exists():
            f_FA_covered.append(f_FA)
    
    has_low = any(val <= 0.3 for val in f_FA_covered)
    has_medium = any(0.3 < val < 0.7 for val in f_FA_covered)
    has_high = any(val >= 0.7 for val in f_FA_covered)
    
    print(f"  Low f_FA: {'✓' if has_low else '✗'}")
    print(f"  Medium f_FA: {'✓' if has_medium else '✗'}")
    print(f"  High f_FA: {'✓' if has_high else '✗'}")
    
    if has_low and has_medium and has_high:
        print(f"  ✓ Full f_FA range covered")
    else:
        print(f"  ✗ f_FA range incomplete")
        all_compliant = False
    
    print()
    if all_compliant:
        print("✓ All requirements (section 4.4) satisfied")
    else:
        print("✗ Some requirements not fully met")
    
    return all_compliant


def generate_summary_report():
    """
    Generate summary report of Phase 10 deliverables.
    """
    print()
    print("="*70)
    print("6. PHASE 10 SUMMARY REPORT")
    print("="*70)
    
    # Count deliverables
    figures_dir = OUTPUTS_FIGURES_DIR / "reaction_paths"
    data_dir = OUTPUTS_TABLES_DIR / "reaction_paths"
    
    n_figures = len(list(figures_dir.glob("*.png")))
    n_data_files = len(list(data_dir.glob("*.csv")))
    
    print(f"\nDeliverables:")
    print(f"  - Figures: {n_figures}")
    print(f"  - Data files: {n_data_files}")
    
    # Calculate total figure size
    total_size = sum(f.stat().st_size for f in figures_dir.glob("*.png"))
    print(f"  - Total figure size: {total_size/1024/1024:.2f} MB")
    
    # List figures
    print(f"\nGenerated figures:")
    for fig_path in sorted(figures_dir.glob("*.png")):
        size_kb = fig_path.stat().st_size / 1024
        print(f"  - {fig_path.name} ({size_kb:.1f} KB)")
    
    # List data files
    print(f"\nGenerated data files:")
    for data_path in sorted(data_dir.glob("*.csv")):
        df = pd.read_csv(data_path)
        print(f"  - {data_path.name} ({len(df)} rows)")
    
    print()


def main():
    """
    Main verification function for Phase 10.
    """
    print()
    print("="*70)
    print("PHASE 10 VERIFICATION: REACTION-PATH SIMULATIONS")
    print("="*70)
    print()
    
    # Run all verifications
    results = []
    
    results.append(("Reaction path figures", verify_reaction_path_figures()))
    results.append(("Reaction path data", verify_reaction_path_data()))
    results.append(("Phase evolution patterns", verify_phase_evolution()))
    results.append(("Representative mix selection", verify_representative_mixes()))
    results.append(("Requirements compliance", verify_requirements_compliance()))
    
    # Generate summary
    generate_summary_report()
    
    # Final report
    print()
    print("="*70)
    print("VERIFICATION RESULTS")
    print("="*70)
    print()
    
    all_passed = True
    for test_name, result in results:
        status = "✓ PASS" if result else "✗ FAIL"
        print(f"{status}: {test_name}")
        if not result:
            all_passed = False
    
    print()
    print("="*70)
    
    if all_passed:
        print("✓✓✓ PHASE 10 VERIFICATION: ALL TESTS PASSED ✓✓✓")
    else:
        print("✗✗✗ PHASE 10 VERIFICATION: SOME TESTS FAILED ✗✗✗")
    
    print("="*70)
    print()
    
    return all_passed


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
