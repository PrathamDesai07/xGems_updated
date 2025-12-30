#!/usr/bin/env python3
"""
PHASE 12 VERIFICATION: DATA EXPORT & VISUALIZATION PIPELINE
============================================================
Comprehensive verification that Phase 12 deliverables are complete.

This script verifies:
1. Deliverables inventory created
2. Project summary generated
3. All required outputs present
4. Project README complete
5. Requirements.txt up to date

NO mock functions - all verification uses real project outputs.
"""

import sys
import json
from pathlib import Path

# Add project root to path
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from config import OUTPUTS_FIGURES_DIR, OUTPUTS_TABLES_DIR, SCRIPTS_DIR


def verify_deliverables_inventory():
    """
    Verify deliverables inventory file was created.
    
    Returns:
        bool: True if inventory exists and is complete
    """
    print("="*70)
    print("1. VERIFYING DELIVERABLES INVENTORY")
    print("="*70)
    
    inventory_path = OUTPUTS_TABLES_DIR / "deliverables_inventory.txt"
    
    if not inventory_path.exists():
        print("✗ deliverables_inventory.txt not found")
        return False
    
    print(f"✓ deliverables_inventory.txt exists ({inventory_path.stat().st_size} bytes)")
    
    # Check content
    with open(inventory_path, 'r') as f:
        content = f.read()
    
    required_sections = [
        'SUMMARY STATISTICS',
        'DATASETS',
        'FIGURES',
        'SCRIPTS'
    ]
    
    all_present = True
    for section in required_sections:
        if section in content:
            print(f"  ✓ {section} section present")
        else:
            print(f"  ✗ {section} section missing")
            all_present = False
    
    return all_present


def verify_project_summary():
    """
    Verify project summary JSON file was created.
    
    Returns:
        bool: True if summary exists and is valid
    """
    print()
    print("="*70)
    print("2. VERIFYING PROJECT SUMMARY")
    print("="*70)
    
    summary_path = OUTPUTS_TABLES_DIR / "project_summary.json"
    
    if not summary_path.exists():
        print("✗ project_summary.json not found")
        return False
    
    print(f"✓ project_summary.json exists")
    
    # Load and validate JSON
    try:
        with open(summary_path, 'r') as f:
            summary = json.load(f)
        
        required_keys = [
            'project_name',
            'completion_date',
            'total_calculations',
            'convergence_rate',
            'phases_identified',
            'phase_names',
            'outputs'
        ]
        
        all_present = True
        for key in required_keys:
            if key in summary:
                print(f"  ✓ {key}: {summary[key]}")
            else:
                print(f"  ✗ {key} missing")
                all_present = False
        
        return all_present
        
    except json.JSONDecodeError as e:
        print(f"✗ Error parsing JSON: {e}")
        return False


