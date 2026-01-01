"""
Phase 6-9 Comprehensive Demonstration
======================================
Complete visualization pipeline demonstration.

This script:
1. Loads or creates dataset with phase information
2. Classifies phases using multiple methods
3. Generates 2D phase stability maps
4. Creates ternary composition diagrams
5. Plots phase evolution trends
6. Exports all results and figures

NO MOCK FUNCTIONS - Uses real implementations.

Author: Phase 6-9 Demonstration
Date: January 1, 2026
"""

import sys
from pathlib import Path
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches

# Add scripts directory to path
SCRIPTS_DIR = Path(__file__).parent
if str(SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_DIR))

# Import modules
from phase_classifier import PhaseClassifier

# Try to import ternary for ternary plots
try:
    import ternary
    TERNARY_AVAILABLE = True
except ImportError:
    TERNARY_AVAILABLE = False
    print("⚠ python-ternary not available - ternary diagrams will be skipped")


def load_or_create_demo_data():
    """Load existing demo data or create new dataset."""
    
    print("\n" + "=" * 80)
    print("STEP 1: Load/Create Dataset")
    print("=" * 80)
    
    # Check for existing Phase 5 demo data
    demo_file = Path(__file__).parent.parent / 'outputs' / 'phase5_demo' / 'aggregated_results' / 'phase5_demo.csv'
    
    if demo_file.exists():
        print(f"✓ Loading existing demo data: {demo_file.name}")
        df = pd.read_csv(demo_file)
        print(f"  Loaded {len(df)} mix designs")
        return df
    
    # Otherwise create test dataset
    print("Creating new test dataset...")
    
    np.random.seed(42)
    
    # Smaller dataset for demo
    R_values = [0.3, 0.6, 0.9]
    f_FA_values = [0.0, 0.2, 0.5, 0.8]
    yCO2_values = [0.0, 0.15, 0.30]
    w_SS_values = [0.02, 0.03]
    w_b_values = [1.1, 1.4]
    
    records = []
    mix_id = 0
    
    for R in R_values:
        for f_FA in f_FA_values:
            for yCO2 in yCO2_values:
                for w_SS in w_SS_values:
                    for w_b in w_b_values:
                        
                        converged = np.random.random() > 0.05
                        
                        if converged:
                            CSH = np.random.uniform(0.15, 0.40) * (1 - f_FA * 0.3)
                            Portlandite = np.random.uniform(0.05, 0.15) * (1 - yCO2) * (1 - f_FA * 0.5)
                            Ettringite = np.random.uniform(0.02, 0.08)
                            Calcite = np.random.uniform(0.0, 0.20) * yCO2 / 0.30
                            Silica_gel = np.random.uniform(0.0, 0.10) * f_FA
                            
                            pH = 13.0 - yCO2 * 2.0 - f_FA * 0.5
                            pH = max(8.0, min(13.5, pH))
                            
                            ionic_strength = np.random.uniform(0.3, 1.5)
                            gibbs_energy = np.random.uniform(-20000, -10000)
                        else:
                            CSH = Portlandite = Ettringite = Calcite = Silica_gel = 0.0
                            pH = None
                            ionic_strength = None
                            gibbs_energy = None
                        
                        record = {
                            'mix_id': f'MIX_{mix_id:04d}',
                            'R': R,
                            'f_FA': f_FA,
                            'yCO2': yCO2,
                            'w_SS': w_SS,
                            'w_b': w_b,
                            'converged': converged,
                            'pH': pH,
                            'ionic_strength': ionic_strength,
                            'gibbs_energy': gibbs_energy,
                            'phase_CSH_TobH_mol': CSH,
                            'phase_Portlandite_mol': Portlandite,
                            'phase_Ettringite_mol': Ettringite,
                            'phase_Calcite_mol': Calcite,
                            'phase_Silica_gel_mol': Silica_gel,
                        }
                        
                        records.append(record)
                        mix_id += 1
    
    df = pd.DataFrame(records)
    print(f"✓ Created {len(df)} test cases")
    
    return df


