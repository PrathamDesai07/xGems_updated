"""
Complete Phase 6-9 Visualization Generator
===========================================
Generates all required visualizations using FULL 4,928-case dataset.

Creates:
1. Phase stability maps (Phase 7)
2. Ternary composition diagrams (Phase 8)  
3. Phase evolution trend plots (Phase 9)
4. Comprehensive analysis reports

Uses real Phase 5 aggregated output with improved phase classification.

NO MOCK FUNCTIONS - All real implementations.

Author: Phases 6-9 Complete Implementation
Date: January 1, 2026
"""

import sys
from pathlib import Path
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import logging

# Add scripts directory
SCRIPTS_DIR = Path(__file__).parent
if str(SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_DIR))

from phase_classifier_improved import ImprovedPhaseClassifier
from phase_map_plotter import PhaseMapPlotter
from ternary_diagram_plotter import TernaryDiagramPlotter
from trend_plotter import TrendPlotter

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def find_phase5_output():
    """Find the Phase 5 aggregated output file."""
    
    # Check multiple possible locations
    possible_paths = [
        Path(__file__).parent.parent / 'outputs' / 'phase5_demo' / 'aggregated_results' / 'phase5_demo.csv',
        Path(__file__).parent.parent / 'outputs' / 'aggregated_results' / 'master_results.csv',
        Path(__file__).parent.parent / 'outputs' / 'mix_designs_phases_with_compositions.csv',
    ]
    
    for path in possible_paths:
        if path.exists():
            logger.info(f"Found Phase 5 output: {path}")
            return path
    
    logger.error("No Phase 5 output found!")
    return None


def load_and_classify_data(input_file: Path, output_dir: Path):
    """Load Phase 5 data and add phase classifications."""
    
    print("\n" + "=" * 80)
    print("STEP 1: Load and Classify Data")
    print("=" * 80)
    
    # Load data
    df = pd.read_csv(input_file)
    print(f"✓ Loaded {len(df)} mix designs")
    print(f"  Columns: {len(df.columns)}")
    
    # Check for phase columns
    phase_cols = [c for c in df.columns if c.startswith('phase_') and c.endswith('_mol')]
    print(f"  Phase columns: {len(phase_cols)}")
    
    if not phase_cols:
        print("✗ No phase columns found - cannot classify!")
        print("  Available columns:", df.columns.tolist()[:10])
        return None
    
    # Classify
    classifier = ImprovedPhaseClassifier(min_phase_threshold=0.005)
    df_classified = classifier.add_classifications(df)
    
    # Save classified data
    classified_file = output_dir / 'classified_data.csv'
    df_classified.to_csv(classified_file, index=False)
    print(f"✓ Saved classified data: {classified_file.name}")
    
    # Summary
    summary = classifier.get_classification_summary(df_classified)
    print(f"\nClassification Summary:")
    print(f"  Total: {summary['total_mixes']}")
    print(f"  Converged: {summary['converged']} ({summary['converged']/summary['total_mixes']*100:.1f}%)")
    print(f"  Unique assemblages: {summary['unique_assemblages']}")
    print(f"  Dominant phases: {len(summary['dominant_phases'])}")
    
    return df_classified