def verify_all_deliverables():
    """
    Verify all major deliverables are present.
    
    Returns:
        dict: Deliverable presence check
    """
    print()
    print("="*70)
    print("3. VERIFYING ALL DELIVERABLES")
    print("="*70)
    print()
    
    deliverables = {
        'master_dataset': OUTPUTS_TABLES_DIR / "master_dataset_classified.csv",
        'validation_report': OUTPUTS_TABLES_DIR / "validation_report.txt",
        'deliverables_inventory': OUTPUTS_TABLES_DIR / "deliverables_inventory.txt",
        'project_summary': OUTPUTS_TABLES_DIR / "project_summary.json"
    }
    
    directories = {
        'phase_maps': OUTPUTS_FIGURES_DIR / "phase_maps",
        'ternary_diagrams': OUTPUTS_FIGURES_DIR / "ternary_diagrams",
        'trends': OUTPUTS_FIGURES_DIR / "trends",
        'reaction_paths': OUTPUTS_FIGURES_DIR / "reaction_paths",
        'validation': OUTPUTS_FIGURES_DIR / "validation"
    }
    
    scripts = {
        'phase_map_plotter': SCRIPTS_DIR / "phase_map_plotter.py",
        'ternary_diagram_plotter': SCRIPTS_DIR / "ternary_diagram_plotter.py",
        'trend_plotter': SCRIPTS_DIR / "trend_plotter.py",
        'reaction_path_plotter': SCRIPTS_DIR / "reaction_path_plotter.py",
        'validation': SCRIPTS_DIR / "validation.py",
        'deliverables_manager': SCRIPTS_DIR / "deliverables_manager.py"
    }
    
    results = {}
    
    # Check key files
    print("Key Files:")
    for name, path in deliverables.items():
        exists = path.exists()
        results[name] = exists
        status = "✓" if exists else "✗"
        size = f"({path.stat().st_size/1024:.1f} KB)" if exists else ""
        print(f"  {status} {name} {size}")
    
    print()
    
    # Check figure directories
    print("Figure Directories:")
    for name, path in directories.items():
        if path.exists():
            n_files = len(list(path.glob("*.png")))
            results[name] = n_files > 0
            print(f"  ✓ {name}: {n_files} files")
        else:
            results[name] = False
            print(f"  ✗ {name}: not found")
    
    print()
    
    # Check scripts
    print("Core Scripts:")
    for name, path in scripts.items():
        exists = path.exists()
        results[f"script_{name}"] = exists
        status = "✓" if exists else "✗"
        print(f"  {status} {name}")
    
    return results


def verify_project_readme():
    """
    Verify PROJECT_README.md exists and is comprehensive.
    
    Returns:
        bool: True if README is complete
    """
    print()
    print("="*70)
    print("4. VERIFYING PROJECT README")
    print("="*70)
    
    readme_path = PROJECT_ROOT / "PROJECT_README.md"
    
    if not readme_path.exists():
        print("✗ PROJECT_README.md not found")
        return False
    
    size = readme_path.stat().st_size
    print(f"✓ PROJECT_README.md exists ({size/1024:.1f} KB)")
    
    # Check content
    with open(readme_path, 'r') as f:
        content = f.read()
    
    required_sections = [
        'Project Overview',
        'Quick Start',
        'Project Structure',
        'Completed Phases',
        'Key Results Summary',
        'Software & Database',
        'Methodology',
        'Deliverables Inventory',
        'Usage Examples',
        'Project Status'
    ]
    
    print("\nSections:")
    all_present = True
    for section in required_sections:
        if section in content:
            print(f"  ✓ {section}")
        else:
            print(f"  ✗ {section} missing")
            all_present = False
    
    # Check for completion markers
    print()
    if "PROJECT COMPLETE" in content:
        print("  ✓ Project completion statement present")
    else:
        print("  ✗ Project completion statement missing")
        all_present = False
    
    if "100% convergence" in content or "100.00% convergence" in content:
        print("  ✓ Convergence rate documented")
    else:
        print("  ⚠ Convergence rate not clearly stated")
    
    if "NO mock functions" in content or "no mock functions" in content:
        print("  ✓ No mock functions statement present")
    else:
        print("  ⚠ Mock functions disclaimer not found")
    
    return all_present


def verify_requirements_txt():
    """
    Verify requirements.txt is present and complete.
    
    Returns:
        bool: True if requirements.txt is adequate
    """
    print()
    print("="*70)
    print("5. VERIFYING REQUIREMENTS.TXT")
    print("="*70)
    
    req_path = PROJECT_ROOT / "requirements.txt"
    
    if not req_path.exists():
        print("✗ requirements.txt not found")
        return False
    
    print(f"✓ requirements.txt exists")
    
    # Check for essential packages
    with open(req_path, 'r') as f:
        content = f.read().lower()
    
    required_packages = [
        'numpy',
        'pandas',
        'matplotlib',
        'scipy',
        'python-ternary'
    ]
    
    print("\nRequired packages:")
    all_present = True
    for package in required_packages:
        if package.lower() in content:
            print(f"  ✓ {package}")
        else:
            print(f"  ✗ {package} missing")
            all_present = False
    
    return all_present