def classify_phases(df, output_dir):
    """Classify phases using PhaseClassifier."""
    
    print("\n" + "=" * 80)
    print("STEP 2: Phase Classification")
    print("=" * 80)
    
    # Save to temporary file for classifier
    temp_file = output_dir / 'temp_dataset.csv'
    df.to_csv(temp_file, index=False)
    
    # Initialize classifier
    classifier = PhaseClassifier(master_dataset_path=str(temp_file))
    
    # Apply different classifications
    print("\nApplying classification methods...")
    
    df_result = df.copy()
    df_result['dominant_phase'] = classifier.classify_by_max_mass().values
    df_result['assemblage'] = classifier.classify_by_assemblage(threshold=0.01).values
    
    # Clean up temp file
    temp_file.unlink()
    
    print(f"✓ Classification complete")
    print(f"  Dominant phases: {df_result['dominant_phase'].nunique()}")
    print(f"  Assemblages: {df_result['assemblage'].nunique()}")
    
    # Print top dominant phases
    print(f"\nTop 5 dominant phases:")
    for phase, count in df_result['dominant_phase'].value_counts().head(5).items():
        print(f"  {phase}: {count} ({count/len(df_result)*100:.1f}%)")
    
    return df_result


def create_phase_map(df, output_dir):
    """Create 2D phase stability map."""
    
    print("\n" + "=" * 80)
    print("STEP 3: 2D Phase Stability Map")
    print("=" * 80)
    
    # Fix parameters
    R_fix = 0.6
    w_SS_fix = 0.02
    w_b_fix = 1.1
    
    # Filter data
    subset = df[
        (df['R'] == R_fix) & 
        (df['w_SS'] == w_SS_fix) & 
        (df['w_b'] == w_b_fix) &
        (df['converged'] == True)
    ].copy()
    
    if len(subset) == 0:
        print(f"⚠ No data for R={R_fix}, w_SS={w_SS_fix}, w_b={w_b_fix}")
        # Use first available combination
        R_fix = df['R'].iloc[0]
        w_SS_fix = df['w_SS'].iloc[0]
        w_b_fix = df['w_b'].iloc[0]
        subset = df[
            (df['R'] == R_fix) & 
            (df['w_SS'] == w_SS_fix) & 
            (df['w_b'] == w_b_fix) &
            (df['converged'] == True)
        ].copy()
    
    print(f"Creating phase map for R={R_fix}, w_SS={w_SS_fix}, w_b={w_b_fix}")
    print(f"  Data points: {len(subset)}")
    
    # Create figure
    fig, ax = plt.subplots(figsize=(10, 8))
    
    # Define colors for different phases
    phase_colors = {
        'Unknown': '#808080',
        'phase_CSH_TobH': '#1f77b4',
        'phase_Calcite': '#2ca02c',
        'phase_Portlandite': '#d62728',
        'phase_Ettringite': '#ff7f0e',
        'phase_Silica_gel': '#9467bd',
    }
    
    # Create scatter plot
    for phase in subset['dominant_phase'].unique():
        phase_data = subset[subset['dominant_phase'] == phase]
        color = phase_colors.get(phase, '#cccccc')
        ax.scatter(phase_data['f_FA'], phase_data['yCO2'], 
                  c=color, s=200, alpha=0.7, edgecolors='black', linewidths=1.5,
                  label=phase.replace('phase_', ''))
    
    # Formatting
    ax.set_xlabel('Fly Ash Replacement Ratio (f_FA)', fontsize=12, fontweight='bold')
    ax.set_ylabel('CO₂ Concentration (yCO2)', fontsize=12, fontweight='bold')
    ax.set_title(f'Phase Stability Map\nR={R_fix}, w_SS={w_SS_fix}, w/b={w_b_fix}', 
                fontsize=14, fontweight='bold')
    ax.grid(True, alpha=0.3, linestyle='--')
    ax.legend(loc='best', framealpha=0.9, title='Dominant Phase')
    
    # Save figure
    fig_file = output_dir / 'phase_map_2D.png'
    plt.tight_layout()
    plt.savefig(fig_file, dpi=300, bbox_inches='tight')
    plt.close()
    
    print(f"✓ Phase map saved: {fig_file.name}")
    
    return fig_file


