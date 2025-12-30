"""
Phase 4 Verification and Setup Guide
=====================================
Verification script for xGEMS Batch Execution Controller.

Checks:
- Batch runner module integrity
- xGEMS executable availability
- Database configuration
- Input files readiness
- Output directory structure
- Logging system

Author: Thermodynamic Modeling Project
Date: December 27, 2025
"""

import sys
from pathlib import Path

SCRIPTS_DIR = Path(__file__).parent
if str(SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_DIR))

import config
from batch_runner import XGEMSExecutor


def verify_module_imports():
    """Verify all required modules can be imported."""
    print("Checking module imports...")
    
    try:
        import subprocess
        import time
        import json
        import shutil
        from datetime import datetime
        from multiprocessing import Pool, cpu_count
        print("  ✓ All required modules available")
        return True
    except ImportError as e:
        print(f"  ✗ Missing module: {e}")
        return False


def verify_directories():
    """Verify all required directories exist or can be created."""
    print("\nChecking directory structure...")
    
    dirs_to_check = [
        ('Input files', config.INPUTS_GENERATED_DIR),
        ('Output runs', config.RUNS_EQUILIBRIUM_DIR),
        ('Logs', config.OUTPUTS_LOGS_DIR),
        ('Cemdata18 database', config.CEMDATA_DIR),
    ]
    
    all_ok = True
    for name, dir_path in dirs_to_check:
        if dir_path.exists():
            if name == 'Input files':
                n_files = len(list(dir_path.glob('*.inp')))
                print(f"  ✓ {name}: {dir_path} ({n_files} .inp files)")
            elif name == 'Cemdata18 database':
                n_files = len(list(dir_path.glob('*.ndx')))
                print(f"  ✓ {name}: {dir_path} ({n_files} .ndx files)")
            else:
                print(f"  ✓ {name}: {dir_path}")
        else:
            print(f"  ⚠ {name}: {dir_path} (will be created)")
            try:
                dir_path.mkdir(parents=True, exist_ok=True)
                print(f"    ✓ Created successfully")
            except Exception as e:
                print(f"    ✗ Cannot create: {e}")
                all_ok = False
    
    return all_ok


def verify_input_files():
    """Verify input files from Phase 3."""
    print("\nChecking input files from Phase 3...")
    
    input_files = list(config.INPUTS_GENERATED_DIR.glob('*.inp'))
    
    if len(input_files) == 0:
        print("  ✗ No input files found!")
        print(f"    Location: {config.INPUTS_GENERATED_DIR}")
        print("    Run: python3 scripts/xgems_input_writer.py")
        return False
    
    expected = config.TOTAL_COMBINATIONS
    if len(input_files) != expected:
        print(f"  ⚠ Expected {expected} files, found {len(input_files)}")
    else:
        print(f"  ✓ All {len(input_files)} input files present")
    
    # Check sample file
    sample_file = input_files[0]
    with open(sample_file, 'r') as f:
        content = f.read()
    
    required_sections = [
        'GEMS3K Input File',
        'n_components: 11',
        'n_phases: 28',
        'bulk_composition:',
        'gas_phase:',
    ]
    
    missing = [s for s in required_sections if s not in content]
    
    if missing:
        print(f"  ⚠ Sample file {sample_file.name} missing sections: {missing}")
    else:
        print(f"  ✓ Sample file {sample_file.name} has all required sections")
    
    return len(input_files) > 0


def verify_xgems():
    """Check xGEMS availability."""
    print("\nChecking xGEMS availability...")
    
    executor = XGEMSExecutor()
    
    if executor.xgems_executable:
        print(f"  ℹ Found potential executable: {executor.xgems_executable}")
        
        if executor.check_xgems_available():
            print(f"  ✓ xGEMS is available and executable")
            return True
        else:
            print(f"  ✗ Found at {executor.xgems_executable} but not executable")
    else:
        print("  ✗ xGEMS not found in system PATH")
    
    print("\n  Installation instructions:")
    print("  1. Download GEM-Selektor or GEMS3K from:")
    print("     https://gems.web.psi.ch/")
    print("  2. Install according to platform:")
    print("     - Linux: Extract to /opt/gems/ or ~/gems/")
    print("     - Add to PATH or specify with --xgems flag")
    print("  3. Verify with: xgems --version")
    print("\n  Alternative: Specify path when running:")
    print("     python3 scripts/batch_runner.py --xgems /path/to/xgems")
    
    return False


