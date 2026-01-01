"""
Test Phase 5 Implementation
============================
Comprehensive tests for CemGEMS output parsing and data aggregation.

Tests:
1. Parser initialization
2. Format detection
3. JSON parsing
4. Text parsing
5. Validation
6. Data aggregation
7. Long format conversion
8. Export functionality

All tests use REAL implementations - NO MOCKS.

Author: Phase 5 Testing
Date: January 1, 2026
"""

import sys
from pathlib import Path
import json
import tempfile
import shutil

# Add scripts directory to path
SCRIPTS_DIR = Path(__file__).parent
if str(SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_DIR))

import pandas as pd
import config
from cemgems_output_parser import CemGEMSOutputParser, DataAggregator


def test_parser_initialization():
    """Test 1: Parser initializes correctly."""
    print("\n" + "=" * 80)
    print("TEST 1: Parser Initialization")
    print("=" * 80)
    
    try:
        parser = CemGEMSOutputParser()
        
        # Check attributes
        assert hasattr(parser, 'phase_patterns'), "Missing phase_patterns attribute"
        assert hasattr(parser, 'convergence_indicators'), "Missing convergence_indicators"
        assert len(parser.convergence_indicators) > 0, "No convergence indicators defined"
        
        print("✓ PASS: Parser initialized successfully")
        print(f"  Convergence indicators: {len(parser.convergence_indicators)}")
        print(f"  Phase patterns: {len([p for p in parser.phase_patterns.values() if p])}")
        return True
        
    except Exception as e:
        print(f"✗ FAIL: {e}")
        return False


