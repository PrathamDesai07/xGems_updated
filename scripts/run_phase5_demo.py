"""
Phase 5 Integration Demo
========================
Demonstrate complete output parsing and data aggregation workflow.

This script:
1. Creates sample CemGEMS output files
2. Parses them using CemGEMSOutputParser
3. Aggregates data using DataAggregator
4. Exports results to multiple formats

Author: Phase 5 Integration
Date: January 1, 2026
"""

import sys
from pathlib import Path
import json
import pandas as pd
import numpy as np

# Add scripts directory to path
SCRIPTS_DIR = Path(__file__).parent
if str(SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_DIR))

from cemgems_output_parser import CemGEMSOutputParser, DataAggregator
import config


def create_sample_outputs(output_dir: Path, num_samples: int = 10):
    """Create sample CemGEMS output files for demonstration."""
    
    print("\n" + "=" * 80)
    print("STEP 1: Creating Sample Output Files")
    print("=" * 80)
    
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Generate realistic sample data
    np.random.seed(42)
    
    for i in range(num_samples):
        mix_id = f"MIX_{i:04d}"
        
        # Simulate varying convergence and results
        converged = np.random.random() > 0.1  # 90% convergence rate
        
        if converged:
            # Realistic phase assemblage for hydrated cement
            phases = {
                'Portlandite': np.random.uniform(0.05, 0.15),
                'CSH_TobH': np.random.uniform(0.20, 0.40),
                'Ettringite': np.random.uniform(0.02, 0.08),
                'Monosulfate': np.random.uniform(0.01, 0.05),
                'Calcite': np.random.uniform(0.00, 0.10),
                'Monocarboaluminate': np.random.uniform(0.00, 0.03),
            }
            
            pH = np.random.uniform(12.0, 13.0)
            ionic_strength = np.random.uniform(0.3, 1.5)
            gibbs_energy = np.random.uniform(-20000, -10000)
            
        else:
            phases = {}
            pH = None
            ionic_strength = None
            gibbs_energy = None
        
        # Create output data
        output_data = {
            'converged': converged,
            'phases': phases,
            'bulk_composition': {
                'Ca': np.random.uniform(1.0, 2.0),
                'Si': np.random.uniform(0.5, 1.5),
                'Al': np.random.uniform(0.2, 0.5),
                'Fe': np.random.uniform(0.05, 0.15),
                'Mg': np.random.uniform(0.01, 0.05),
                'K': np.random.uniform(0.01, 0.05),
                'Na': np.random.uniform(0.01, 0.05),
                'S': np.random.uniform(0.05, 0.15),
                'C': np.random.uniform(0.0, 0.5),
                'O': np.random.uniform(3.0, 5.0),
                'H': np.random.uniform(4.0, 6.0),
            },
            'pH': pH,
            'ionic_strength': ionic_strength,
            'temperature_K': 298.15,
            'pressure_bar': 1.01325,
            'gibbs_energy': gibbs_energy
        }
        
        # Write JSON output file
        output_file = output_dir / f"{mix_id}.json"
        with open(output_file, 'w') as f:
            json.dump(output_data, f, indent=2)
    
    print(f"✓ Created {num_samples} sample output files")
    print(f"  Location: {output_dir}")
    
    return output_dir


def create_sample_mix_designs(num_samples: int = 10):
    """Create sample mix design DataFrame."""
    
    print("\n" + "=" * 80)
    print("STEP 2: Creating Sample Mix Designs")
    print("=" * 80)
    
    # Generate sample mix designs
    np.random.seed(42)
    
    mix_ids = [f"MIX_{i:04d}" for i in range(num_samples)]
    
    data = {
        'mix_id': mix_ids,
        'R': np.random.choice([0.25, 0.30, 0.35], num_samples),
        'f_FA': np.random.choice([0.0, 0.1, 0.2], num_samples),
        'yCO2': np.random.choice([0.0, 0.15, 0.30, 0.45], num_samples),
        'w_SS': np.random.choice([0.02, 0.05], num_samples),
        'w_b': np.random.choice([1.1, 1.2, 1.3], num_samples),
    }
    
    df = pd.DataFrame(data)
    
    print(f"✓ Created {num_samples} mix designs")
    print(f"  Variables: R, f_FA, yCO2, w_SS, w_b")
    
    return df


def parse_outputs(output_dir: Path):
    """Parse all output files."""
    
    print("\n" + "=" * 80)
    print("STEP 3: Parsing Output Files")
    print("=" * 80)
    
    parser = CemGEMSOutputParser()
    
    output_files = sorted(output_dir.glob("MIX_*.json"))
    
    parsed_results = []
    
    for output_file in output_files:
        result = parser.parse_output_file(str(output_file))
        result['output_file'] = str(output_file)
        parsed_results.append(result)
    
    print(f"✓ Parsed {len(parsed_results)} output files")
    
    # Validation statistics
    converged = sum(1 for r in parsed_results if r['converged'])
    print(f"  Converged: {converged}/{len(parsed_results)} ({converged/len(parsed_results)*100:.1f}%)")
    
    return parsed_results


