#!/usr/bin/env python3
"""
PHASE 10: REACTION-PATH SIMULATIONS
====================================
Simulates stepwise carbonation process for representative mix designs.

This module generates reaction-path curves showing phase evolution as CO₂
is gradually added to the system. Uses existing equilibrium data at different
yCO2 levels to represent stepwise carbonation progression.

Representative mixes selected:
- Mix 1: Low f_FA (0.1) - cement-dominated system
- Mix 2: Medium f_FA (0.5) - balanced cement/fly ash
- Mix 3: High f_FA (0.9) - fly ash-dominated system

NO mock functions - all data from real equilibrium calculations.
"""

import sys
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path

# Add project root to path
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from config import OUTPUTS_FIGURES_DIR, OUTPUTS_TABLES_DIR


class ReactionPathPlotter:
    """
    Creates reaction-path evolution curves for stepwise carbonation.
    Uses real equilibrium data to simulate progressive CO₂ addition.
    """
    
    def __init__(self, classified_dataset_path):
        """
        Initialize plotter with classified dataset.
        
        Args:
            classified_dataset_path: Path to master_dataset_classified.csv
        """
        print(f"Loading classified dataset from {classified_dataset_path}...")
        self.df = pd.read_csv(classified_dataset_path)
        print(f"Loaded {len(self.df)} equilibrium cases")
        
        # Identify available phase columns
        self.phase_columns_kg = [col for col in self.df.columns if col.endswith('_kg')]
        self.phase_columns_mol = [col for col in self.df.columns if col.endswith('_mol')]
        
        print(f"Available phases for reaction paths: {len(self.phase_columns_kg)}")
        for col in self.phase_columns_kg:
            phase_name = col.replace('_kg', '')
            print(f"  - {phase_name}")
    
    def extract_reaction_path_data(self, R, f_FA, w_SS, w_b):
        """
        Extract reaction path data for a specific mix design.
        
        This simulates stepwise carbonation by using equilibrium states
        at progressively higher CO₂ concentrations.
        
        Args:
            R: Binder-to-aggregate ratio
            f_FA: Fly ash replacement ratio
            w_SS: Sodium silicate dosage
            w_b: Water-to-binder ratio
            
        Returns:
            DataFrame with reaction path data sorted by yCO2
        """
        # Filter data for this mix design
        df_path = self.df[
            (self.df['R'] == R) &
            (abs(self.df['f_FA'] - f_FA) < 1e-6) &
            (abs(self.df['w_SS'] - w_SS) < 1e-6) &
            (abs(self.df['w_b'] - w_b) < 1e-6)
        ].copy()
        
        # Sort by yCO2 (reaction progress)
        df_path = df_path.sort_values('yCO2')
        
        return df_path
    
    def plot_reaction_path(self, R, f_FA, w_SS, w_b, 
                          phases=['Calcite', 'C-S-H_1.0', 'Silica_gel', 'Ettringite', 'Hydrotalcite'],
                          unit='kg',
                          show_pH=True):
        """
        Plot reaction path showing phase evolution during stepwise carbonation.
        
        Args:
            R: Binder-to-aggregate ratio
            f_FA: Fly ash replacement ratio
            w_SS: Sodium silicate dosage
            w_b: Water-to-binder ratio
            phases: List of phase names to plot
            unit: 'kg' or 'mol'
            show_pH: Whether to show pH evolution on secondary axis
            
        Returns:
            Matplotlib Figure object
        """
        # Get reaction path data
        df_path = self.extract_reaction_path_data(R, f_FA, w_SS, w_b)
        
        if len(df_path) == 0:
            print(f"WARNING: No data for R={R}, f_FA={f_FA}, w_SS={w_SS}, w_b={w_b}")
            return None
        
        print(f"\n{'='*70}")
        print(f"Reaction Path - Stepwise Carbonation:")
        print(f"  R = {R}")
        print(f"  f_FA = {f_FA}")
        print(f"  w_SS = {w_SS*100:.1f}%")
        print(f"  w_b = {w_b}")
        print(f"  CO₂ steps: {len(df_path)} (yCO2: {df_path['yCO2'].min():.2f} → {df_path['yCO2'].max():.2f})")
        
        # Create figure with optional pH axis
        if show_pH:
            fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 10), 
                                          height_ratios=[3, 1])
        else:
            fig, ax1 = plt.subplots(figsize=(12, 7))
        
        # Extract data
        yCO2_values = df_path['yCO2'].values * 100  # Convert to percentage
        
        # Define colors and markers
        colors = plt.cm.tab10(np.linspace(0, 1, len(phases)))
        markers = ['o', 's', '^', 'D', 'v', '<', '>', 'p', '*', 'h']
        
        # Plot phase evolution
        for i, phase in enumerate(phases):
            col_name = f"{phase}_{unit}"
            
            if col_name not in df_path.columns:
                print(f"  WARNING: Phase {phase} not found in data")
                continue
            
            phase_amounts = df_path[col_name].values
            
            # Plot on main axis
            ax1.plot(yCO2_values, phase_amounts,
                    marker=markers[i % len(markers)],
                    markersize=10,
                    linewidth=2.5,
                    color=colors[i],
                    label=phase.replace('_', ' '),
                    alpha=0.85,
                    markeredgewidth=1.5,
                    markeredgecolor='black')
            
            # Print evolution summary
            initial = phase_amounts[0]
            final = phase_amounts[-1]
            change = final - initial
            print(f"  {phase}: {initial:.4f} → {final:.4f} {unit} (Δ = {change:+.4f})")
        
        # Format main axis
        ax1.set_xlabel('CO₂ Concentration (%)', fontsize=14, fontweight='bold')
        ax1.set_ylabel(f'Phase Amount ({unit})', fontsize=14, fontweight='bold')
        
        title = f"Reaction Path: Stepwise Carbonation\n"
        title += f"R={R}, f_FA={f_FA}, w_SS={w_SS*100:.1f}%, w/b={w_b}"
        ax1.set_title(title, fontsize=15, fontweight='bold', pad=15)
        
        ax1.legend(loc='best', fontsize=11, framealpha=0.95, 
                  edgecolor='black', fancybox=True)
        ax1.grid(True, alpha=0.4, linestyle='--', linewidth=0.8)
        ax1.set_xlim(left=-2)
        ax1.set_ylim(bottom=0)
        
        # Add annotation for reaction progress
        ax1.annotate('Reaction Progress →', 
                    xy=(0.5, 0.98), xycoords='axes fraction',
                    ha='center', va='top', fontsize=12, 
                    style='italic', color='gray')
        
        # Plot pH evolution if requested
        if show_pH:
            pH_values = df_path['pH'].values
            
            ax2.plot(yCO2_values, pH_values,
                    marker='o',
                    markersize=8,
                    linewidth=2.5,
                    color='darkred',
                    alpha=0.85,
                    markeredgewidth=1.5,
                    markeredgecolor='black')
            
            ax2.set_xlabel('CO₂ Concentration (%)', fontsize=14, fontweight='bold')
            ax2.set_ylabel('pH', fontsize=14, fontweight='bold', color='darkred')
            ax2.tick_params(axis='y', labelcolor='darkred')
            ax2.grid(True, alpha=0.4, linestyle='--', linewidth=0.8)
            ax2.set_xlim(left=-2)
            
            # Add pH range reference lines
            ax2.axhline(y=7, color='gray', linestyle=':', alpha=0.5, label='Neutral pH')
            ax2.axhline(y=10, color='orange', linestyle=':', alpha=0.5, label='Alkaline threshold')
            ax2.legend(loc='best', fontsize=9)
            
            print(f"  pH: {pH_values[0]:.2f} → {pH_values[-1]:.2f} (Δ = {pH_values[-1]-pH_values[0]:+.2f})")
        
        plt.tight_layout()
        
        return fig
    
    def create_comparison_reaction_paths(self, R, f_FA_values, w_SS, w_b,
                                        phases=['Calcite', 'C-S-H_1.0', 'Silica_gel'],
                                        unit='kg'):
        """
        Create multi-panel comparison of reaction paths for different f_FA values.
        
        Args:
            R: Fixed binder-to-aggregate ratio
            f_FA_values: List of f_FA values to compare
            w_SS: Fixed sodium silicate dosage
            w_b: Fixed water-to-binder ratio
            phases: List of phases to plot
            unit: 'kg' or 'mol'
            
        Returns:
            Matplotlib Figure object
        """
        n_mixes = len(f_FA_values)
        fig, axes = plt.subplots(n_mixes, 1, figsize=(12, 6*n_mixes))
        
        if n_mixes == 1:
            axes = [axes]
        
        colors = plt.cm.tab10(np.linspace(0, 1, len(phases)))
        markers = ['o', 's', '^', 'D', 'v']
        
        for idx, f_FA in enumerate(f_FA_values):
            ax = axes[idx]
            
            # Get reaction path data
            df_path = self.extract_reaction_path_data(R, f_FA, w_SS, w_b)
            
            if len(df_path) == 0:
                continue
            
            yCO2_values = df_path['yCO2'].values * 100
            
            # Plot each phase
            for i, phase in enumerate(phases):
                col_name = f"{phase}_{unit}"
                
                if col_name not in df_path.columns:
                    continue
                
                phase_amounts = df_path[col_name].values
                
                ax.plot(yCO2_values, phase_amounts,
                       marker=markers[i % len(markers)],
                       markersize=8,
                       linewidth=2,
                       color=colors[i],
                       label=phase.replace('_', ' '),
                       alpha=0.8,
                       markeredgewidth=1,
                       markeredgecolor='black')
            
            # Format subplot
            ax.set_xlabel('CO₂ Concentration (%)', fontsize=12, fontweight='bold')
            ax.set_ylabel(f'Phase Amount ({unit})', fontsize=12, fontweight='bold')
            ax.set_title(f'f_FA = {f_FA} ({"Cement-rich" if f_FA < 0.3 else "Balanced" if f_FA < 0.7 else "Fly ash-rich"})', 
                        fontsize=13, fontweight='bold')
            ax.legend(loc='best', fontsize=10)
            ax.grid(True, alpha=0.3, linestyle='--')
            ax.set_xlim(left=-2)
            ax.set_ylim(bottom=0)
        
        # Overall title
        fig.suptitle(f'Reaction Path Comparison: R={R}, w_SS={w_SS*100:.1f}%, w/b={w_b}',
                    fontsize=16, fontweight='bold', y=0.995)
        
        plt.tight_layout(rect=[0, 0, 1, 0.99])
        
        return fig
    
    def generate_all_reaction_paths(self, output_dir=None):
        """
        Generate all reaction path figures for representative mixes.
        
        Args:
            output_dir: Output directory (default: outputs/figures/reaction_paths/)
        """
        if output_dir is None:
            output_dir = OUTPUTS_FIGURES_DIR / "reaction_paths"
        output_dir.mkdir(parents=True, exist_ok=True)
        
        # Also create CSV output directory
        csv_output_dir = OUTPUTS_TABLES_DIR / "reaction_paths"
        csv_output_dir.mkdir(parents=True, exist_ok=True)
        
        print("="*70)
        print("GENERATING REACTION-PATH SIMULATIONS")
        print("="*70)
        print()
        
        # Fixed parameters
        R = 0.6
        w_SS = 0.03
        w_b = 1.4
        
        # Representative mixes: low, medium, high fly ash
        representative_mixes = [
            (0.1, "Low f_FA (Cement-dominated)"),
            (0.5, "Medium f_FA (Balanced)"),
            (0.9, "High f_FA (Fly ash-dominated)")
        ]
        
        phases = ['Calcite', 'C-S-H_1.0', 'Silica_gel', 'Ettringite', 'Hydrotalcite']
        
        figures_created = 0
        
        # 1. Generate individual reaction paths with pH
        print("1. Generating individual reaction paths with pH evolution...")
        for f_FA, description in representative_mixes:
            print(f"\n  Processing: {description}")
            
            fig = self.plot_reaction_path(
                R=R, f_FA=f_FA, w_SS=w_SS, w_b=w_b,
                phases=phases, unit='kg', show_pH=True
            )
            
            if fig:
                filename = f"reaction_path_R{R}_fFA{f_FA}_pH.png"
                fig.savefig(output_dir / filename, dpi=300, bbox_inches='tight')
                plt.close(fig)
                print(f"  Saved: {filename}")
                figures_created += 1
            
            # Save reaction path data to CSV
            df_path = self.extract_reaction_path_data(R, f_FA, w_SS, w_b)
            if len(df_path) > 0:
                csv_filename = f"reaction_path_data_R{R}_fFA{f_FA}.csv"
                csv_path = csv_output_dir / csv_filename
                
                # Select relevant columns
                output_cols = ['mix_id', 'R', 'f_FA', 'yCO2', 'w_SS', 'w_b', 'pH'] + self.phase_columns_kg
                df_path[output_cols].to_csv(csv_path, index=False)
                print(f"  Saved data: {csv_filename}")
        
        # 2. Generate comparison figure
        print("\n2. Generating comparison figure for all representative mixes...")
        
        f_FA_values = [mix[0] for mix in representative_mixes]
        fig = self.create_comparison_reaction_paths(
            R=R, f_FA_values=f_FA_values,
            w_SS=w_SS, w_b=w_b,
            phases=phases, unit='kg'
        )
        
        if fig:
            filename = f"reaction_paths_comparison_R{R}.png"
            fig.savefig(output_dir / filename, dpi=300, bbox_inches='tight')
            plt.close(fig)
            print(f"  Saved: {filename}")
            figures_created += 1
        
        # 3. Generate individual plots without pH for focused view
        print("\n3. Generating focused reaction paths (phases only)...")
        for f_FA, description in representative_mixes:
            fig = self.plot_reaction_path(
                R=R, f_FA=f_FA, w_SS=w_SS, w_b=w_b,
                phases=phases, unit='kg', show_pH=False
            )
            
            if fig:
                filename = f"reaction_path_R{R}_fFA{f_FA}_phases.png"
                fig.savefig(output_dir / filename, dpi=300, bbox_inches='tight')
                plt.close(fig)
                print(f"  Saved: {filename}")
                figures_created += 1
        
        print()
        print("="*70)
        print("REACTION-PATH GENERATION COMPLETE")
        print("="*70)
        print(f"Generated {figures_created} reaction path figures")
        print(f"Saved figures to: {output_dir}")
        print(f"Saved data tables to: {csv_output_dir}")
        print()
        
        return figures_created