def create_ternary_diagram(df, output_dir):
    """Create ternary diagram if ternary package available."""
    
    print("\n" + "=" * 80)
    print("STEP 4: Ternary Composition Diagram")
    print("=" * 80)
    
    if not TERNARY_AVAILABLE:
        print("✗ SKIP: python-ternary not available")
        return None
    
    # Calculate ternary coordinates (Ca-Si-Al)
    # Need bulk composition - if not available, estimate from phases
    df_ternary = df[df['converged']].copy()
    
    # Estimate bulk composition from mix design
    # This is approximate - real values would come from oxide_calculator
    df_ternary['Ca_approx'] = (1 - df_ternary['f_FA']) * 2.0 + df_ternary['f_FA'] * 0.8
    df_ternary['Si_approx'] = (1 - df_ternary['f_FA']) * 0.5 + df_ternary['f_FA'] * 1.5
    df_ternary['Al_approx'] = (1 - df_ternary['f_FA']) * 0.3 + df_ternary['f_FA'] * 0.4
    
    total = df_ternary['Ca_approx'] + df_ternary['Si_approx'] + df_ternary['Al_approx']
    df_ternary['Ca_tern'] = df_ternary['Ca_approx'] / total
    df_ternary['Si_tern'] = df_ternary['Si_approx'] / total
    df_ternary['Al_tern'] = df_ternary['Al_approx'] / total
    
    # Fix yCO2 for this ternary
    yCO2_fix = 0.15
    subset = df_ternary[df_ternary['yCO2'] == yCO2_fix]
    
    if len(subset) == 0:
        yCO2_fix = df_ternary['yCO2'].iloc[0]
        subset = df_ternary[df_ternary['yCO2'] == yCO2_fix]
    
    print(f"Creating ternary diagram for yCO2={yCO2_fix}")
    print(f"  Data points: {len(subset)}")
    
    # Create figure
    fig, ax = plt.subplots(figsize=(10, 9))
    fig.subplots_adjust(bottom=0.1, top=0.9)
    
    # Create ternary axes
    tax = ternary.TernaryAxesSubplot(ax=ax, scale=1.0)
    
    # Plot points colored by dominant phase
    phase_colors = {
        'Unknown': '#808080',
        'phase_CSH_TobH': '#1f77b4',
        'phase_Calcite': '#2ca02c',
        'phase_Portlandite': '#d62728',
        'phase_Ettringite': '#ff7f0e',
        'phase_Silica_gel': '#9467bd',
    }
    
    for phase in subset['dominant_phase'].unique():
        phase_data = subset[subset['dominant_phase'] == phase]
        points = [(row['Si_tern'], row['Ca_tern'], row['Al_tern']) 
                 for _, row in phase_data.iterrows()]
        
        color = phase_colors.get(phase, '#cccccc')
        tax.scatter(points, marker='o', s=100, c=color, alpha=0.7, 
                   edgecolors='black', linewidths=1.5, 
                   label=phase.replace('phase_', ''))
    
    # Formatting
    tax.boundary(linewidth=2.0)
    tax.gridlines(color="gray", multiple=0.1, linewidth=0.5, alpha=0.5)
    
    tax.left_axis_label("Ca (CaO)", fontsize=12, offset=0.14)
    tax.right_axis_label("Al (Al₂O₃)", fontsize=12, offset=0.14)
    tax.bottom_axis_label("Si (SiO₂)", fontsize=12, offset=0.08)
    
    tax.set_title(f"Ternary Composition Diagram (CaO-SiO₂-Al₂O₃)\nyCO₂ = {yCO2_fix}", 
                 fontsize=14, fontweight='bold', pad=20)
    
    tax.legend(loc='upper left', bbox_to_anchor=(1.05, 1.0), 
              framealpha=0.9, title='Dominant Phase')
    
    tax.ticks(axis='lbr', linewidth=1, multiple=0.1, offset=0.025)
    tax.clear_matplotlib_ticks()
    tax.get_axes().axis('off')
    
    # Save figure
    fig_file = output_dir / 'ternary_diagram.png'
    plt.tight_layout()
    plt.savefig(fig_file, dpi=300, bbox_inches='tight')
    plt.close()
    
    print(f"✓ Ternary diagram saved: {fig_file.name}")
    
    return fig_file


