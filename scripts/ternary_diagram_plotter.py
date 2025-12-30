#!/usr/bin/env python3
"""
PHASE 8: TERNARY DIAGRAM GENERATION (TYPE B)
=============================================
Generates CaO-SiO₂-Al₂O₃ ternary phase diagrams for carbonation system.

This module creates ternary diagrams showing phase distributions in the
CaO-SiO₂-Al₂O₃ compositional space for fixed R and yCO2 values.

NO mock functions - all data from real equilibrium calculations.
"""

import sys
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path
import ternary

# Add project root to path
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from config import OUTPUTS_FIGURES_DIR, OUTPUTS_TABLES_DIR, OXIDE_MOLAR_MASSES


class TernaryDiagramPlotter:
    """
    Creates CaO-SiO₂-Al₂O₃ ternary phase diagrams.
    Uses initial bulk oxide composition from real equilibrium data.
    """
    
    def __init__(self, classified_dataset_path, composition_dataset_path):
        """
        Initialize plotter with classified dataset and composition data.
        
        Args:
            classified_dataset_path: Path to master_dataset_classified.csv
            composition_dataset_path: Path to mix_designs_with_compositions.csv
        """
        print(f"Loading classified dataset from {classified_dataset_path}...")
        self.df_classified = pd.read_csv(classified_dataset_path)
        print(f"Loaded {len(self.df_classified)} equilibrium cases")
        
        print(f"Loading composition dataset from {composition_dataset_path}...")
        self.df_composition = pd.read_csv(composition_dataset_path)
        print(f"Loaded {len(self.df_composition)} composition records")
        
        # Merge datasets on mix_id
        self.df = pd.merge(
            self.df_classified,
            self.df_composition[['mix_id', 'Ca_mol', 'Si_mol', 'Al_mol']],
            on='mix_id'
        )
        print(f"Merged dataset: {len(self.df)} records")
        
        # Define color schemes for different classification types
        self.color_schemes = {
            'phase_diagram_class': {
                'Silica-rich': '#1f77b4',           # Blue
                'Calcite + C-S-H': '#ff7f0e',       # Orange
                'Calcite-rich': '#2ca02c',           # Green
                'C-S-H dominant': '#d62728',         # Red
                'C-S-H + Ettringite': '#9467bd',     # Purple
            },
            'carbonation_state': {
                'Uncarbonated': '#e5e5e5',                    # Light gray
                'Low carbonation': '#ffffb2',                 # Light yellow
                'Medium carbonation': '#fecc5c',              # Yellow-orange
                'High carbonation': '#fd8d3c',                # Orange
                'Very high carbonation': '#e31a1c',           # Red
            },
            'csh_silica_class': {
                'Silica dominant': '#1f77b4',        # Blue
                'High silica': '#aec7e8',             # Light blue
                'Balanced': '#ffbb78',                # Light orange
                'C-S-H dominant': '#2ca02c',          # Green
            },
            'pH_regime': {
                'Neutral-alkaline (pH<9.0)': '#ffffb2',       # Light yellow
                'Moderately alkaline (pH 9.0-10.0)': '#fecc5c',  # Yellow-orange
                'Alkaline (pH 10.0-11.0)': '#fd8d3c',         # Orange
                'Highly alkaline (pH>11.0)': '#e31a1c',       # Red
                'Highly alkaline (pH>10.0)': '#e31a1c',       # Red (alternative)
            }
        }
    
    def calculate_ternary_composition(self, Ca_mol, Si_mol, Al_mol):
        """
        Calculate normalized ternary composition for CaO-SiO₂-Al₂O₃.
        
        Args:
            Ca_mol: Moles of Ca
            Si_mol: Moles of Si
            Al_mol: Moles of Al
            
        Returns:
            Tuple of (CaO_frac, SiO2_frac, Al2O3_frac) normalized to sum=1
        """
        # Convert element moles to oxide moles
        # CaO: 1 Ca → 1 CaO
        # SiO₂: 1 Si → 1 SiO₂
        # Al₂O₃: 2 Al → 1 Al₂O₃
        CaO_mol = Ca_mol
        SiO2_mol = Si_mol
        Al2O3_mol = Al_mol / 2.0
        
        # Normalize to sum = 1
        total = CaO_mol + SiO2_mol + Al2O3_mol
        
        if total > 0:
            CaO_frac = CaO_mol / total
            SiO2_frac = SiO2_mol / total
            Al2O3_frac = Al2O3_mol / total
        else:
            CaO_frac = 0
            SiO2_frac = 0
            Al2O3_frac = 0
        
        return (CaO_frac, SiO2_frac, Al2O3_frac)
    
    def create_ternary_diagram(self, R, yCO2, w_SS=0.03, w_b=1.4, 
                               classification_type='phase_diagram_class',
                               scale=100):
        """
        Create ternary diagram for fixed R and yCO2 values.
        
        Args:
            R: Binder-to-aggregate ratio (e.g., 0.6)
            yCO2: CO2 concentration (e.g., 0.20 for 20%)
            w_SS: Sodium silicate dosage (default: 0.03 for 3%)
            w_b: Water-to-binder ratio (default: 1.4)
            classification_type: Type of phase classification to use
            scale: Scale for ternary diagram (default: 100)
            
        Returns:
            Matplotlib Figure object
        """
        # Filter data for specified conditions
        df_filtered = self.df[
            (self.df['R'] == R) &
            (abs(self.df['yCO2'] - yCO2) < 1e-6) &
            (abs(self.df['w_SS'] - w_SS) < 1e-6) &
            (abs(self.df['w_b'] - w_b) < 1e-6)
        ].copy()
        
        if len(df_filtered) == 0:
            print(f"WARNING: No data found for R={R}, yCO2={yCO2}")
            return None
        
        print(f"\n{'='*70}")
        print(f"Creating ternary diagram for:")
        print(f"  R = {R}")
        print(f"  yCO2 = {yCO2*100:.0f}%")
        print(f"  w_SS = {w_SS*100:.1f}%")
        print(f"  w_b = {w_b}")
        print(f"  Classification: {classification_type}")
        print(f"  Data points: {len(df_filtered)}")
        
        # Calculate ternary compositions
        ternary_coords = []
        colors = []
        labels = []
        
        for idx, row in df_filtered.iterrows():
            CaO_frac, SiO2_frac, Al2O3_frac = self.calculate_ternary_composition(
                row['Ca_mol'], row['Si_mol'], row['Al_mol']
            )
            
            # Convert to ternary coordinates (scale * fraction)
            # Ternary library uses (bottom, right, left) = (a, b, c) where a+b+c=scale
            # For CaO-SiO₂-Al₂O₃: (Al₂O₃, SiO₂, CaO)
            ternary_coords.append((
                Al2O3_frac * scale,
                SiO2_frac * scale,
                CaO_frac * scale
            ))
            
            # Get color for this point
            phase_class = row[classification_type]
            color_scheme = self.color_schemes.get(classification_type, {})
            color = color_scheme.get(phase_class, '#808080')  # Default gray
            colors.append(color)
            labels.append(phase_class)
        
        # Create figure
        fig, ax = plt.subplots(figsize=(12, 10))
        
        # Create ternary axes
        tax = ternary.TernaryAxesSubplot(ax=ax, scale=scale)
        
        # Set axis labels (matching ternary coordinate order)
        tax.bottom_axis_label("Al₂O₃ (mol%)", fontsize=14, offset=0.15)
        tax.right_axis_label("SiO₂ (mol%)", fontsize=14, offset=0.15)
        tax.left_axis_label("CaO (mol%)", fontsize=14, offset=0.15)
        
        # Set title
        title = f"Ternary Diagram: CaO-SiO₂-Al₂O₃\n"
        title += f"R={R}, yCO2={yCO2*100:.0f}%, w_SS={w_SS*100:.1f}%, w/b={w_b}"
        tax.set_title(title, fontsize=16, pad=20)
        
        # Plot points
        for coord, color in zip(ternary_coords, colors):
            tax.scatter([coord], marker='o', s=100, c=[color], 
                       edgecolors='black', linewidths=0.5, alpha=0.8, zorder=3)
        
        # Draw grid
        tax.gridlines(multiple=10, color="gray", linewidth=0.5, alpha=0.3)
        tax.boundary(linewidth=1.5)
        tax.clear_matplotlib_ticks()
        tax.get_axes().axis('off')
        
        # Create legend
        unique_labels = []
        unique_colors = []
        for label, color in zip(labels, colors):
            if label not in unique_labels:
                unique_labels.append(label)
                unique_colors.append(color)
        
        # Add legend
        legend_elements = [
            plt.Line2D([0], [0], marker='o', color='w', 
                      markerfacecolor=color, markersize=10,
                      markeredgecolor='black', markeredgewidth=0.5,
                      label=label)
            for label, color in zip(unique_labels, unique_colors)
        ]
        
        ax.legend(handles=legend_elements, loc='upper left', 
                 bbox_to_anchor=(1.05, 1), fontsize=10,
                 title=classification_type.replace('_', ' ').title(),
                 title_fontsize=11, framealpha=0.9)
        
        plt.tight_layout()
        
        return fig, tax
    
    def create_multiple_ternary_diagrams(self, R_values, yCO2_values,
                                         w_SS=0.03, w_b=1.4,
                                         classification_type='phase_diagram_class'):
        """
        Generate ternary diagrams for multiple R and yCO2 combinations.
        
        Args:
            R_values: List of R values
            yCO2_values: List of yCO2 values
            w_SS: Sodium silicate dosage
            w_b: Water-to-binder ratio
            classification_type: Type of phase classification
        """
        output_dir = OUTPUTS_FIGURES_DIR / "ternary_diagrams"
        output_dir.mkdir(parents=True, exist_ok=True)
        
        print("="*70)
        print("GENERATING MULTIPLE TERNARY DIAGRAMS")
        print("="*70)
        
        diagrams_created = 0
        
        for R in R_values:
            for yCO2 in yCO2_values:
                fig, tax = self.create_ternary_diagram(
                    R=R,
                    yCO2=yCO2,
                    w_SS=w_SS,
                    w_b=w_b,
                    classification_type=classification_type
                )
                
                if fig is not None:
                    # Save figure
                    filename = f"ternary_R{R}_yCO2{int(yCO2*100)}pct_wSS{int(w_SS*100)}pct_wb{w_b}_{classification_type}.png"
                    filepath = output_dir / filename
                    fig.savefig(filepath, dpi=300, bbox_inches='tight')
                    plt.close(fig)
                    print(f"Saved ternary diagram to: {filepath}")
                    diagrams_created += 1
        
        print()
        print("="*70)
        print("TERNARY DIAGRAM GENERATION COMPLETE")
        print("="*70)
        print(f"Generated {diagrams_created} ternary diagrams")
        print(f"Saved to: {output_dir}")
        print()
    
    def create_comparison_ternary_figure(self, R, yCO2_values, w_SS=0.03, w_b=1.4,
                                         classification_type='phase_diagram_class'):
        """
        Create multi-panel comparison figure with multiple yCO2 values.
        
        Args:
            R: Fixed R value
            yCO2_values: List of yCO2 values to compare
            w_SS: Sodium silicate dosage
            w_b: Water-to-binder ratio
            classification_type: Type of phase classification
        """
        n_panels = len(yCO2_values)
        n_cols = min(2, n_panels)
        n_rows = (n_panels + n_cols - 1) // n_cols
        
        fig = plt.figure(figsize=(12 * n_cols, 10 * n_rows))
        
        for i, yCO2 in enumerate(yCO2_values):
            # Filter data
            df_filtered = self.df[
                (self.df['R'] == R) &
                (abs(self.df['yCO2'] - yCO2) < 1e-6) &
                (abs(self.df['w_SS'] - w_SS) < 1e-6) &
                (abs(self.df['w_b'] - w_b) < 1e-6)
            ].copy()
            
            if len(df_filtered) == 0:
                continue
            
            # Calculate ternary compositions
            ternary_coords = []
            colors = []
            labels = []
            
            for idx, row in df_filtered.iterrows():
                CaO_frac, SiO2_frac, Al2O3_frac = self.calculate_ternary_composition(
                    row['Ca_mol'], row['Si_mol'], row['Al_mol']
                )
                
                ternary_coords.append((
                    Al2O3_frac * 100,
                    SiO2_frac * 100,
                    CaO_frac * 100
                ))
                
                phase_class = row[classification_type]
                color_scheme = self.color_schemes.get(classification_type, {})
                color = color_scheme.get(phase_class, '#808080')
                colors.append(color)
                labels.append(phase_class)
            
            # Create subplot
            ax = fig.add_subplot(n_rows, n_cols, i + 1)
            tax = ternary.TernaryAxesSubplot(ax=ax, scale=100)
            
            # Labels and title
            tax.bottom_axis_label("Al₂O₃ (mol%)", fontsize=12, offset=0.14)
            tax.right_axis_label("SiO₂ (mol%)", fontsize=12, offset=0.14)
            tax.left_axis_label("CaO (mol%)", fontsize=12, offset=0.14)
            tax.set_title(f"yCO2 = {yCO2*100:.0f}%", fontsize=14, pad=15)
            
            # Plot points
            for coord, color in zip(ternary_coords, colors):
                tax.scatter([coord], marker='o', s=80, c=[color],
                           edgecolors='black', linewidths=0.5, alpha=0.8)
            
            # Grid and boundary
            tax.gridlines(multiple=10, color="gray", linewidth=0.5, alpha=0.3)
            tax.boundary(linewidth=1.5)
            tax.clear_matplotlib_ticks()
            tax.get_axes().axis('off')
        
        # Overall title
        fig.suptitle(f"Ternary Diagrams Comparison: R={R}, w_SS={w_SS*100:.1f}%, w/b={w_b}",
                    fontsize=16, y=0.98)
        
        plt.tight_layout(rect=[0, 0, 1, 0.97])
        
        # Save figure
        output_dir = OUTPUTS_FIGURES_DIR / "ternary_diagrams"
        output_dir.mkdir(parents=True, exist_ok=True)
        filename = f"ternary_comparison_R{R}_{classification_type}.png"
        filepath = output_dir / filename
        fig.savefig(filepath, dpi=300, bbox_inches='tight')
        plt.close(fig)
        
        print(f"Saved comparison figure to: {filepath}")
        
        return fig