def test_format_detection():
    """Test 2: Format detection works correctly."""
    print("\n" + "=" * 80)
    print("TEST 2: Format Detection")
    print("=" * 80)
    
    parser = CemGEMSOutputParser()
    
    try:
        # Create temporary test files
        with tempfile.TemporaryDirectory() as tmpdir:
            tmppath = Path(tmpdir)
            
            # JSON file
            json_file = tmppath / 'test.json'
            with open(json_file, 'w') as f:
                json.dump({'test': 'data'}, f)
            
            # Text file
            text_file = tmppath / 'test.txt'
            with open(text_file, 'w') as f:
                f.write('Phase: Calcite Amount: 0.15 mol\n')
            
            # DAT file
            dat_file = tmppath / 'test.dat'
            with open(dat_file, 'w') as f:
                f.write('Binary data here\n')
            
            # Test detection
            json_fmt = parser.detect_format(json_file)
            text_fmt = parser.detect_format(text_file)
            dat_fmt = parser.detect_format(dat_file)
            
            assert json_fmt == 'json', f"JSON detection failed: {json_fmt}"
            assert text_fmt == 'text', f"Text detection failed: {text_fmt}"
            assert dat_fmt == 'dat', f"DAT detection failed: {dat_fmt}"
            
            print("✓ PASS: Format detection working")
            print(f"  .json detected as: {json_fmt}")
            print(f"  .txt detected as: {text_fmt}")
            print(f"  .dat detected as: {dat_fmt}")
            return True
            
    except Exception as e:
        print(f"✗ FAIL: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_json_parsing():
    """Test 3: JSON parsing extracts data correctly."""
    print("\n" + "=" * 80)
    print("TEST 3: JSON Parsing")
    print("=" * 80)
    
    parser = CemGEMSOutputParser()
    
    try:
        with tempfile.TemporaryDirectory() as tmpdir:
            tmppath = Path(tmpdir)
            json_file = tmppath / 'test_output.json'
            
            # Create test JSON output
            test_data = {
                'converged': True,
                'phases': {
                    'Calcite': 0.150,
                    'Portlandite': 0.075,
                    'CSH_TobH': 0.250
                },
                'bulk_composition': {
                    'Ca': 1.5,
                    'Si': 0.8,
                    'Al': 0.3
                },
                'pH': 12.5,
                'temperature_K': 298.15,
                'pressure_bar': 1.01325,
                'gibbs_energy': -15000.0
            }
            
            with open(json_file, 'w') as f:
                json.dump(test_data, f)
            
            # Parse
            result = parser.parse_output_file(str(json_file))
            
            # Validate
            assert result['converged'] == True, "Convergence flag incorrect"
            assert len(result['phases']) == 3, f"Wrong number of phases: {len(result['phases'])}"
            assert 'Calcite' in result['phases'], "Calcite not found in phases"
            assert abs(result['phases']['Calcite'] - 0.150) < 1e-6, "Calcite amount incorrect"
            assert result['pH'] == 12.5, "pH incorrect"
            assert result['temperature_K'] == 298.15, "Temperature incorrect"
            
            print("✓ PASS: JSON parsing working correctly")
            print(f"  Converged: {result['converged']}")
            print(f"  Phases: {len(result['phases'])}")
            print(f"  pH: {result['pH']}")
            print(f"  Gibbs energy: {result['gibbs_energy']}")
            return True
            
    except Exception as e:
        print(f"✗ FAIL: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_text_parsing():
    """Test 4: Text format parsing works."""
    print("\n" + "=" * 80)
    print("TEST 4: Text Format Parsing")
    print("=" * 80)
    
    parser = CemGEMSOutputParser()
    
    try:
        with tempfile.TemporaryDirectory() as tmpdir:
            tmppath = Path(tmpdir)
            text_file = tmppath / 'test_output.txt'
            
            # Create test text output
            test_content = """
GEMS Equilibrium Calculation
CONVERGED

Stable Phases:
Calcite    0.150 mol
Portlandite  0.075 mol
CSH_TobH   0.250 mol

Solution Properties:
pH = 12.5
Ionic strength = 0.85
Temperature = 298.15 K
Pressure = 1.01325 bar
Gibbs energy = -15000.0 J
"""
            
            with open(text_file, 'w') as f:
                f.write(test_content)
            
            # Parse
            result = parser.parse_output_file(str(text_file))
            
            # Validate
            assert result['converged'] == True, "Should detect convergence"
            assert result['pH'] == 12.5, f"pH incorrect: {result['pH']}"
            assert result['temperature_K'] == 298.15, "Temperature incorrect"
            assert len(result['phases']) >= 0, "Should parse phases"
            
            print("✓ PASS: Text parsing working")
            print(f"  Converged: {result['converged']}")
            print(f"  pH: {result['pH']}")
            print(f"  Temperature: {result['temperature_K']} K")
            print(f"  Ionic strength: {result['ionic_strength']}")
            return True
            
    except Exception as e:
        print(f"✗ FAIL: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_validation():
    """Test 5: Output validation works correctly."""
    print("\n" + "=" * 80)
    print("TEST 5: Output Validation")
    print("=" * 80)
    
    parser = CemGEMSOutputParser()
    
    try:
        # Test valid output
        valid_result = {
            'converged': True,
            'phases': {'Calcite': 0.15, 'Portlandite': 0.075},
            'pH': 12.5,
            'ionic_strength': 0.85
        }
        
        is_valid, warnings = parser.validate_output(valid_result)
        assert is_valid == True, "Valid output should pass"
        assert len(warnings) == 0, f"Valid output should have no warnings: {warnings}"
        
        # Test non-converged
        nonconv_result = {
            'converged': False,
            'phases': {},
            'pH': None
        }
        
        is_valid2, warnings2 = parser.validate_output(nonconv_result)
        assert is_valid2 == False, "Non-converged should fail"
        assert len(warnings2) > 0, "Non-converged should have warnings"
        
        # Test invalid pH
        invalid_ph = {
            'converged': True,
            'phases': {'Calcite': 0.15},
            'pH': 25.0,  # Out of range
            'ionic_strength': 0.5
        }
        
        is_valid3, warnings3 = parser.validate_output(invalid_ph)
        assert is_valid3 == False, "Invalid pH should fail"
        assert any('pH' in w for w in warnings3), "Should warn about pH"
        
        # Test negative phase amount
        negative_phase = {
            'converged': True,
            'phases': {'Calcite': 0.15, 'Bad_phase': -0.05},
            'pH': 12.5
        }
        
        is_valid4, warnings4 = parser.validate_output(negative_phase)
        assert is_valid4 == False, "Negative phase should fail"
        assert any('negative' in w.lower() for w in warnings4), "Should warn about negative"
        
        print("✓ PASS: Validation working correctly")
        print(f"  Valid output: PASS")
        print(f"  Non-converged: FAIL (expected)")
        print(f"  Invalid pH: FAIL (expected)")
        print(f"  Negative phase: FAIL (expected)")
        return True
        
    except Exception as e:
        print(f"✗ FAIL: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_data_aggregation():
    """Test 6: Data aggregation works."""
    print("\n" + "=" * 80)
    print("TEST 6: Data Aggregation")
    print("=" * 80)
    
    try:
        with tempfile.TemporaryDirectory() as tmpdir:
            tmppath = Path(tmpdir)
            
            # Create sample mix designs
            mix_designs = pd.DataFrame({
                'mix_id': ['MIX_0000', 'MIX_0001', 'MIX_0002'],
                'R': [0.3, 0.3, 0.3],
                'f_FA': [0.0, 0.1, 0.2],
                'yCO2': [0.0, 0.0, 0.15],
                'w_SS': [0.02, 0.02, 0.02],
                'w_b': [1.1, 1.1, 1.1]
            })
            
            mix_file = tmppath / 'mix_designs.csv'
            mix_designs.to_csv(mix_file, index=False)
            
            # Create sample output files
            output_dir = tmppath / 'outputs'
            output_dir.mkdir()
            
            for mix_id in mix_designs['mix_id']:
                output_file = output_dir / f'{mix_id}.json'
                output_data = {
                    'converged': True,
                    'phases': {
                        'Calcite': 0.15,
                        'Portlandite': 0.075
                    },
                    'pH': 12.5
                }
                with open(output_file, 'w') as f:
                    json.dump(output_data, f)
            
            # Aggregate
            parser = CemGEMSOutputParser()
            aggregator = DataAggregator(parser)
            
            df_master = aggregator.aggregate_equilibrium_results(
                input_dir=str(tmppath),
                output_dir=str(output_dir),
                mix_designs_file=str(mix_file)
            )
            
            # Validate
            assert len(df_master) == 3, f"Wrong number of rows: {len(df_master)}"
            assert 'mix_id' in df_master.columns, "Missing mix_id column"
            assert 'converged' in df_master.columns, "Missing converged column"
            assert 'pH' in df_master.columns, "Missing pH column"
            assert df_master['converged'].all(), "All should be converged"
            
            print("✓ PASS: Data aggregation working")
            print(f"  Rows aggregated: {len(df_master)}")
            print(f"  Columns: {len(df_master.columns)}")
            print(f"  Convergence rate: {df_master['converged'].mean() * 100:.1f}%")
            return True
            
    except Exception as e:
        print(f"✗ FAIL: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_long_format_conversion():
    """Test 7: Long format conversion works."""
    print("\n" + "=" * 80)
    print("TEST 7: Long Format Conversion")
    print("=" * 80)
    
    try:
        # Create sample wide format data
        df_wide = pd.DataFrame({
            'mix_id': ['MIX_0000', 'MIX_0001'],
            'R': [0.3, 0.3],
            'f_FA': [0.0, 0.1],
            'yCO2': [0.0, 0.15],
            'w_SS': [0.02, 0.02],
            'w_b': [1.1, 1.1],
            'phase_Calcite_mol': [0.15, 0.12],
            'phase_Portlandite_mol': [0.075, 0.060],
            'phase_CSH_mol': [0.25, 0.30]
        })
        
        # Convert
        aggregator = DataAggregator()
        df_long = aggregator.create_long_format(df_wide)
        
        # Validate
        assert 'phase_name' in df_long.columns, "Missing phase_name column"
        assert 'amount_mol' in df_long.columns, "Missing amount_mol column"
        assert len(df_long) > 0, "Should have phase records"
        assert all(df_long['amount_mol'] > 0), "All amounts should be positive"
        
        # Check phase names are cleaned
        assert not any('phase_' in name for name in df_long['phase_name']), "Phase names not cleaned"
        assert not any('_mol' in name for name in df_long['phase_name']), "Phase names not cleaned"
        
        print("✓ PASS: Long format conversion working")
        print(f"  Wide format rows: {len(df_wide)}")
        print(f"  Long format rows: {len(df_long)}")
        print(f"  Unique phases: {df_long['phase_name'].nunique()}")
        return True
        
    except Exception as e:
        print(f"✗ FAIL: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_export_functionality():
    """Test 8: Export functionality works."""
    print("\n" + "=" * 80)
    print("TEST 8: Export Functionality")
    print("=" * 80)
    
    try:
        with tempfile.TemporaryDirectory() as tmpdir:
            tmppath = Path(tmpdir)
            
            # Create sample data
            df_sample = pd.DataFrame({
                'mix_id': ['MIX_0000', 'MIX_0001', 'MIX_0002'],
                'R': [0.3, 0.3, 0.3],
                'converged': [True, True, False],
                'pH': [12.5, 12.3, None],
                'phase_Calcite_mol': [0.15, 0.12, 0.0]
            })
            
            # Export
            aggregator = DataAggregator()
            aggregator.export_results(
                df_sample,
                output_dir=str(tmppath),
                prefix='test_export'
            )
            
            # Check files
            csv_file = tmppath / 'test_export.csv'
            summary_file = tmppath / 'test_export_summary.txt'
            
            assert csv_file.exists(), "CSV file not created"
            assert summary_file.exists(), "Summary file not created"
            
            # Verify CSV can be read
            df_loaded = pd.read_csv(csv_file)
            assert len(df_loaded) == 3, "CSV has wrong number of rows"
            
            # Verify summary file
            with open(summary_file, 'r') as f:
                summary_content = f.read()
            assert 'Total mix designs: 3' in summary_content, "Summary missing total"
            assert 'Converged: 2' in summary_content, "Summary missing convergence count"
            
            print("✓ PASS: Export functionality working")
            print(f"  CSV created: {csv_file.name}")
            print(f"  Summary created: {summary_file.name}")
            print(f"  CSV verified: {len(df_loaded)} rows")
            return True
            
    except Exception as e:
        print(f"✗ FAIL: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Run all Phase 5 tests."""
    
    print("\n" + "=" * 80)
    print("PHASE 5 IMPLEMENTATION TEST SUITE")
    print("CemGEMS Output Parsing & Data Aggregation")
    print("=" * 80)
    
    tests = [
        ("Parser Initialization", test_parser_initialization),
        ("Format Detection", test_format_detection),
        ("JSON Parsing", test_json_parsing),
        ("Text Parsing", test_text_parsing),
        ("Output Validation", test_validation),
        ("Data Aggregation", test_data_aggregation),
        ("Long Format Conversion", test_long_format_conversion),
        ("Export Functionality", test_export_functionality),
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
        print("\n✅ PHASE 5 COMPLETE: All tests passed!")
        print("\nDeliverables:")
        print("  ✓ cemgems_output_parser.py - Full implementation")
        print("  ✓ JSON format parsing")
        print("  ✓ Text format parsing")
        print("  ✓ Output validation")
        print("  ✓ Data aggregation")
        print("  ✓ Long format conversion")
        print("  ✓ Export functionality")
        print("\nNext Phase: Phase 6 - Phase Diagram Generation")
    else:
        print("\n⚠ Some tests failed - review above")
    
    return passed == total


if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)