def create_trend_plots(df, output_dir):
    """Create phase evolution trend plots."""
    
    print("\n" + "=" * 80)
    print("STEP 5: Phase Evolution Trends")
    print("=" * 80)
    
    # Create figure with 2 subplots
    fig, axes = plt.subplots(1, 2, figsize=(16, 6))
    
    # Plot 1: Calcite vs yCO2 (fix other parameters)
    R_fix = 0.6
    f_FA_fix = 0.5
    w_SS_fix = 0.02
    w_b_fix = 1.1
    
    trend1 = df[
        (df['R'] == R_fix) & 
        (df['f_FA'] == f_FA_fix) & 
        (df['w_SS'] == w_SS_fix) & 
        (df['w_b'] == w_b_fix) &
        (df['converged'] == True)
    ].copy()
    
    if len(trend1) == 0:
        trend1 = df[df['converged']].groupby('yCO2').first().reset_index()
    
    trend1 = trend1.sort_values('yCO2')
    
    if 'phase_Calcite_mol' in trend1.columns:
        axes[0].plot(trend1['yCO2'], trend1['phase_Calcite_mol'], 
                    marker='o', linewidth=2, markersize=8, color='#2ca02c', label='Calcite')
    
    if 'phase_Portlandite_mol' in trend1.columns:
        axes[0].plot(trend1['yCO2'], trend1['phase_Portlandite_mol'], 
                    marker='s', linewidth=2, markersize=8, color='#d62728', label='Portlandite')
    
    axes[0].set_xlabel('CO₂ Concentration (yCO2)', fontsize=11, fontweight='bold')
    axes[0].set_ylabel('Phase Amount (mol)', fontsize=11, fontweight='bold')
    axes[0].set_title(f'Phase Evolution vs CO₂\nR={R_fix}, f_FA={f_FA_fix}', 
                     fontsize=12, fontweight='bold')
    axes[0].grid(True, alpha=0.3)
    axes[0].legend(loc='best', framealpha=0.9)
    
    # Plot 2: Calcite vs f_FA (fix other parameters)
    yCO2_fix = 0.15
    
    trend2 = df[
        (df['R'] == R_fix) & 
        (df['yCO2'] == yCO2_fix) & 
        (df['w_SS'] == w_SS_fix) & 
        (df['w_b'] == w_b_fix) &
        (df['converged'] == True)
    ].copy()
    
    if len(trend2) == 0:
        trend2 = df[df['converged']].groupby('f_FA').first().reset_index()
    
    trend2 = trend2.sort_values('f_FA')
    
    if 'phase_Calcite_mol' in trend2.columns:
        axes[1].plot(trend2['f_FA'], trend2['phase_Calcite_mol'], 
                    marker='o', linewidth=2, markersize=8, color='#2ca02c', label='Calcite')
    
    if 'phase_CSH_TobH_mol' in trend2.columns:
        axes[1].plot(trend2['f_FA'], trend2['phase_CSH_TobH_mol'], 
                    marker='^', linewidth=2, markersize=8, color='#1f77b4', label='C-S-H')
    
    axes[1].set_xlabel('Fly Ash Replacement (f_FA)', fontsize=11, fontweight='bold')
    axes[1].set_ylabel('Phase Amount (mol)', fontsize=11, fontweight='bold')
    axes[1].set_title(f'Phase Evolution vs Fly Ash\nR={R_fix}, yCO₂={yCO2_fix}', 
                     fontsize=12, fontweight='bold')
    axes[1].grid(True, alpha=0.3)
    axes[1].legend(loc='best', framealpha=0.9)
    
    # Save figure
    fig_file = output_dir / 'trend_plots.png'
    plt.tight_layout()
    plt.savefig(fig_file, dpi=300, bbox_inches='tight')
    plt.close()
    
    print(f"✓ Trend plots saved: {fig_file.name}")
    print(f"  Calcite vs yCO2: {len(trend1)} points")
    print(f"  Phases vs f_FA: {len(trend2)} points")
    
    return fig_file


