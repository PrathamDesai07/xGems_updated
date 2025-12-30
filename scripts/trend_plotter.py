#!/usr/bin/env python3
"""
PHASE 9: PRODUCT EVOLUTION TREND CURVES
========================================
Generates trend curves showing phase amounts vs independent variables.

This module creates two sets of trend curves:
1. Phase amounts vs yCO2 (fixed R, f_FA, w_SS, w_b)
2. Phase amounts vs f_FA (fixed R, yCO2, w_SS, w_b)

Key phases plotted: Calcite, C-S-H, Silica gel, Ettringite, Hydrotalcite

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


class TrendPlotter:
    """
    Creates product evolution trend curves for carbonation system.
    Uses real equilibrium data from 4,928 calculations.
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
        
        print(f"Available phases: {len(self.phase_columns_kg)}")
        for col in self.phase_columns_kg:
            phase_name = col.replace('_kg', '')
            print(f"  - {phase_name}")
    
    def plot_phase_vs_yCO2(self, R, f_FA, w_SS, w_b, 
                           phases=['Calcite', 'C-S-H_1.0', 'Silica_gel'],
                           unit='kg'):
        """
        Plot phase amounts vs yCO2 for fixed R, f_FA, w_SS, w_b.
        
        Args:
            R: Binder-to-aggregate ratio
            f_FA: Fly ash replacement ratio
            w_SS: Sodium silicate dosage
            w_b: Water-to-binder ratio
            phases: List of phase names to plot
            unit: 'kg' or 'mol'
            
        Returns:
            Matplotlib Figure object
        """
        # Filter data
        df_filtered = self.df[
            (self.df['R'] == R) &
            (abs(self.df['f_FA'] - f_FA) < 1e-6) &
            (abs(self.df['w_SS'] - w_SS) < 1e-6) &
            (abs(self.df['w_b'] - w_b) < 1e-6)
        ].copy()
        
        if len(df_filtered) == 0:
            print(f"WARNING: No data for R={R}, f_FA={f_FA}, w_SS={w_SS}, w_b={w_b}")
            return None
        
        # Sort by yCO2
        df_filtered = df_filtered.sort_values('yCO2')
        
        print(f"\n{'='*70}")
        print(f"Plotting phases vs yCO2:")
        print(f"  R = {R}")
        print(f"  f_FA = {f_FA}")
        print(f"  w_SS = {w_SS*100:.1f}%")
        print(f"  w_b = {w_b}")
        print(f"  Data points: {len(df_filtered)}")
        
        # Create figure
        fig, ax = plt.subplots(figsize=(10, 7))
        
        # Define colors and markers
        colors = plt.cm.tab10(np.linspace(0, 1, len(phases)))
        markers = ['o', 's', '^', 'D', 'v', '<', '>', 'p', '*', 'h']
        
        # Plot each phase
        for i, phase in enumerate(phases):
            col_name = f"{phase}_{unit}"
            
            if col_name not in df_filtered.columns:
                print(f"  WARNING: Phase {phase} not found in data")
                continue
            
            # Extract data
            yCO2_values = df_filtered['yCO2'].values * 100  # Convert to percentage
            phase_amounts = df_filtered[col_name].values
            
            # Plot
            ax.plot(yCO2_values, phase_amounts, 
                   marker=markers[i % len(markers)], 
                   markersize=8,
                   linewidth=2,
                   color=colors[i],
                   label=phase.replace('_', ' '),
                   alpha=0.8)
            
            print(f"  ✓ Plotted {phase}: range [{phase_amounts.min():.4f}, {phase_amounts.max():.4f}] {unit}")
        
        # Formatting
        ax.set_xlabel('CO₂ Concentration (%)', fontsize=14, fontweight='bold')
        ax.set_ylabel(f'Phase Amount ({unit})', fontsize=14, fontweight='bold')
        
        title = f"Phase Evolution vs CO₂ Concentration\n"
        title += f"R={R}, f_FA={f_FA}, w_SS={w_SS*100:.1f}%, w/b={w_b}"
        ax.set_title(title, fontsize=15, fontweight='bold', pad=15)
        
        ax.legend(loc='best', fontsize=11, framealpha=0.9)
        ax.grid(True, alpha=0.3, linestyle='--')
        ax.set_xlim(left=-2)
        ax.set_ylim(bottom=0)
        
        plt.tight_layout()
        
        return fig
    
    def plot_phase_vs_f_FA(self, R, yCO2, w_SS, w_b,
                          phases=['Calcite', 'C-S-H_1.0', 'Silica_gel'],
                          unit='kg'):
        """
        Plot phase amounts vs f_FA for fixed R, yCO2, w_SS, w_b.
        
        Args:
            R: Binder-to-aggregate ratio
            yCO2: CO2 concentration
            w_SS: Sodium silicate dosage
            w_b: Water-to-binder ratio
            phases: List of phase names to plot
            unit: 'kg' or 'mol'
            
        Returns:
            Matplotlib Figure object
        """
        # Filter data
        df_filtered = self.df[
            (self.df['R'] == R) &
            (abs(self.df['yCO2'] - yCO2) < 1e-6) &
            (abs(self.df['w_SS'] - w_SS) < 1e-6) &
            (abs(self.df['w_b'] - w_b) < 1e-6)
        ].copy()
        
        if len(df_filtered) == 0:
            print(f"WARNING: No data for R={R}, yCO2={yCO2}, w_SS={w_SS}, w_b={w_b}")
            return None
        
        # Sort by f_FA
        df_filtered = df_filtered.sort_values('f_FA')
        
        print(f"\n{'='*70}")
        print(f"Plotting phases vs f_FA:")
        print(f"  R = {R}")
        print(f"  yCO2 = {yCO2*100:.0f}%")
        print(f"  w_SS = {w_SS*100:.1f}%")
        print(f"  w_b = {w_b}")
        print(f"  Data points: {len(df_filtered)}")
        
        # Create figure
        fig, ax = plt.subplots(figsize=(10, 7))
        
        # Define colors and markers
        colors = plt.cm.tab10(np.linspace(0, 1, len(phases)))
        markers = ['o', 's', '^', 'D', 'v', '<', '>', 'p', '*', 'h']
        
        # Plot each phase
        for i, phase in enumerate(phases):
            col_name = f"{phase}_{unit}"
            
            if col_name not in df_filtered.columns:
                print(f"  WARNING: Phase {phase} not found in data")
                continue
            
            # Extract data
            f_FA_values = df_filtered['f_FA'].values
            phase_amounts = df_filtered[col_name].values
            
            # Plot
            ax.plot(f_FA_values, phase_amounts,
                   marker=markers[i % len(markers)],
                   markersize=8,
                   linewidth=2,
                   color=colors[i],
                   label=phase.replace('_', ' '),
                   alpha=0.8)
            
            print(f"  ✓ Plotted {phase}: range [{phase_amounts.min():.4f}, {phase_amounts.max():.4f}] {unit}")
        
        # Formatting
        ax.set_xlabel('Fly Ash Replacement Ratio (f_FA)', fontsize=14, fontweight='bold')
        ax.set_ylabel(f'Phase Amount ({unit})', fontsize=14, fontweight='bold')
        
        title = f"Phase Evolution vs Fly Ash Content\n"
        title += f"R={R}, yCO2={yCO2*100:.0f}%, w_SS={w_SS*100:.1f}%, w/b={w_b}"
        ax.set_title(title, fontsize=15, fontweight='bold', pad=15)
        
        ax.legend(loc='best', fontsize=11, framealpha=0.9)
        ax.grid(True, alpha=0.3, linestyle='--')
        ax.set_xlim([-0.05, 1.05])
        ax.set_ylim(bottom=0)
        
        plt.tight_layout()
        
        return fig
    
    def create_multi_panel_yCO2_trends(self, R_values, f_FA, w_SS, w_b,
                                       phases=['Calcite', 'C-S-H_1.0', 'Silica_gel'],
                                       unit='kg'):
        """
        Create multi-panel figure with yCO2 trends for multiple R values.
        
        Args:
            R_values: List of R values
            f_FA: Fixed fly ash replacement ratio
            w_SS: Fixed sodium silicate dosage
            w_b: Fixed water-to-binder ratio
            phases: List of phases to plot
            unit: 'kg' or 'mol'
            
        Returns:
            Matplotlib Figure object
        """
        n_panels = len(R_values)
        n_cols = 2
        n_rows = (n_panels + n_cols - 1) // n_cols
        
        fig, axes = plt.subplots(n_rows, n_cols, figsize=(16, 6*n_rows))
        if n_panels == 1:
            axes = np.array([axes])
        axes = axes.flatten()
        
        colors = plt.cm.tab10(np.linspace(0, 1, len(phases)))
        markers = ['o', 's', '^', 'D', 'v']
        
        for idx, R in enumerate(R_values):
            ax = axes[idx]
            
            # Filter data
            df_filtered = self.df[
                (self.df['R'] == R) &
                (abs(self.df['f_FA'] - f_FA) < 1e-6) &
                (abs(self.df['w_SS'] - w_SS) < 1e-6) &
                (abs(self.df['w_b'] - w_b) < 1e-6)
            ].copy().sort_values('yCO2')
            
            if len(df_filtered) == 0:
                continue
            
            # Plot phases
            for i, phase in enumerate(phases):
                col_name = f"{phase}_{unit}"
                if col_name not in df_filtered.columns:
                    continue
                
                yCO2_values = df_filtered['yCO2'].values * 100
                phase_amounts = df_filtered[col_name].values
                
                ax.plot(yCO2_values, phase_amounts,
                       marker=markers[i % len(markers)],
                       markersize=7,
                       linewidth=2,
                       color=colors[i],
                       label=phase.replace('_', ' '),
                       alpha=0.8)
            
            # Formatting
            ax.set_xlabel('CO₂ Concentration (%)', fontsize=12, fontweight='bold')
            ax.set_ylabel(f'Phase Amount ({unit})', fontsize=12, fontweight='bold')
            ax.set_title(f'R = {R}', fontsize=13, fontweight='bold')
            ax.legend(loc='best', fontsize=10)
            ax.grid(True, alpha=0.3, linestyle='--')
            ax.set_xlim(left=-2)
            ax.set_ylim(bottom=0)
        
        # Hide unused subplots
        for idx in range(n_panels, len(axes)):
            axes[idx].axis('off')
        
        # Overall title
        fig.suptitle(f'Phase Evolution vs CO₂ (f_FA={f_FA}, w_SS={w_SS*100:.1f}%, w/b={w_b})',
                    fontsize=16, fontweight='bold', y=0.995)
        
        plt.tight_layout(rect=[0, 0, 1, 0.99])
        
        return fig
    
    def create_multi_panel_f_FA_trends(self, R_values, yCO2_values, w_SS, w_b,
                                       phases=['Calcite', 'C-S-H_1.0', 'Silica_gel'],
                                       unit='kg'):
        """
        Create multi-panel figure with f_FA trends for multiple R and yCO2 combinations.
        
        Args:
            R_values: List of R values
            yCO2_values: List of yCO2 values
            w_SS: Fixed sodium silicate dosage
            w_b: Fixed water-to-binder ratio
            phases: List of phases to plot
            unit: 'kg' or 'mol'
            
        Returns:
            Matplotlib Figure object
        """
        n_R = len(R_values)
        n_yCO2 = len(yCO2_values)
        
        fig, axes = plt.subplots(n_R, n_yCO2, figsize=(7*n_yCO2, 5*n_R))
        if n_R == 1 and n_yCO2 == 1:
            axes = np.array([[axes]])
        elif n_R == 1:
            axes = axes.reshape(1, -1)
        elif n_yCO2 == 1:
            axes = axes.reshape(-1, 1)
        
        colors = plt.cm.tab10(np.linspace(0, 1, len(phases)))
        markers = ['o', 's', '^', 'D', 'v']
        
        for i, R in enumerate(R_values):
            for j, yCO2 in enumerate(yCO2_values):
                ax = axes[i, j]
                
                # Filter data
                df_filtered = self.df[
                    (self.df['R'] == R) &
                    (abs(self.df['yCO2'] - yCO2) < 1e-6) &
                    (abs(self.df['w_SS'] - w_SS) < 1e-6) &
                    (abs(self.df['w_b'] - w_b) < 1e-6)
                ].copy().sort_values('f_FA')
                
                if len(df_filtered) == 0:
                    continue
                
                # Plot phases
                for k, phase in enumerate(phases):
                    col_name = f"{phase}_{unit}"
                    if col_name not in df_filtered.columns:
                        continue
                    
                    f_FA_values = df_filtered['f_FA'].values
                    phase_amounts = df_filtered[col_name].values
                    
                    ax.plot(f_FA_values, phase_amounts,
                           marker=markers[k % len(markers)],
                           markersize=6,
                           linewidth=2,
                           color=colors[k],
                           label=phase.replace('_', ' '),
                           alpha=0.8)
                
                # Formatting
                ax.set_xlabel('f_FA', fontsize=11, fontweight='bold')
                ax.set_ylabel(f'{unit}', fontsize=11, fontweight='bold')
                ax.set_title(f'R={R}, yCO2={yCO2*100:.0f}%', fontsize=12, fontweight='bold')
                if i == 0 and j == 0:
                    ax.legend(loc='best', fontsize=9)
                ax.grid(True, alpha=0.3, linestyle='--')
                ax.set_xlim([-0.05, 1.05])
                ax.set_ylim(bottom=0)
        
        # Overall title
        fig.suptitle(f'Phase Evolution vs Fly Ash Content (w_SS={w_SS*100:.1f}%, w/b={w_b})',
                    fontsize=16, fontweight='bold', y=0.995)
        
        plt.tight_layout(rect=[0, 0, 1, 0.99])
        
        return fig
    
    def generate_all_trends(self, output_dir=None):
        """
        Generate all trend curve figures.
        
        Args:
            output_dir: Output directory for figures (default: outputs/figures/trends/)
        """
        if output_dir is None:
            output_dir = OUTPUTS_FIGURES_DIR / "trends"
        output_dir.mkdir(parents=True, exist_ok=True)
        
        print("="*70)
        print("GENERATING PRODUCT EVOLUTION TREND CURVES")
        print("="*70)
        print()
        
        # Fixed parameters
        w_SS = 0.03  # 3%
        w_b = 1.4
        
        # Key phases to plot
        phases = ['Calcite', 'C-S-H_1.0', 'Silica_gel', 'Ettringite', 'Hydrotalcite']
        
        figures_created = 0
        
        # 1. Calcite vs yCO2 for different f_FA at R=0.6
        print("1. Generating Calcite vs yCO2 trends for different f_FA...")
        for f_FA in [0.0, 0.3, 0.6, 0.9]:
            fig = self.plot_phase_vs_yCO2(
                R=0.6, f_FA=f_FA, w_SS=w_SS, w_b=w_b,
                phases=['Calcite'], unit='kg'
            )
            if fig:
                filename = f"calcite_vs_yCO2_R0.6_fFA{f_FA}.png"
                fig.savefig(output_dir / filename, dpi=300, bbox_inches='tight')
                plt.close(fig)
                print(f"  Saved: {filename}")
                figures_created += 1
        
        # 2. Multiple phases vs yCO2 for R=0.6, f_FA=0.5
        print("\n2. Generating multi-phase vs yCO2 trends...")
        fig = self.plot_phase_vs_yCO2(
            R=0.6, f_FA=0.5, w_SS=w_SS, w_b=w_b,
            phases=phases, unit='kg'
        )
        if fig:
            filename = f"phases_vs_yCO2_R0.6_fFA0.5.png"
            fig.savefig(output_dir / filename, dpi=300, bbox_inches='tight')
            plt.close(fig)
            print(f"  Saved: {filename}")
            figures_created += 1
        
        # 3. Multi-panel yCO2 trends for different R values
        print("\n3. Generating multi-panel yCO2 trends...")
        fig = self.create_multi_panel_yCO2_trends(
            R_values=[0.3, 0.6, 0.9, 1.2],
            f_FA=0.5, w_SS=w_SS, w_b=w_b,
            phases=phases, unit='kg'
        )
        if fig:
            filename = f"phases_vs_yCO2_all_R_fFA0.5.png"
            fig.savefig(output_dir / filename, dpi=300, bbox_inches='tight')
            plt.close(fig)
            print(f"  Saved: {filename}")
            figures_created += 1
        
        # 4. Calcite vs f_FA for different yCO2 at R=0.6
        print("\n4. Generating Calcite vs f_FA trends for different yCO2...")
        for yCO2 in [0.0, 0.20, 0.40]:
            fig = self.plot_phase_vs_f_FA(
                R=0.6, yCO2=yCO2, w_SS=w_SS, w_b=w_b,
                phases=['Calcite'], unit='kg'
            )
            if fig:
                filename = f"calcite_vs_fFA_R0.6_yCO2{int(yCO2*100)}pct.png"
                fig.savefig(output_dir / filename, dpi=300, bbox_inches='tight')
                plt.close(fig)
                print(f"  Saved: {filename}")
                figures_created += 1
        
        # 5. Multiple phases vs f_FA for R=0.6, yCO2=20%
        print("\n5. Generating multi-phase vs f_FA trends...")
        fig = self.plot_phase_vs_f_FA(
            R=0.6, yCO2=0.20, w_SS=w_SS, w_b=w_b,
            phases=phases, unit='kg'
        )
        if fig:
            filename = f"phases_vs_fFA_R0.6_yCO220pct.png"
            fig.savefig(output_dir / filename, dpi=300, bbox_inches='tight')
            plt.close(fig)
            print(f"  Saved: {filename}")
            figures_created += 1
        
        # 6. Multi-panel f_FA trends
        print("\n6. Generating multi-panel f_FA trends...")
        fig = self.create_multi_panel_f_FA_trends(
            R_values=[0.6, 1.2],
            yCO2_values=[0.0, 0.20, 0.40],
            w_SS=w_SS, w_b=w_b,
            phases=phases, unit='kg'
        )
        if fig:
            filename = f"phases_vs_fFA_multi_panel.png"
            fig.savefig(output_dir / filename, dpi=300, bbox_inches='tight')
            plt.close(fig)
            print(f"  Saved: {filename}")
            figures_created += 1
        
        print()
        print("="*70)
        print("TREND CURVE GENERATION COMPLETE")
        print("="*70)
        print(f"Generated {figures_created} trend curve figures")
        print(f"Saved to: {output_dir}")
        print()
        
        return figures_created


def main():
    """
    Main execution function for Phase 9: Product Evolution Trend Curves.
    """
    print()
    print("="*70)
    print("PHASE 9: PRODUCT EVOLUTION TREND CURVES")
    print("="*70)
    print()
    
    # Path to classified dataset
    classified_dataset_path = OUTPUTS_TABLES_DIR / "master_dataset_classified.csv"
    
    # Initialize plotter
    plotter = TrendPlotter(classified_dataset_path)
    
    # Generate all trends
    plotter.generate_all_trends()
    
    print()
    print("="*70)
    print("PHASE 9 - PRODUCT EVOLUTION TREND CURVES COMPLETE")
    print("="*70)
    print()
    print("Generated trend curves:")
    print("  - Calcite vs yCO2 (multiple f_FA values)")
    print("  - Multi-phase vs yCO2 (5 phases)")
    print("  - Multi-panel comparison (all R values)")
    print("  - Calcite vs f_FA (multiple yCO2 values)")
    print("  - Multi-phase vs f_FA (5 phases)")
    print("  - Multi-panel f_FA trends (2 R × 3 yCO2)")
    print()
    print("All figures saved to: outputs/figures/trends/")
    print()


if __name__ == "__main__":
    main()