def aggregate_data(parsed_results, mix_designs_df, output_dir: Path):
    """Aggregate parsed results with mix designs."""
    
    print("\n" + "=" * 80)
    print("STEP 4: Aggregating Data")
    print("=" * 80)
    
    aggregator = DataAggregator()
    
    # Convert parsed results to DataFrame
    records = []
    
    for result in parsed_results:
        record = {
            'mix_id': Path(result['output_file']).stem,
            'converged': result['converged'],
            'pH': result.get('pH'),
            'ionic_strength': result.get('ionic_strength'),
            'gibbs_energy': result.get('gibbs_energy'),
        }
        
        # Add phase amounts
        for phase, amount in result.get('phases', {}).items():
            record[f'phase_{phase}_mol'] = amount
        
        records.append(record)
    
    df_results = pd.DataFrame(records)
    
    # Merge with mix designs
    df_master = pd.merge(
        mix_designs_df,
        df_results,
        on='mix_id',
        how='left'
    )
    
    print(f"✓ Aggregated {len(df_master)} records")
    print(f"  Columns: {len(df_master.columns)}")
    print(f"  Phase columns: {len([c for c in df_master.columns if c.startswith('phase_')])}")
    
    return df_master


def export_results(df_master, export_dir: Path):
    """Export results to multiple formats."""
    
    print("\n" + "=" * 80)
    print("STEP 5: Exporting Results")
    print("=" * 80)
    
    aggregator = DataAggregator()
    
    # Export
    aggregator.export_results(
        df_master,
        output_dir=str(export_dir),
        prefix='phase5_demo'
    )
    
    # Create long format
    df_long = aggregator.create_long_format(df_master)
    
    # Save long format
    long_file = export_dir / 'phase5_demo_long.csv'
    df_long.to_csv(long_file, index=False)
    print(f"✓ Saved long format: {long_file.name}")
    
    return df_long


def display_summary(df_master, df_long):
    """Display final summary statistics."""
    
    print("\n" + "=" * 80)
    print("STEP 6: Summary Statistics")
    print("=" * 80)
    
    # Overall statistics
    total = len(df_master)
    converged = df_master['converged'].sum()
    
    print(f"\nOverall Statistics:")
    print(f"  Total mix designs: {total}")
    print(f"  Converged: {converged} ({converged/total*100:.1f}%)")
    print(f"  Failed: {total - converged} ({(total-converged)/total*100:.1f}%)")
    
    # pH statistics (converged only)
    df_conv = df_master[df_master['converged']]
    if len(df_conv) > 0:
        print(f"\npH Statistics (converged cases):")
        print(f"  Mean: {df_conv['pH'].mean():.2f}")
        print(f"  Std: {df_conv['pH'].std():.2f}")
        print(f"  Min: {df_conv['pH'].min():.2f}")
        print(f"  Max: {df_conv['pH'].max():.2f}")
    
    # Phase statistics
    phase_cols = [c for c in df_master.columns if c.startswith('phase_') and c.endswith('_mol')]
    
    if phase_cols:
        print(f"\nPhase Statistics:")
        print(f"  Total phases detected: {len(phase_cols)}")
        print(f"  Most common phases:")
        
        for col in sorted(phase_cols)[:5]:
            phase_name = col.replace('phase_', '').replace('_mol', '')
            count = df_master[col].notna().sum()
            if count > 0:
                mean_amount = df_master[col].mean()
                print(f"    {phase_name}: present in {count}/{total} cases (avg: {mean_amount:.4f} mol)")
    
    # Long format statistics
    print(f"\nLong Format Statistics:")
    print(f"  Total phase records: {len(df_long)}")
    print(f"  Unique phases: {df_long['phase_name'].nunique()}")
    print(f"  Unique mixes: {df_long['mix_id'].nunique()}")


def main():
    """Run Phase 5 integration demo."""
    
    print("\n" + "=" * 80)
    print("PHASE 5 INTEGRATION DEMO")
    print("CemGEMS Output Parsing & Data Aggregation")
    print("=" * 80)
    print("\nThis demo illustrates the complete Phase 5 workflow:")
    print("  1. Create sample CemGEMS output files")
    print("  2. Parse outputs using CemGEMSOutputParser")
    print("  3. Aggregate data with mix designs")
    print("  4. Export to multiple formats")
    print("  5. Generate summary statistics")
    
    # Setup directories
    demo_dir = Path(__file__).parent.parent / 'outputs' / 'phase5_demo'
    output_dir = demo_dir / 'cemgems_outputs'
    export_dir = demo_dir / 'aggregated_results'
    
    demo_dir.mkdir(parents=True, exist_ok=True)
    export_dir.mkdir(parents=True, exist_ok=True)
    
    # Run workflow
    num_samples = 10
    
    # Step 1: Create sample outputs
    create_sample_outputs(output_dir, num_samples)
    
    # Step 2: Create sample mix designs
    df_mix_designs = create_sample_mix_designs(num_samples)
    
    # Step 3: Parse outputs
    parsed_results = parse_outputs(output_dir)
    
    # Step 4: Aggregate data
    df_master = aggregate_data(parsed_results, df_mix_designs, output_dir)
    
    # Step 5: Export results
    df_long = export_results(df_master, export_dir)
    
    # Step 6: Display summary
    display_summary(df_master, df_long)
    
    print("\n" + "=" * 80)
    print("DEMO COMPLETE")
    print("=" * 80)
    print(f"\nOutput files saved to:")
    print(f"  {export_dir}/")
    print(f"\nFiles created:")
    print(f"  ✓ phase5_demo.csv (wide format)")
    print(f"  ✓ phase5_demo.xlsx (Excel)")
    print(f"  ✓ phase5_demo_summary.txt (summary)")
    print(f"  ✓ phase5_demo_long.csv (long format)")
    
    print("\n✅ Phase 5 workflow demonstrated successfully!")
    
    return True


if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)