def main():
    """
    Main execution function for Phase 8: Ternary Diagram Generation.
    """
    print()
    print("="*70)
    print("PHASE 8: TERNARY DIAGRAM GENERATION (TYPE B)")
    print("="*70)
    print()
    
    # Paths to datasets
    classified_dataset_path = OUTPUTS_TABLES_DIR / "master_dataset_classified.csv"
    composition_dataset_path = OUTPUTS_TABLES_DIR / "mix_designs_with_compositions.csv"
    
    # Initialize plotter
    plotter = TernaryDiagramPlotter(classified_dataset_path, composition_dataset_path)
    
    # 1. Generate ternary diagrams for R=0.6 with different yCO2 values
    print("1. Generating ternary diagrams for R=0.6 with different yCO2 values...")
    print()
    
    R_values = [0.6]
    yCO2_values = [0.0, 0.20, 0.40]  # 0%, 20%, 40%
    
    plotter.create_multiple_ternary_diagrams(
        R_values=R_values,
        yCO2_values=yCO2_values,
        w_SS=0.03,
        w_b=1.4,
        classification_type='phase_diagram_class'
    )
    
    # 2. Generate ternary diagrams with carbonation state classification
    print("2. Generating ternary diagrams with carbonation state classification...")
    print()
    
    plotter.create_multiple_ternary_diagrams(
        R_values=[0.6],
        yCO2_values=[0.0, 0.20, 0.40],
        w_SS=0.03,
        w_b=1.4,
        classification_type='carbonation_state'
    )
    
    # 3. Generate ternary diagrams for different R values at yCO2=20%
    print("3. Generating ternary diagrams for different R values at yCO2=20%...")
    print()
    
    plotter.create_multiple_ternary_diagrams(
        R_values=[0.3, 0.6, 0.9, 1.2],
        yCO2_values=[0.20],
        w_SS=0.03,
        w_b=1.4,
        classification_type='phase_diagram_class'
    )
    
    # 4. Create comparison figure
    print("4. Creating comparison figure for R=0.6 with multiple yCO2 values...")
    print()
    
    plotter.create_comparison_ternary_figure(
        R=0.6,
        yCO2_values=[0.0, 0.20, 0.40],
        w_SS=0.03,
        w_b=1.4,
        classification_type='phase_diagram_class'
    )
    
    print()
    print("="*70)
    print("PHASE 8 - TERNARY DIAGRAM GENERATION COMPLETE")
    print("="*70)
    print()
    print("Generated ternary diagrams:")
    print("  - CaO-SiO₂-Al₂O₃ ternary plots")
    print("  - Multiple R values: 0.3, 0.6, 0.9, 1.2")
    print("  - Multiple yCO2 values: 0%, 20%, 40%")
    print("  - Classification schemes: phase_diagram_class, carbonation_state")
    print("  - Comparison figures included")
    print()
    print("All figures saved to: outputs/figures/ternary_diagrams/")
    print()


if __name__ == "__main__":
    main()