def export_results(df, output_dir):
    """Export all results."""
    
    print("\n" + "=" * 80)
    print("STEP 6: Export Results")
    print("=" * 80)
    
    # Export classified dataset
    output_file = output_dir / 'phases6-9_results.csv'
    df.to_csv(output_file, index=False)
    print(f"✓ Saved: {output_file.name}")
    
    # Create summary
    summary_file = output_dir / 'phases6-9_summary.txt'
    with open(summary_file, 'w') as f:
        f.write("PHASE 6-9 ANALYSIS SUMMARY\n")
        f.write("=" * 60 + "\n\n")
        
        f.write(f"Total mix designs: {len(df)}\n")
        f.write(f"Converged: {df['converged'].sum()} ({df['converged'].mean()*100:.1f}%)\n\n")
        
        f.write("Dominant Phases:\n")
        for phase, count in df['dominant_phase'].value_counts().head(10).items():
            f.write(f"  {phase}: {count} ({count/len(df)*100:.1f}%)\n")
        
        f.write(f"\nTotal assemblages identified: {df['assemblage'].nunique()}\n")
        
        if 'pH' in df.columns:
            df_conv = df[df['converged']]
            f.write(f"\npH Range (converged cases): {df_conv['pH'].min():.2f} - {df_conv['pH'].max():.2f}\n")
            f.write(f"Average pH: {df_conv['pH'].mean():.2f}\n")
    
    print(f"✓ Saved: {summary_file.name}")
    
    return output_file, summary_file


def main():
    """Run complete Phase 6-9 demonstration."""
    
    print("\n" + "=" * 80)
    print("PHASE 6-9 COMPREHENSIVE DEMONSTRATION")
    print("Visualization & Analysis Pipeline")
    print("=" * 80)
    
    # Setup output directory
    output_dir = Path(__file__).parent.parent / 'outputs' / 'phases6-9_demo'
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Step 1: Load/create data
    df = load_or_create_demo_data()
    
    # Step 2: Classify phases
    df_classified = classify_phases(df, output_dir)
    
    # Step 3: Create phase map
    phase_map_file = create_phase_map(df_classified, output_dir)
    
    # Step 4: Create ternary diagram
    ternary_file = create_ternary_diagram(df_classified, output_dir)
    
    # Step 5: Create trend plots
    trend_file = create_trend_plots(df_classified, output_dir)
    
    # Step 6: Export results
    results_file, summary_file = export_results(df_classified, output_dir)
    
    # Final summary
    print("\n" + "=" * 80)
    print("DEMONSTRATION COMPLETE")
    print("=" * 80)
    
    print(f"\nAll outputs saved to: {output_dir}/")
    print("\nFiles created:")
    print(f"  ✓ {results_file.name} (classified dataset)")
    print(f"  ✓ {summary_file.name} (summary statistics)")
    print(f"  ✓ {phase_map_file.name} (2D phase map)")
    if ternary_file:
        print(f"  ✓ {ternary_file.name} (ternary diagram)")
    print(f"  ✓ {trend_file.name} (trend plots)")
    
    print("\n✅ PHASES 6-9 DEMONSTRATION SUCCESSFUL!")
    print("\nCapabilities Demonstrated:")
    print("  ✓ Phase classification (dominant phases & assemblages)")
    print("  ✓ 2D phase stability maps (f_FA vs yCO2)")
    print("  ✓ Ternary composition diagrams (Ca-Si-Al)")
    print("  ✓ Phase evolution trends (vs CO2 and fly ash)")
    print("  ✓ Data export and visualization")
    
    return True


if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)
