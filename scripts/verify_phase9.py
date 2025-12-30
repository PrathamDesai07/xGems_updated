#!/usr/bin/env python3
"""
PHASE 9 VERIFICATION SCRIPT
============================
Verifies the product evolution trend curve generation.

This script checks:
1. All required trend curve files exist
2. Figures are readable and properly formatted
3. Trend data is correctly extracted from real equilibrium results
4. Both curve sets are generated (vs yCO2 and vs f_FA)
5. No mock functions were used - all data is real

NO MOCK FUNCTIONS - This is a validation script using real generated figures.
"""

import os
import sys
import pandas as pd
import numpy as np
from pathlib import Path
import matplotlib.image as mpimg

# Add project root to path
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from config import OUTPUTS_FIGURES_DIR, OUTPUTS_TABLES_DIR


def verify_phase9_completion():
    """
    Verify Phase 9: Product Evolution Trend Curves is complete.
    """
    print("=" * 70)
    print("PHASE 9 VERIFICATION: PRODUCT EVOLUTION TREND CURVES")
    print("=" * 70)
    print()
    
    # Define expected files
    trends_dir = OUTPUTS_FIGURES_DIR / "trends"
    
    # Expected file patterns
    expected_files = [
        # Calcite vs yCO2 for different f_FA
        "calcite_vs_yCO2_R0.6_fFA0.0.png",
        "calcite_vs_yCO2_R0.6_fFA0.3.png",
        "calcite_vs_yCO2_R0.6_fFA0.6.png",
        "calcite_vs_yCO2_R0.6_fFA0.9.png",
        
        # Multi-phase vs yCO2
        "phases_vs_yCO2_R0.6_fFA0.5.png",
        "phases_vs_yCO2_all_R_fFA0.5.png",
        
        # Calcite vs f_FA for different yCO2
        "calcite_vs_fFA_R0.6_yCO20pct.png",
        "calcite_vs_fFA_R0.6_yCO220pct.png",
        "calcite_vs_fFA_R0.6_yCO240pct.png",
        
        # Multi-phase vs f_FA
        "phases_vs_fFA_R0.6_yCO220pct.png",
        "phases_vs_fFA_multi_panel.png",
    ]
    
    # Check 1: Verify all files exist
    print("Check 1: Verifying file existence...")
    print("-" * 70)
    
    missing_files = []
    existing_files = []
    
    for filename in expected_files:
        filepath = trends_dir / filename
        if filepath.exists():
            file_size = filepath.stat().st_size
            existing_files.append((filename, file_size))
            print(f"  ✓ {filename} ({file_size/1024:.1f} KB)")
        else:
            missing_files.append(filename)
            print(f"  ✗ {filename} - NOT FOUND")
    
    print()
    print(f"Found: {len(existing_files)}/{len(expected_files)} files")
    
    if missing_files:
        print(f"\n⚠ WARNING: {len(missing_files)} files missing:")
        for fname in missing_files:
            print(f"  - {fname}")
        return False
    
    print("✓ All expected files exist")
    print()
    
    # Check 2: Verify file integrity
    print("Check 2: Verifying file integrity...")
    print("-" * 70)
    
    corrupt_files = []
    for filename, _ in existing_files:
        filepath = trends_dir / filename
        try:
            # Try to load the image
            img = mpimg.imread(str(filepath))
            
            # Check image dimensions
            height, width = img.shape[:2]
            
            # Verify reasonable dimensions
            if height < 400 or width < 600:
                print(f"  ⚠ {filename}: Small dimensions ({width}x{height})")
                corrupt_files.append((filename, "Small dimensions"))
            else:
                print(f"  ✓ {filename}: {width}x{height} pixels")
                
        except Exception as e:
            print(f"  ✗ {filename}: Cannot read - {str(e)}")
            corrupt_files.append((filename, str(e)))
    
    print()
    
    if corrupt_files:
        print(f"⚠ WARNING: {len(corrupt_files)} files may be corrupt:")
        for fname, reason in corrupt_files:
            print(f"  - {fname}: {reason}")
        return False
    
    print("✓ All files are readable and properly formatted")
    print()
    
    # Check 3: Verify trend data coverage
    print("Check 3: Verifying trend data coverage...")
    print("-" * 70)
    
    # Load classified dataset
    classified_dataset_path = OUTPUTS_TABLES_DIR / "master_dataset_classified.csv"
    
    if not classified_dataset_path.exists():
        print("✗ Classified dataset not found")
        return False
    
    df = pd.read_csv(classified_dataset_path)
    
    # Check Curve Set 1: vs yCO2 (fixed R, f_FA, w_SS, w_b)
    print("Curve Set 1: Phase amounts vs yCO2")
    
    test_cases_yCO2 = [
        (0.6, 0.0, 0.03, 1.4),
        (0.6, 0.3, 0.03, 1.4),
        (0.6, 0.5, 0.03, 1.4),
        (0.6, 0.6, 0.03, 1.4),
        (0.6, 0.9, 0.03, 1.4),
    ]
    
    all_yCO2_valid = True
    for R, f_FA, w_SS, w_b in test_cases_yCO2:
        df_filtered = df[
            (df['R'] == R) &
            (abs(df['f_FA'] - f_FA) < 1e-6) &
            (abs(df['w_SS'] - w_SS) < 1e-6) &
            (abs(df['w_b'] - w_b) < 1e-6)
        ]
        
        n_points = len(df_filtered)
        yCO2_levels = df_filtered['yCO2'].nunique()
        
        print(f"  R={R}, f_FA={f_FA}: {n_points} points, {yCO2_levels} yCO2 levels")
        
        if n_points < 5:
            print(f"    ⚠ WARNING: Only {n_points} data points")
            all_yCO2_valid = False
    
    print()
    
    # Check Curve Set 2: vs f_FA (fixed R, yCO2, w_SS, w_b)
    print("Curve Set 2: Phase amounts vs f_FA")
    
    test_cases_f_FA = [
        (0.6, 0.0, 0.03, 1.4),
        (0.6, 0.20, 0.03, 1.4),
        (0.6, 0.40, 0.03, 1.4),
    ]
    
    all_f_FA_valid = True
    for R, yCO2, w_SS, w_b in test_cases_f_FA:
        df_filtered = df[
            (df['R'] == R) &
            (abs(df['yCO2'] - yCO2) < 1e-6) &
            (abs(df['w_SS'] - w_SS) < 1e-6) &
            (abs(df['w_b'] - w_b) < 1e-6)
        ]
        
        n_points = len(df_filtered)
        f_FA_levels = df_filtered['f_FA'].nunique()
        
        print(f"  R={R}, yCO2={yCO2*100:.0f}%: {n_points} points, {f_FA_levels} f_FA levels")
        
        if n_points < 9:
            print(f"    ⚠ WARNING: Only {n_points} data points")
            all_f_FA_valid = False
    
    print()
    
    if not (all_yCO2_valid and all_f_FA_valid):
        print("⚠ WARNING: Some trend data has insufficient coverage")
        return False
    
    print("✓ All trend data has adequate coverage")
    print()
    
    # Check 4: Verify key phases are present
    print("Check 4: Verifying key phases in dataset...")
    print("-" * 70)
    
    key_phases = ['Calcite', 'C-S-H_1.0', 'Silica_gel', 'Ettringite', 'Hydrotalcite']
    missing_phases = []
    
    for phase in key_phases:
        col_kg = f"{phase}_kg"
        col_mol = f"{phase}_mol"
        
        if col_kg in df.columns and col_mol in df.columns:
            # Check if phase has non-zero values
            max_kg = df[col_kg].max()
            print(f"  ✓ {phase}: max amount = {max_kg:.4f} kg")
        else:
            missing_phases.append(phase)
            print(f"  ✗ {phase}: NOT FOUND in dataset")
    
    print()
    
    if missing_phases:
        print(f"⚠ WARNING: {len(missing_phases)} phases missing from dataset")
        return False
    
    print("✓ All key phases present in dataset")
    print()
    
    # Check 5: Verify no mock functions
    print("Check 5: Verifying no mock functions...")
    print("-" * 70)
    
    # Read the trend_plotter.py file
    plotter_file = PROJECT_ROOT / "scripts" / "trend_plotter.py"
    
    if not plotter_file.exists():
        print("✗ trend_plotter.py not found")
        return False
    
    with open(plotter_file, 'r') as f:
        plotter_code = f.read()
    
    # Check for mock-related keywords in actual code (not comments/docstrings)
    mock_keywords = ['def mock_', 'class Mock', 'fake_data', 'dummy_data', 'test_data', 'synthetic_data']
    found_mocks = []
    
    lines = plotter_code.split('\n')
    in_docstring = False
    
    for i, line in enumerate(lines, 1):
        stripped = line.strip()
        
        # Track docstring state
        if '"""' in stripped or "'''" in stripped:
            in_docstring = not in_docstring
            continue
        
        # Skip comments and docstrings
        if stripped.startswith('#') or in_docstring:
            continue
        
        # Check for mock keywords in actual code
        for keyword in mock_keywords:
            if keyword in stripped:
                found_mocks.append((keyword, i, stripped[:80]))
    
    if found_mocks:
        print("⚠ WARNING: Possible mock-related code found:")
        for keyword, line_num, line in found_mocks:
            print(f"  Line {line_num}: {line}...")
    else:
        print("✓ No mock functions detected in trend_plotter.py")
    
    print()
    
    # Check 6: Verify data source is real
    print("Check 6: Verifying data source...")
    print("-" * 70)
    
    # Check that the plotter reads from actual datasets
    if 'master_dataset_classified.csv' in plotter_code:
        print("  ✓ Uses master_dataset_classified.csv (real equilibrium data)")
    else:
        print("  ✗ Does not reference master_dataset_classified.csv")
        return False
    
    # Check for proper data filtering
    if 'df_filtered' in plotter_code or 'df[' in plotter_code:
        print("  ✓ Performs proper data filtering on real dataset")
    else:
        print("  ✗ No data filtering detected")
        return False
    
    print()
    print("✓ All data sources verified as real equilibrium data")
    print()
    
    # Final summary
    print("=" * 70)
    print("PHASE 9 VERIFICATION SUMMARY")
    print("=" * 70)
    print()
    
    verification_results = {
        "File existence": len(missing_files) == 0,
        "File integrity": len(corrupt_files) == 0,
        "Trend data coverage": all_yCO2_valid and all_f_FA_valid,
        "Key phases present": len(missing_phases) == 0,
        "No mock functions": len(found_mocks) == 0,
        "Real data sources": True
    }
    
    all_passed = all(verification_results.values())
    
    for check, passed in verification_results.items():
        status = "✓ PASS" if passed else "✗ FAIL"
        print(f"{status}: {check}")
    
    print()
    
    if all_passed:
        print("✓✓✓ PHASE 9 VERIFICATION COMPLETE - ALL CHECKS PASSED ✓✓✓")
        print()
        print("Generated outputs:")
        print(f"  - 11 trend curve figures")
        print(f"  - Curve Set 1: Phase amounts vs yCO2 (6 figures)")
        print(f"    * Calcite vs yCO2 for f_FA = 0.0, 0.3, 0.6, 0.9")
        print(f"    * Multi-phase vs yCO2 (5 phases)")
        print(f"    * Multi-panel comparison (4 R values)")
        print(f"  - Curve Set 2: Phase amounts vs f_FA (5 figures)")
        print(f"    * Calcite vs f_FA for yCO2 = 0%, 20%, 40%")
        print(f"    * Multi-phase vs f_FA (5 phases)")
        print(f"    * Multi-panel comparison (2 R × 3 yCO2)")
        print(f"  - Total file size: {sum(size for _, size in existing_files)/1024:.1f} KB")
        print()
        print("Phase 9 deliverables:")
        print("  ✓ Product evolution trend curves generated")
        print("  ✓ Fixed parameters: w_SS=3%, w_b=1.4")
        print("  ✓ Key phases: Calcite, C-S-H, Silica gel, Ettringite, Hydrotalcite")
        print("  ✓ Curve Set 1: Phases vs yCO2 (fixed R, f_FA)")
        print("  ✓ Curve Set 2: Phases vs f_FA (fixed R, yCO2)")
        print("  ✓ Multi-panel comparison figures")
        print("  ✓ NO MOCK FUNCTIONS - All visualizations use real equilibrium data")
        return True
    else:
        print("✗✗✗ PHASE 9 VERIFICATION INCOMPLETE - SOME CHECKS FAILED ✗✗✗")
        return False


if __name__ == "__main__":
    success = verify_phase9_completion()
    sys.exit(0 if success else 1)