def calculate_project_statistics():
    """
    Calculate and display comprehensive project statistics.
    
    Returns:
        dict: Project statistics
    """
    print()
    print("="*70)
    print("6. PROJECT STATISTICS")
    print("="*70)
    print()
    
    # Count all outputs
    tables_dir = OUTPUTS_TABLES_DIR
    figures_dir = OUTPUTS_FIGURES_DIR
    scripts_dir = SCRIPTS_DIR
    
    # Datasets
    csv_files = list(tables_dir.glob("*.csv"))
    txt_files = list(tables_dir.glob("*.txt"))
    json_files = list(tables_dir.glob("*.json"))
    
    n_datasets = len(csv_files) + len(txt_files) + len(json_files)
    
    dataset_size = sum(f.stat().st_size for f in csv_files + txt_files + json_files)
    
    # Figures
    png_files = list(figures_dir.glob("**/*.png"))
    n_figures = len(png_files)
    figures_size = sum(f.stat().st_size for f in png_files)
    
    # Scripts
    py_files = list(scripts_dir.glob("*.py"))
    n_scripts = len(py_files)
    
    total_lines = 0
    for py_file in py_files:
        with open(py_file, 'r') as f:
            total_lines += len(f.readlines())
    
    scripts_size = sum(f.stat().st_size for f in py_files)
    
    # Calculate totals
    total_size = dataset_size + figures_size + scripts_size
    
    stats = {
        'datasets': {
            'count': n_datasets,
            'size_mb': dataset_size / 1024 / 1024
        },
        'figures': {
            'count': n_figures,
            'size_mb': figures_size / 1024 / 1024
        },
        'scripts': {
            'count': n_scripts,
            'lines': total_lines,
            'size_mb': scripts_size / 1024 / 1024
        },
        'total_size_mb': total_size / 1024 / 1024
    }
    
    print("Datasets:")
    print(f"  Files: {stats['datasets']['count']}")
    print(f"  Size: {stats['datasets']['size_mb']:.2f} MB")
    print()
    
    print("Figures:")
    print(f"  Files: {stats['figures']['count']}")
    print(f"  Size: {stats['figures']['size_mb']:.2f} MB")
    print()
    
    print("Scripts:")
    print(f"  Files: {stats['scripts']['count']}")
    print(f"  Lines: {stats['scripts']['lines']:,}")
    print(f"  Size: {stats['scripts']['size_mb']:.2f} MB")
    print()
    
    print(f"Total Project Size: {stats['total_size_mb']:.2f} MB")
    
    return stats


def main():
    """
    Main verification function for Phase 12.
    """
    print()
    print("="*70)
    print("PHASE 12 VERIFICATION: DATA EXPORT & VISUALIZATION PIPELINE")
    print("="*70)
    print()
    
    # Run all verifications
    results = []
    
    results.append(("Deliverables inventory", verify_deliverables_inventory()))
    results.append(("Project summary", verify_project_summary()))
    
    deliverables_check = verify_all_deliverables()
    all_deliverables = all(deliverables_check.values())
    results.append(("All deliverables", all_deliverables))
    
    results.append(("Project README", verify_project_readme()))
    results.append(("Requirements.txt", verify_requirements_txt()))
    
    # Calculate statistics
    stats = calculate_project_statistics()
    
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
        print("✓✓✓ PHASE 12 VERIFICATION: ALL TESTS PASSED ✓✓✓")
        print()
        print("Project Deliverables Summary:")
        print(f"  - {stats['datasets']['count']} datasets ({stats['datasets']['size_mb']:.2f} MB)")
        print(f"  - {stats['figures']['count']} figures ({stats['figures']['size_mb']:.2f} MB)")
        print(f"  - {stats['scripts']['count']} scripts ({stats['scripts']['lines']:,} lines)")
        print(f"  - Total: {stats['total_size_mb']:.2f} MB")
        print()
        print("PROJECT STATUS: COMPLETE AND READY FOR DELIVERY")
    else:
        print("✗✗✗ PHASE 12 VERIFICATION: SOME TESTS FAILED ✗✗✗")
    
    print("="*70)
    print()
    
    return all_passed


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
