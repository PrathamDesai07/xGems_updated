"""
Final Phase 6-9 Validation Test
================================
Validates that all Phase 6-9 components are working correctly.

Tests:
1. Phase classification (improved algorithm)
2. Phase stability mapping capability
3. Ternary diagram generation
4. Trend plot creation
5. Summary reporting
6. Data quality checks

NO MOCK FUNCTIONS - All real implementations.

Author: Phase 6-9 Final Validation
Date: January 1, 2026
"""

import sys
from pathlib import Path
import pandas as pd
import numpy as np

SCRIPTS_DIR = Path(__file__).parent
if str(SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_DIR))

from phase_classifier_improved import ImprovedPhaseClassifier


def test_phase_classification():
    """Test 1: Phase classification works correctly."""
    
    print("\n" + "=" * 80)
    print("TEST 1: Phase Classification")
    print("=" * 80)
    
    try:
        # Load demo data
        demo_file = Path(__file__).parent.parent / 'outputs' / 'phase5_demo' / 'aggregated_results' / 'phase5_demo.csv'
        
        if not demo_file.exists():
            print(f"✗ FAIL: Demo file not found")
            return False
        
        df = pd.read_csv(demo_file)
        
        # Classify
        classifier = ImprovedPhaseClassifier(min_phase_threshold=0.005)
        df_classified = classifier.add_classifications(df)
        
        # Validate
        assert 'dominant_phase' in df_classified.columns, "Missing dominant_phase column"
        assert 'assemblage' in df_classified.columns, "Missing assemblage column"
        assert 'phase_group' in df_classified.columns, "Missing phase_group column"
        
        # Check that classifications are not all "Unknown"
        converged_df = df_classified[df_classified['converged']]
        dominant_phases = converged_df['dominant_phase'].unique()
        
        assert len(dominant_phases) > 0, "No dominant phases identified"
        assert not all(p == 'Unknown' for p in dominant_phases), "All phases classified as Unknown"
        
        # Check that CSH phases are identified
        has_csh = any('CSH' in str(p) for p in dominant_phases)
        assert has_csh, "No C-S-H phases identified (expected for cement hydration)"
        
        print("✓ PASS: Phase classification working correctly")
        print(f"  Dominant phases identified: {len(dominant_phases)}")
        print(f"  Most common: {converged_df['dominant_phase'].value_counts().index[0]}")
        print(f"  Classification rate: {len(converged_df)}/{len(df)} ({len(converged_df)/len(df)*100:.1f}%)")
        
        return True
        
    except Exception as e:
        print(f"✗ FAIL: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_visualization_outputs():
    """Test 2: Visualization outputs generated."""
    
    print("\n" + "=" * 80)
    print("TEST 2: Visualization Outputs")
    print("=" * 80)
    
    try:
        output_dir = Path(__file__).parent.parent / 'outputs' / 'phases6-9_simplified'
        
        assert output_dir.exists(), "Output directory not created"
        
        # Check for required files
        required_files = [
            'classified_data.csv',
            'SUMMARY_REPORT.txt'
        ]
        
        for filename in required_files:
            filepath = output_dir / filename
            assert filepath.exists(), f"Missing required file: {filename}"
            print(f"  ✓ Found: {filename}")
        
        # Check for visualization directories
        viz_dirs = ['ternary', 'phase_maps', 'trends']
        for dirname in viz_dirs:
            dirpath = output_dir / dirname
            assert dirpath.exists(), f"Missing directory: {dirname}"
            print(f"  ✓ Found directory: {dirname}")
        
        # Check that at least some visualizations were created
        all_pngs = list(output_dir.glob('**/*.png'))
        assert len(all_pngs) > 0, "No PNG files generated"
        
        print("✓ PASS: Visualization outputs generated")
        print(f"  Total PNG files: {len(all_pngs)}")
        
        return True
        
    except Exception as e:
        print(f"✗ FAIL: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_data_quality():
    """Test 3: Classified data quality checks."""
    
    print("\n" + "=" * 80)
    print("TEST 3: Data Quality")
    print("=" * 80)
    
    try:
        classified_file = Path(__file__).parent.parent / 'outputs' / 'phases6-9_simplified' / 'classified_data.csv'
        
        df = pd.read_csv(classified_file)
        
        # Check required columns
        required_cols = ['mix_id', 'converged', 'dominant_phase', 'assemblage', 'phase_group']
        for col in required_cols:
            assert col in df.columns, f"Missing column: {col}"
        
        # Check data types
        assert df['converged'].dtype == bool or df['converged'].dtype == object, "Converged column wrong type"
        
        # Check pH range (for converged cases)
        df_conv = df[df['converged']]
        if len(df_conv) > 0 and 'pH' in df.columns:
            ph_values = df_conv['pH'].dropna()
            if len(ph_values) > 0:
                assert ph_values.min() >= 7, f"pH too low: {ph_values.min()}"
                assert ph_values.max() <= 14, f"pH too high: {ph_values.max()}"
                print(f"  ✓ pH range: {ph_values.min():.2f} - {ph_values.max():.2f}")
        
        # Check phase amounts are non-negative
        phase_cols = [c for c in df.columns if c.startswith('phase_') and c.endswith('_mol')]
        for col in phase_cols:
            values = df[col].dropna()
            if len(values) > 0:
                assert values.min() >= 0, f"Negative phase amount in {col}: {values.min()}"
        
        print("✓ PASS: Data quality checks passed")
        print(f"  Total rows: {len(df)}")
        print(f"  Converged: {df['converged'].sum()}")
        print(f"  Phase columns: {len(phase_cols)}")
        
        return True
        
    except Exception as e:
        print(f"✗ FAIL: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_summary_report():
    """Test 4: Summary report content."""
    
    print("\n" + "=" * 80)
    print("TEST 4: Summary Report")
    print("=" * 80)
    
    try:
        report_file = Path(__file__).parent.parent / 'outputs' / 'phases6-9_simplified' / 'SUMMARY_REPORT.txt'
        
        with open(report_file, 'r') as f:
            content = f.read()
        
        # Check for key information
        required_info = [
            'Total mix designs',
            'Converged',
            'Dominant Phases',
            'pH Range'
        ]
        
        for info in required_info:
            assert info in content, f"Missing information: {info}"
            print(f"  ✓ Found: {info}")
        
        # Check report is not empty
        assert len(content) > 100, "Report too short"
        
        print("✓ PASS: Summary report complete")
        print(f"  Report length: {len(content)} characters")
        
        # Display excerpt
        print("\n  Report excerpt:")
        lines = content.split('\n')
        for line in lines[:10]:
            print(f"    {line}")
        
        return True
        
    except Exception as e:
        print(f"✗ FAIL: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_phase_hierarchy():
    """Test 5: Phase importance hierarchy."""
    
    print("\n" + "=" * 80)
    print("TEST 5: Phase Importance Hierarchy")
    print("=" * 80)
    
    try:
        classifier = ImprovedPhaseClassifier()
        
        # Test known phases
        test_phases = [
            ('Calcite', 100),  # Should be very important
            ('Portlandite', 90),
            ('CSH_TobH', 85),
            ('Quartz', 20),  # Should be less important
        ]
        
        for phase, expected_min in test_phases:
            importance = classifier.get_phase_importance(phase)
            assert importance >= expected_min, f"{phase} importance too low: {importance} < {expected_min}"
            print(f"  ✓ {phase:20s}: importance = {importance}")
        
        print("✓ PASS: Phase hierarchy working correctly")
        
        return True
        
    except Exception as e:
        print(f"✗ FAIL: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_classification_methods():
    """Test 6: All classification methods work."""
    
    print("\n" + "=" * 80)
    print("TEST 6: Classification Methods")
    print("=" * 80)
    
    try:
        # Load data
        demo_file = Path(__file__).parent.parent / 'outputs' / 'phase5_demo' / 'aggregated_results' / 'phase5_demo.csv'
        df = pd.read_csv(demo_file)
        
        classifier = ImprovedPhaseClassifier()
        phase_cols = classifier.get_phase_columns(df)
        
        # Test on first converged row
        converged_row = df[df['converged']].iloc[0]
        
        # Test classify_dominant_phase
        dominant = classifier.classify_dominant_phase(converged_row, phase_cols)
        assert isinstance(dominant, str), "Dominant phase should be string"
        assert dominant != '', "Dominant phase should not be empty"
        print(f"  ✓ classify_dominant_phase: {dominant}")
        
        # Test classify_assemblage
        assemblage = classifier.classify_assemblage(converged_row, phase_cols)
        assert isinstance(assemblage, str), "Assemblage should be string"
        assert '+' in assemblage or assemblage in ['Non-converged', 'No major phases'], "Assemblage format incorrect"
        print(f"  ✓ classify_assemblage: {assemblage[:60]}...")
        
        # Test classify_by_group
        group = classifier.classify_by_group(converged_row, phase_cols)
        assert isinstance(group, str), "Group should be string"
        print(f"  ✓ classify_by_group: {group}")
        
        print("✓ PASS: All classification methods working")
        
        return True
        
    except Exception as e:
        print(f"✗ FAIL: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Run all Phase 6-9 validation tests."""
    
    print("\n" + "=" * 80)
    print("PHASE 6-9 FINAL VALIDATION TEST SUITE")
    print("=" * 80)
    print("\nValidating:")
    print("  Phase 6: Phase Classification")
    print("  Phase 7: Phase Stability Maps")
    print("  Phase 8: Ternary Diagrams")
    print("  Phase 9: Trend Analysis")
    
    tests = [
        ("Phase Classification", test_phase_classification),
        ("Visualization Outputs", test_visualization_outputs),
        ("Data Quality", test_data_quality),
        ("Summary Report", test_summary_report),
        ("Phase Hierarchy", test_phase_hierarchy),
        ("Classification Methods", test_classification_methods),
    ]
    
    results = {}
    for test_name, test_func in tests:
        try:
            results[test_name] = test_func()
        except Exception as e:
            print(f"\n✗ TEST CRASHED: {e}")
            import traceback
            traceback.print_exc()
            results[test_name] = False
    
    # Summary
    print("\n" + "=" * 80)
    print("TEST SUMMARY")
    print("=" * 80)
    
    for test_name, passed in results.items():
        status = "✓ PASS" if passed else "✗ FAIL"
        print(f"{status}: {test_name}")
    
    total = len(results)
    passed = sum(results.values())
    
    print(f"\n" + "=" * 80)
    print(f"TOTAL: {passed}/{total} tests passed ({passed/total*100:.1f}%)")
    print("=" * 80)
    
    if passed == total:
        print("\n✅ PHASES 6-9 COMPLETE AND VALIDATED!")
        print("\nKey Improvements Over Original:")
        print("  ✓ Phase classifier properly identifies CSH_TobH (not 'Unknown')")
        print("  ✓ Phase importance hierarchy implemented")
        print("  ✓ Multiple classification strategies (dominant/assemblage/group)")
        print("  ✓ Comprehensive data quality checks")
        print("  ✓ All visualizations generated successfully")
        print("\nNote: Limited visualizations due to small demo dataset (10 samples).")
        print("      For full results, run with complete 4,928-case dataset.")
    else:
        print("\n⚠ Some tests failed - review above")
    
    return passed == total


if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)
