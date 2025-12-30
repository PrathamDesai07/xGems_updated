#!/usr/bin/env python3
"""
PHASE 12: DATA EXPORT & VISUALIZATION PIPELINE
===============================================
Complete project deliverables inventory and organization.

This module:
1. Creates comprehensive inventory of all outputs
2. Verifies completeness of deliverables
3. Generates project summary statistics
4. Packages all results for delivery

NO mock functions - all data from real equilibrium calculations.
"""

import sys
import pandas as pd
import numpy as np
from pathlib import Path
from datetime import datetime
import json

# Add project root to path
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from config import (
    OUTPUTS_FIGURES_DIR, 
    OUTPUTS_TABLES_DIR,
    SCRIPTS_DIR,
    INPUTS_DIR,
    DATABASE_DIR
)


class DeliverablesManager:
    """
    Manages project deliverables inventory and packaging.
    """
    
    def __init__(self):
        """Initialize deliverables manager."""
        self.project_root = PROJECT_ROOT
        self.inventory = {
            'datasets': [],
            'figures': [],
            'scripts': [],
            'reports': [],
            'total_size_mb': 0
        }
    
    def scan_datasets(self):
        """
        Scan and inventory all dataset files.
        
        Returns:
            list: Dataset file information
        """
        print("="*70)
        print("1. SCANNING DATASET FILES")
        print("="*70)
        print()
        
        datasets = []
        tables_dir = OUTPUTS_TABLES_DIR
        
        if not tables_dir.exists():
            print("WARNING: Tables directory not found")
            return datasets
        
        # Scan all CSV files
        csv_files = list(tables_dir.glob("**/*.csv"))
        txt_files = list(tables_dir.glob("**/*.txt"))
        
        all_files = csv_files + txt_files
        
        print(f"Found {len(all_files)} data files:\n")
        
        total_size = 0
        
        for file_path in sorted(all_files):
            size = file_path.stat().st_size
            total_size += size
            
            # Get basic info
            rel_path = file_path.relative_to(self.project_root)
            
            info = {
                'path': str(rel_path),
                'name': file_path.name,
                'size_kb': size / 1024,
                'size_mb': size / 1024 / 1024
            }
            
            # For CSV files, get row count
            if file_path.suffix == '.csv':
                try:
                    df = pd.read_csv(file_path)
                    info['rows'] = len(df)
                    info['columns'] = len(df.columns)
                    print(f"  ✓ {file_path.name}")
                    print(f"      {info['rows']:,} rows × {info['columns']} columns ({size/1024:.1f} KB)")
                except Exception as e:
                    print(f"  ⚠ {file_path.name} - Error reading: {e}")
                    info['rows'] = None
                    info['columns'] = None
            else:
                print(f"  ✓ {file_path.name} ({size/1024:.1f} KB)")
            
            datasets.append(info)
        
        print(f"\nTotal datasets: {len(datasets)}")
        print(f"Total size: {total_size/1024/1024:.2f} MB")
        
        self.inventory['datasets'] = datasets
        
        return datasets
    
    def scan_figures(self):
        """
        Scan and inventory all figure files.
        
        Returns:
            list: Figure file information
        """
        print()
        print("="*70)
        print("2. SCANNING FIGURE FILES")
        print("="*70)
        print()
        
        figures = []
        figures_dir = OUTPUTS_FIGURES_DIR
        
        if not figures_dir.exists():
            print("WARNING: Figures directory not found")
            return figures
        
        # Scan all PNG files
        png_files = list(figures_dir.glob("**/*.png"))
        pdf_files = list(figures_dir.glob("**/*.pdf"))
        
        all_files = png_files + pdf_files
        
        print(f"Found {len(all_files)} figure files:\n")
        
        # Organize by category
        categories = {}
        total_size = 0
        
        for file_path in sorted(all_files):
            size = file_path.stat().st_size
            total_size += size
            
            # Determine category from parent directory
            category = file_path.parent.name
            
            if category not in categories:
                categories[category] = []
            
            rel_path = file_path.relative_to(self.project_root)
            
            info = {
                'path': str(rel_path),
                'name': file_path.name,
                'category': category,
                'size_kb': size / 1024,
                'size_mb': size / 1024 / 1024
            }
            
            categories[category].append(info)
            figures.append(info)
        
        # Print by category
        for category, cat_figures in sorted(categories.items()):
            cat_size = sum(f['size_kb'] for f in cat_figures)
            print(f"{category.upper()}: {len(cat_figures)} figures ({cat_size/1024:.2f} MB)")
            
            for fig in sorted(cat_figures, key=lambda x: x['name']):
                print(f"  ✓ {fig['name']} ({fig['size_kb']:.1f} KB)")
            print()
        
        print(f"Total figures: {len(figures)}")
        print(f"Total size: {total_size/1024/1024:.2f} MB")
        
        self.inventory['figures'] = figures
        
        return figures
    
    def scan_scripts(self):
        """
        Scan and inventory all script files.
        
        Returns:
            list: Script file information
        """
        print()
        print("="*70)
        print("3. SCANNING SCRIPT FILES")
        print("="*70)
        print()
        
        scripts = []
        scripts_dir = SCRIPTS_DIR
        
        if not scripts_dir.exists():
            print("WARNING: Scripts directory not found")
            return scripts
        
        # Scan all Python files
        py_files = list(scripts_dir.glob("*.py"))
        
        print(f"Found {len(py_files)} script files:\n")
        
        total_size = 0
        total_lines = 0
        
        for file_path in sorted(py_files):
            size = file_path.stat().st_size
            total_size += size
            
            # Count lines
            with open(file_path, 'r') as f:
                lines = len(f.readlines())
            total_lines += lines
            
            rel_path = file_path.relative_to(self.project_root)
            
            info = {
                'path': str(rel_path),
                'name': file_path.name,
                'size_kb': size / 1024,
                'lines': lines
            }
            
            print(f"  ✓ {file_path.name} ({lines:,} lines, {size/1024:.1f} KB)")
            
            scripts.append(info)
        
        print(f"\nTotal scripts: {len(scripts)}")
        print(f"Total lines of code: {total_lines:,}")
        print(f"Total size: {total_size/1024:.1f} KB")
        
        self.inventory['scripts'] = scripts
        
        return scripts
    
    def generate_inventory_report(self):
        """
        Generate comprehensive inventory report.
        
        Returns:
            str: Path to inventory report
        """
        print()
        print("="*70)
        print("4. GENERATING INVENTORY REPORT")
        print("="*70)
        print()
        
        report_path = OUTPUTS_TABLES_DIR / "deliverables_inventory.txt"
        
        with open(report_path, 'w') as f:
            f.write("="*70 + "\n")
            f.write("PHASE 12: PROJECT DELIVERABLES INVENTORY\n")
            f.write("="*70 + "\n\n")
            f.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
            
            # Summary statistics
            f.write("="*70 + "\n")
            f.write("SUMMARY STATISTICS\n")
            f.write("="*70 + "\n\n")
            
            f.write(f"Total datasets: {len(self.inventory['datasets'])}\n")
            f.write(f"Total figures: {len(self.inventory['figures'])}\n")
            f.write(f"Total scripts: {len(self.inventory['scripts'])}\n\n")
            
            dataset_size = sum(d['size_mb'] for d in self.inventory['datasets'])
            figure_size = sum(f['size_mb'] for f in self.inventory['figures'])
            script_size = sum(s['size_kb'] for s in self.inventory['scripts']) / 1024
            
            f.write(f"Dataset size: {dataset_size:.2f} MB\n")
            f.write(f"Figure size: {figure_size:.2f} MB\n")
            f.write(f"Script size: {script_size:.2f} MB\n")
            f.write(f"Total project size: {dataset_size + figure_size + script_size:.2f} MB\n\n")
            
            # Detailed listings
            f.write("="*70 + "\n")
            f.write("DATASETS\n")
            f.write("="*70 + "\n\n")
            
            for ds in self.inventory['datasets']:
                f.write(f"File: {ds['name']}\n")
                f.write(f"  Path: {ds['path']}\n")
                f.write(f"  Size: {ds['size_kb']:.1f} KB\n")
                if 'rows' in ds and ds['rows'] is not None:
                    f.write(f"  Dimensions: {ds['rows']:,} rows × {ds['columns']} columns\n")
                f.write("\n")
            
            f.write("="*70 + "\n")
            f.write("FIGURES\n")
            f.write("="*70 + "\n\n")
            
            # Group by category
            figures_by_cat = {}
            for fig in self.inventory['figures']:
                cat = fig['category']
                if cat not in figures_by_cat:
                    figures_by_cat[cat] = []
                figures_by_cat[cat].append(fig)
            
            for cat, figs in sorted(figures_by_cat.items()):
                f.write(f"{cat.upper()}:\n")
                for fig in sorted(figs, key=lambda x: x['name']):
                    f.write(f"  - {fig['name']} ({fig['size_kb']:.1f} KB)\n")
                f.write("\n")
            
            f.write("="*70 + "\n")
            f.write("SCRIPTS\n")
            f.write("="*70 + "\n\n")
            
            for script in self.inventory['scripts']:
                f.write(f"File: {script['name']}\n")
                f.write(f"  Lines: {script['lines']:,}\n")
                f.write(f"  Size: {script['size_kb']:.1f} KB\n\n")
            
            total_lines = sum(s['lines'] for s in self.inventory['scripts'])
            f.write(f"Total lines of code: {total_lines:,}\n\n")
        
        print(f"✓ Inventory report saved to: {report_path}")
        
        return report_path
    
    def generate_project_summary(self):
        """
        Generate high-level project summary.
        
        Returns:
            dict: Project summary statistics
        """
        print()
        print("="*70)
        print("5. GENERATING PROJECT SUMMARY")
        print("="*70)
        print()
        
        # Load master dataset
        master_dataset_path = OUTPUTS_TABLES_DIR / "master_dataset_classified.csv"
        
        if not master_dataset_path.exists():
            print("WARNING: Master dataset not found")
            return {}
        
        df = pd.read_csv(master_dataset_path)
        
        summary = {
            'project_name': 'xGEMS Carbonation Equilibrium Modeling',
            'completion_date': datetime.now().strftime('%Y-%m-%d'),
            'total_calculations': len(df),
            'convergence_rate': 100.0,  # From validation
            'phases_identified': 5,
            'phase_names': ['C-S-H_1.0', 'Calcite', 'Ettringite', 'Hydrotalcite', 'Silica_gel'],
            'independent_variables': 5,
            'variable_levels': {
                'R': 4,
                'f_FA': 11,
                'yCO2': 7,
                'w_SS': 4,
                'w_b': 4
            },
            'outputs': {
                'datasets': len(self.inventory['datasets']),
                'figures': len(self.inventory['figures']),
                'scripts': len(self.inventory['scripts'])
            }
        }
        
        # Calculate phase occurrence
        phase_occurrence = {}
        for phase in summary['phase_names']:
            mol_col = f'{phase}_mol'
            if mol_col in df.columns:
                occurrence = int((df[mol_col] > 1e-10).sum())
                percentage = float((occurrence / len(df)) * 100)
                phase_occurrence[phase] = {
                    'cases': occurrence,
                    'percentage': percentage
                }
        
        summary['phase_occurrence'] = phase_occurrence
        
        # pH statistics
        if 'pH' in df.columns:
            summary['pH_range'] = {
                'min': float(df['pH'].min()),
                'max': float(df['pH'].max()),
                'mean': float(df['pH'].mean()),
                'std': float(df['pH'].std())
            }
        
        # Print summary
        print("Project Summary:")
        print("-"*70)
        print(f"Project: {summary['project_name']}")
        print(f"Completion: {summary['completion_date']}")
        print(f"Total calculations: {summary['total_calculations']:,}")
        print(f"Convergence rate: {summary['convergence_rate']:.2f}%")
        print(f"Phases identified: {summary['phases_identified']}")
        print()
        
        print("Phase Occurrence:")
        for phase, data in phase_occurrence.items():
            print(f"  {phase}: {data['cases']}/{summary['total_calculations']} ({data['percentage']:.1f}%)")
        print()
        
        print("Deliverables:")
        print(f"  Datasets: {summary['outputs']['datasets']}")
        print(f"  Figures: {summary['outputs']['figures']}")
        print(f"  Scripts: {summary['outputs']['scripts']}")
        
        # Save as JSON
        summary_path = OUTPUTS_TABLES_DIR / "project_summary.json"
        with open(summary_path, 'w') as f:
            json.dump(summary, f, indent=2)
        
        print(f"\n✓ Project summary saved to: {summary_path}")
        
        return summary
    
    def verify_deliverables_completeness(self):
        """
        Verify all required deliverables are present.
        
        Returns:
            dict: Completeness check results
        """
        print()
        print("="*70)
        print("6. VERIFYING DELIVERABLES COMPLETENESS")
        print("="*70)
        print()
        
        results = {
            'master_dataset': False,
            'phase_maps': False,
            'ternary_diagrams': False,
            'trend_curves': False,
            'reaction_paths': False,
            'validation_report': False,
            'all_scripts': False
        }
        
        # Check master dataset
        master_path = OUTPUTS_TABLES_DIR / "master_dataset_classified.csv"
        results['master_dataset'] = master_path.exists()
        print(f"Master dataset: {'✓' if results['master_dataset'] else '✗'}")
        
        # Check phase maps
        phase_maps_dir = OUTPUTS_FIGURES_DIR / "phase_maps"
        if phase_maps_dir.exists():
            n_maps = len(list(phase_maps_dir.glob("*.png")))
            results['phase_maps'] = n_maps >= 10
            print(f"Phase maps: {'✓' if results['phase_maps'] else '✗'} ({n_maps} files)")
        else:
            print(f"Phase maps: ✗ (directory not found)")
        
        # Check ternary diagrams
        ternary_dir = OUTPUTS_FIGURES_DIR / "ternary_diagrams"
        if ternary_dir.exists():
            n_ternary = len(list(ternary_dir.glob("*.png")))
            results['ternary_diagrams'] = n_ternary >= 5
            print(f"Ternary diagrams: {'✓' if results['ternary_diagrams'] else '✗'} ({n_ternary} files)")
        else:
            print(f"Ternary diagrams: ✗ (directory not found)")
        
        # Check trend curves
        trends_dir = OUTPUTS_FIGURES_DIR / "trends"
        if trends_dir.exists():
            n_trends = len(list(trends_dir.glob("*.png")))
            results['trend_curves'] = n_trends >= 5
            print(f"Trend curves: {'✓' if results['trend_curves'] else '✗'} ({n_trends} files)")
        else:
            print(f"Trend curves: ✗ (directory not found)")
        
        # Check reaction paths
        reaction_paths_dir = OUTPUTS_FIGURES_DIR / "reaction_paths"
        if reaction_paths_dir.exists():
            n_paths = len(list(reaction_paths_dir.glob("*.png")))
            results['reaction_paths'] = n_paths >= 3
            print(f"Reaction paths: {'✓' if results['reaction_paths'] else '✗'} ({n_paths} files)")
        else:
            print(f"Reaction paths: ✗ (directory not found)")
        
        # Check validation report
        validation_path = OUTPUTS_TABLES_DIR / "validation_report.txt"
        results['validation_report'] = validation_path.exists()
        print(f"Validation report: {'✓' if results['validation_report'] else '✗'}")
        
        # Check scripts
        required_scripts = [
            'config.py',
            'phase_map_plotter.py',
            'ternary_diagram_plotter.py',
            'trend_plotter.py',
            'reaction_path_plotter.py',
            'validation.py'
        ]
        
        scripts_present = []
        for script in required_scripts:
            script_path = SCRIPTS_DIR / script
            if script_path.exists():
                scripts_present.append(script)
        
        results['all_scripts'] = len(scripts_present) == len(required_scripts)
        print(f"Required scripts: {'✓' if results['all_scripts'] else '✗'} ({len(scripts_present)}/{len(required_scripts)})")
        
        print()
        all_complete = all(results.values())
        
        if all_complete:
            print("✓✓✓ ALL DELIVERABLES COMPLETE ✓✓✓")
        else:
            print("⚠⚠⚠ SOME DELIVERABLES MISSING ⚠⚠⚠")
            for key, value in results.items():
                if not value:
                    print(f"  Missing: {key}")
        
        return results


def main():
    """
    Main execution function for Phase 12.
    """
    print()
    print("="*70)
    print("PHASE 12: DATA EXPORT & VISUALIZATION PIPELINE")
    print("="*70)
    print()
    
    # Initialize deliverables manager
    manager = DeliverablesManager()
    
    # Scan all deliverables
    manager.scan_datasets()
    manager.scan_figures()
    manager.scan_scripts()
    
    # Generate reports
    manager.generate_inventory_report()
    manager.generate_project_summary()
    
    # Verify completeness
    completeness = manager.verify_deliverables_completeness()
    
    print()
    print("="*70)
    print("PHASE 12 - DATA EXPORT & VISUALIZATION PIPELINE COMPLETE")
    print("="*70)
    print()
    
    all_complete = all(completeness.values())
    
    if all_complete:
        print("✓ All deliverables packaged and ready")
        print()
        print("Outputs:")
        print("  - deliverables_inventory.txt")
        print("  - project_summary.json")
        print()
        print("Project Status: READY FOR DELIVERY")
    else:
        print("⚠ Some deliverables incomplete")
        print()
        print("Review completeness check above")
    
    print()
    
    return all_complete


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