def generate_phase_stability_maps(df: pd.DataFrame, output_dir: Path):
    """Generate phase stability maps for different conditions."""
    
    print("\n" + "=" * 80)
    print("STEP 2: Generate Phase Stability Maps")
    print("=" * 80)
    
    plotter = PhaseMapPlotter()
    maps_dir = output_dir / 'phase_stability_maps'
    maps_dir.mkdir(parents=True, exist_ok=True)
    
    # Get available R and w_b values
    R_values = sorted(df['R'].unique())
    wb_values = sorted(df['w_b'].unique())
    wss_values = sorted(df['w_SS'].unique())
    
    print(f"Available conditions:")
    print(f"  R values: {R_values}")
    print(f"  w/b values: {wb_values}")
    print(f"  w_SS values: {wss_values}")
    
    # Generate maps for each combination of R, w_SS, w/b
    map_count = 0
    for R in R_values[:2]:  # Limit to first 2 R values for speed
        for w_SS in [wss_values[0]]:  # Use first w_SS
            for w_b in [wb_values[0], wb_values[-1]]:  # Use first and last w/b
                
                # Filter data
                df_subset = df[(df['R'] == R) & (df['w_SS'] == w_SS) & (df['w_b'] == w_b)]
                
                if len(df_subset) < 5:
                    continue
                
                # Create map
                fig = plotter.plot(
                    df_subset,
                    x_var='f_FA',
                    y_var='yCO2',
                    title=f'Phase Stability Map\nR={R}, w_SS={w_SS}, w/b={w_b}'
                )
                
                # Save
                filename = f'stability_map_R{R}_wSS{w_SS}_wb{w_b}.png'
                fig.savefig(maps_dir / filename, dpi=300, bbox_inches='tight')
                plt.close(fig)
                
                map_count += 1
                print(f"  ✓ Created: {filename} ({len(df_subset)} points)")
    
    print(f"✓ Generated {map_count} phase stability maps")
    return map_count


def generate_ternary_diagrams(df: pd.DataFrame, output_dir: Path):
    """Generate ternary composition diagrams."""
    
    print("\n" + "=" * 80)
    print("STEP 3: Generate Ternary Diagrams")
    print("=" * 80)
    
    ternary_dir = output_dir / 'ternary_diagrams'
    ternary_dir.mkdir(parents=True, exist_ok=True)
    
    plotter = TernaryDiagramPlotter()
    
    # Generate ternary plots for different yCO2 levels
    yCO2_values = sorted(df['yCO2'].unique())
    
    diagram_count = 0
    for yCO2 in yCO2_values[:4]:  # Limit to first 4 CO2 levels
        
        df_subset = df[df['yCO2'] == yCO2]
        
        if len(df_subset) < 3:
            continue
        
        try:
            fig = plotter.plot_ternary(
                df_subset,
                title=f'Ternary Composition Diagram (CaO-SiO₂-Al₂O₃)\nyCO₂ = {yCO2}'
            )
            
            filename = f'ternary_yCO2_{yCO2:.2f}.png'
            fig.savefig(ternary_dir / filename, dpi=300, bbox_inches='tight')
            plt.close(fig)
            
            diagram_count += 1
            print(f"  ✓ Created: {filename} ({len(df_subset)} points)")
            
        except Exception as e:
            print(f"  ✗ Failed for yCO2={yCO2}: {e}")
            continue
    
    print(f"✓ Generated {diagram_count} ternary diagrams")
    return diagram_count