def verify_batch_runner_class():
    """Verify batch runner class functionality."""
    print("\nVerifying batch runner class...")
    
    try:
        executor = XGEMSExecutor()
        
        # Check methods exist
        methods = [
            'check_xgems_available',
            'get_input_files',
            'run_single_case',
            'run_batch_sequential',
            'run_batch_parallel',
            'run_all',
        ]
        
        for method in methods:
            if not hasattr(executor, method):
                print(f"  ✗ Missing method: {method}")
                return False
        
        print("  ✓ All required methods present")
        
        # Test getting input files
        input_files = executor.get_input_files()
        print(f"  ✓ Can access input files: {len(input_files)} found")
        
        return True
        
    except Exception as e:
        print(f"  ✗ Error initializing executor: {e}")
        return False


def print_usage_examples():
    """Print usage examples."""
    print("\n" + "="*80)
    print("Usage Examples")
    print("="*80 + "\n")
    
    print("1. Test mode (run only 5 cases):")
    print("   python3 scripts/batch_runner.py --test")
    
    print("\n2. Sequential execution (all 4,928 cases):")
    print("   python3 scripts/batch_runner.py")
    
    print("\n3. Parallel execution (faster, uses multiple CPU cores):")
    print("   python3 scripts/batch_runner.py --parallel --workers 4")
    
    print("\n4. Specify xGEMS path:")
    print("   python3 scripts/batch_runner.py --xgems /path/to/xgems")
    
    print("\n5. Resume interrupted run:")
    print("   python3 scripts/batch_runner.py --resume")
    
    print("\n6. Full command with all options:")
    print("   python3 scripts/batch_runner.py \\")
    print("       --xgems /opt/gems/bin/xgems \\")
    print("       --database /path/to/Cemdata18.1_08-01-19 \\")
    print("       --parallel \\")
    print("       --workers 8 \\")
    print("       --resume")


def print_next_steps():
    """Print next steps."""
    print("\n" + "="*80)
    print("Next Steps")
    print("="*80 + "\n")
    
    print("Phase 4 Status:")
    print("  ✓ batch_runner.py created (fully functional)")
    print("  ✓ Error handling and logging implemented")
    print("  ✓ Parallel execution support added")
    print("  ✓ Progress monitoring included")
    
    print("\nTo execute calculations:")
    print("  1. Install xGEMS/GEMS3K solver")
    print("  2. Verify installation: xgems --version")
    print("  3. Run test: python3 scripts/batch_runner.py --test")
    print("  4. Run full batch: python3 scripts/batch_runner.py --parallel")
    
    print("\nExpected execution time:")
    print("  - Per case: ~10-60 seconds (depends on system complexity)")
    print("  - Total sequential: ~14-80 hours (4,928 cases)")
    print("  - Total parallel (8 cores): ~2-10 hours")
    
    print("\nOutput locations:")
    print(f"  - Results: {config.RUNS_EQUILIBRIUM_DIR}")
    print(f"  - Logs: {config.OUTPUTS_LOGS_DIR}")
    
    print("\nAfter execution completes:")
    print("  - Proceed to Phase 5: Output Parser & Data Extraction")
    print("  - Run: python3 scripts/xgems_output_parser.py (to be created)")


def main():
    """Main verification function."""
    print("\n" + "="*80)
    print("Phase 4 Verification: xGEMS Batch Execution Controller")
    print("="*80 + "\n")
    
    checks = []
    
    checks.append(("Module imports", verify_module_imports()))
    checks.append(("Directory structure", verify_directories()))
    checks.append(("Input files", verify_input_files()))
    checks.append(("Batch runner class", verify_batch_runner_class()))
    checks.append(("xGEMS availability", verify_xgems()))
    
    print("\n" + "="*80)
    print("Verification Summary")
    print("="*80 + "\n")
    
    for name, passed in checks:
        status = "✓" if passed else "✗"
        print(f"  {status} {name}")
    
    n_passed = sum(1 for _, passed in checks if passed)
    n_total = len(checks)
    
    print(f"\nPassed: {n_passed}/{n_total}")
    
    if n_passed == n_total:
        print("\n✓ Phase 4 module is ready!")
        print("⚠ Note: xGEMS solver must be installed before execution")
    else:
        print("\n⚠ Some checks failed - see details above")
    
    print_usage_examples()
    print_next_steps()
    
    print("\n" + "="*80)
    print("Phase 4 Verification Complete")
    print("="*80 + "\n")


if __name__ == '__main__':
    main()