def main():
    """
    Main execution function for Phase 10: Reaction-Path Simulations.
    """
    print()
    print("="*70)
    print("PHASE 10: REACTION-PATH SIMULATIONS")
    print("="*70)
    print()
    
    # Path to classified dataset
    classified_dataset_path = OUTPUTS_TABLES_DIR / "master_dataset_classified.csv"
    
    # Initialize plotter
    plotter = ReactionPathPlotter(classified_dataset_path)
    
    # Generate all reaction paths
    plotter.generate_all_reaction_paths()
    
    print()
    print("="*70)
    print("PHASE 10 - REACTION-PATH SIMULATIONS COMPLETE")
    print("="*70)
    print()
    print("Generated reaction path outputs:")
    print("  - 3 representative mixes (f_FA = 0.1, 0.5, 0.9)")
    print("  - Individual paths with pH evolution")
    print("  - Individual paths (phases only)")
    print("  - Comparison figure (all 3 mixes)")
    print("  - CSV data tables for each mix")
    print()
    print("Simulated stepwise carbonation:")
    print("  - CO₂ progression: 0% → 40% (7 steps)")
    print("  - 5 phases tracked: Calcite, C-S-H, Silica gel, Ettringite, Hydrotalcite")
    print("  - pH evolution monitored")
    print()
    print("All outputs saved to:")
    print("  - Figures: outputs/figures/reaction_paths/")
    print("  - Data: outputs/tables/reaction_paths/")
    print()


if __name__ == "__main__":
    main()