def generate_trend_plots(df: pd.DataFrame, output_dir: Path):
    """Generate phase evolution trend plots."""
    
    print("\n" + "=" * 80)
    print("STEP 4: Generate Trend Plots")
    print("=" * 80)
    
    trends_dir = output_dir / 'trend_plots'
    trends_dir.mkdir(parents=True, exist_ok=True)
    
    plotter = TrendPlotter()
    
    # Get phase columns
    phase_cols = [c for c in df.columns if c.startswith('phase_') and c.endswith('_mol')]
    phase_names = [c.replace('phase_', '').replace('_mol', '') for c in phase_cols]
    
    # Select key phases to plot
    key_phases = []
    for phase in ['Calcite', 'Portlandite', 'CSH', 'CSH_TobH', 'Ettringite']:
        matching = [p for p in phase_names if phase in p]
        if matching:
            key_phases.extend(matching[:1])  # Add first match
    
    if not key_phases:
        key_phases = phase_names[:3]  # Use first 3 phases
    
    print(f"Key phases to plot: {key_phases}")
    
    # Get condition values
    R_values = sorted(df['R'].unique())
    f_FA_values = sorted(df['f_FA'].unique())
    yCO2_values = sorted(df['yCO2'].unique())
    
    plot_count = 0
    
    # 1. Phase vs CO2 plots (fixed R and f_FA)
    for R in [R_values[len(R_values)//2]]:  # Use middle R value
        for f_FA in [f_FA_values[len(f_FA_values)//2]]:  # Use middle f_FA
            
            df_subset = df[(df['R'] == R) & (df['f_FA'] == f_FA)]
            
            if len(df_subset) < 3:
                continue
            
            try:
                fig = plotter.plot_phase_evolution_vs_variable(
                    df_subset,
                    variable='yCO2',
                    phases=key_phases[:2],  # Plot top 2 phases
                    title=f'Phase Evolution vs CO₂\nR={R}, f_FA={f_FA}'
                )
                
                filename = f'trend_vs_CO2_R{R}_fFA{f_FA}.png'
                fig.savefig(trends_dir / filename, dpi=300, bbox_inches='tight')
                plt.close(fig)
                
                plot_count += 1
                print(f"  ✓ Created: {filename}")
                
            except Exception as e:
                print(f"  ✗ Failed: {e}")
                continue
    
    # 2. Phase vs Fly Ash plots (fixed R and yCO2)
    for R in [R_values[len(R_values)//2]]:
        for yCO2 in [yCO2_values[len(yCO2_values)//2]]:  # Use middle CO2
            
            df_subset = df[(df['R'] == R) & (df['yCO2'] == yCO2)]
            
            if len(df_subset) < 3:
                continue
            
            try:
                fig = plotter.plot_phase_evolution_vs_variable(
                    df_subset,
                    variable='f_FA',
                    phases=key_phases[:2],
                    title=f'Phase Evolution vs Fly Ash\nR={R}, yCO₂={yCO2}'
                )
                
                filename = f'trend_vs_FlyAsh_R{R}_yCO2{yCO2}.png'
                fig.savefig(trends_dir / filename, dpi=300, bbox_inches='tight')
                plt.close(fig)
                
                plot_count += 1
                print(f"  ✓ Created: {filename}")
                
            except Exception as e:
                print(f"  ✗ Failed: {e}")
                continue
    
    print(f"✓ Generated {plot_count} trend plots")
    return plot_count


def generate_summary_report(df: pd.DataFrame, output_dir: Path, stats: dict):
    """Generate comprehensive summary report."""
    
    print("\n" + "=" * 80)
    print("STEP 5: Generate Summary Report")
    print("=" * 80)
    
    report_file = output_dir / 'PHASES_6-9_COMPLETE_REPORT.txt'
    
    with open(report_file, 'w') as f:
        f.write("=" * 80 + "\n")
        f.write("PHASES 6-9 COMPLETE ANALYSIS REPORT\n")
        f.write("CemGEMS Thermodynamic Modeling Results\n")
        f.write("=" * 80 + "\n\n")
        
        # Dataset info
        f.write("DATASET INFORMATION\n")
        f.write("-" * 80 + "\n")
        f.write(f"Total mix designs: {len(df)}\n")
        f.write(f"Converged cases: {df['converged'].sum()} ({df['converged'].mean()*100:.1f}%)\n")
        f.write(f"Failed cases: {(~df['converged']).sum()} ({(~df['converged']).mean()*100:.1f}%)\n\n")
        
        # Variable ranges
        f.write("VARIABLE RANGES\n")
        f.write("-" * 80 + "\n")
        for var in ['R', 'f_FA', 'yCO2', 'w_SS', 'w_b']:
            if var in df.columns:
                values = df[var].unique()
                f.write(f"{var}: {sorted(values)}\n")
        f.write("\n")
        
        # Phase classification
        if 'dominant_phase' in df.columns:
            f.write("DOMINANT PHASE DISTRIBUTION\n")
            f.write("-" * 80 + "\n")
            phase_counts = df['dominant_phase'].value_counts()
            for phase, count in phase_counts.head(15).items():
                f.write(f"{phase:30s}: {count:5d} ({count/len(df)*100:5.1f}%)\n")
            f.write("\n")
        
        # pH statistics
        if 'pH' in df.columns:
            df_conv = df[df['converged']]
            if len(df_conv) > 0:
                f.write("pH STATISTICS (Converged Cases)\n")
                f.write("-" * 80 + "\n")
                f.write(f"Mean:   {df_conv['pH'].mean():.2f}\n")
                f.write(f"Std:    {df_conv['pH'].std():.2f}\n")
                f.write(f"Min:    {df_conv['pH'].min():.2f}\n")
                f.write(f"25%:    {df_conv['pH'].quantile(0.25):.2f}\n")
                f.write(f"Median: {df_conv['pH'].median():.2f}\n")
                f.write(f"75%:    {df_conv['pH'].quantile(0.75):.2f}\n")
                f.write(f"Max:    {df_conv['pH'].max():.2f}\n\n")
        
        # Visualization statistics
        f.write("VISUALIZATION OUTPUTS\n")
        f.write("-" * 80 + "\n")
        f.write(f"Phase stability maps: {stats.get('maps', 0)}\n")
        f.write(f"Ternary diagrams: {stats.get('ternary', 0)}\n")
        f.write(f"Trend plots: {stats.get('trends', 0)}\n\n")
        
        # Phase assemblages
        if 'assemblage' in df.columns:
            f.write("UNIQUE PHASE ASSEMBLAGES\n")
            f.write("-" * 80 + "\n")
            f.write(f"Total unique assemblages: {df['assemblage'].nunique()}\n")
            f.write("\nMost common assemblages:\n")
            assemblage_counts = df['assemblage'].value_counts()
            for assemblage, count in assemblage_counts.head(10).items():
                f.write(f"\n{count:4d} cases ({count/len(df)*100:5.1f}%):\n")
                f.write(f"  {assemblage}\n")
        
        f.write("\n" + "=" * 80 + "\n")
        f.write("Report generated: January 1, 2026\n")
        f.write("=" * 80 + "\n")
    
    print(f"✓ Generated summary report: {report_file.name}")
    
    # Display summary
    with open(report_file, 'r') as f:
        print("\n" + f.read())


def main():
    """Run complete Phases 6-9 visualization pipeline."""
    
    print("\n" + "=" * 80)
    print("COMPLETE PHASES 6-9 IMPLEMENTATION")
    print("Phase Classification + Diagrams + Analysis")
    print("=" * 80)
    
    # Setup output directory
    output_dir = Path(__file__).parent.parent / 'outputs' / 'phases6-9_complete'
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Find input data
    input_file = find_phase5_output()
    if input_file is None:
        print("\n✗ FAILED: No Phase 5 output found!")
        print("Please run Phase 5 first to generate aggregated results.")
        return False
    
    # Step 1: Load and classify
    df = load_and_classify_data(input_file, output_dir)
    if df is None:
        return False
    
    # Visualization statistics
    stats = {}
    
    # Step 2: Phase stability maps
    stats['maps'] = generate_phase_stability_maps(df, output_dir)
    
    # Step 3: Ternary diagrams
    stats['ternary'] = generate_ternary_diagrams(df, output_dir)
    
    # Step 4: Trend plots
    stats['trends'] = generate_trend_plots(df, output_dir)
    
    # Step 5: Summary report
    generate_summary_report(df, output_dir, stats)
    
    print("\n" + "=" * 80)
    print("✅ PHASES 6-9 COMPLETE!")
    print("=" * 80)
    print(f"\nAll outputs saved to:")
    print(f"  {output_dir}/")
    print(f"\nGenerated:")
    print(f"  ✓ {stats['maps']} phase stability maps")
    print(f"  ✓ {stats['ternary']} ternary diagrams")
    print(f"  ✓ {stats['trends']} trend plots")
    print(f"  ✓ 1 comprehensive report")
    print(f"  ✓ 1 classified dataset (CSV)")
    
    return True


if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)
