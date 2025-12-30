#!/usr/bin/env python3
"""
Phase Map Plotter - Phase 7
Creates 2D phase stability maps (Type A diagrams)
Plots f_FA (X-axis) vs yCO2 (Y-axis) colored by phase classification
NO mock functions - all real data visualization from actual equilibrium calculations
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from pathlib import Path
from typing import Dict, List, Tuple, Optional


class PhaseMapPlotter:
    """
    Creates 2D phase stability maps showing phase regions
    X-axis: Fly ash replacement ratio (f_FA)
    Y-axis: CO2 concentration (yCO2)
    """
    
    def __init__(self, classified_dataset_path: str = "outputs/tables/master_dataset_classified.csv"):
        """
        Initialize phase map plotter
        
        Args:
            classified_dataset_path: Path to classified dataset CSV
        """
        self.dataset_path = Path(classified_dataset_path)
        if not self.dataset_path.exists():
            raise FileNotFoundError(f"Classified dataset not found: {classified_dataset_path}")
        
        # Load classified dataset
        print(f"Loading classified dataset from {self.dataset_path}...")
        self.df = pd.read_csv(self.dataset_path)
        print(f"Loaded {len(self.df)} equilibrium cases")
        
        # Define color schemes for different classification types
        self.color_schemes = {
            'phase_diagram_class': {
                'Silica-rich': '#1f77b4',        # Blue
                'Calcite + C-S-H': '#ff7f0e',    # Orange
                'Calcite-rich': '#2ca02c',       # Green
                'C-S-H dominant': '#d62728',     # Red
                'C-S-H + AFt': '#9467bd'         # Purple
            },
            'carbonation_state': {
                'Uncarbonated': '#e5e5e5',               # Light gray
                'Low carbonation': '#ffffb2',            # Light yellow
                'Medium carbonation': '#fecc5c',         # Yellow-orange
                'High carbonation': '#fd8d3c',           # Orange
                'Very high carbonation': '#e31a1c'       # Red
            },
            'dominant_phase_by_mass': {
                'Silica_gel': '#1f77b4',         # Blue
                'C-S-H_1.0': '#ff7f0e',          # Orange
                'Calcite': '#2ca02c',            # Green
                'Ettringite': '#d62728',         # Red
                'Hydrotalcite': '#9467bd'        # Purple
            },
            'pH_regime': {
                'Neutral (pH<8.5)': '#d62728',                    # Red
                'Slightly alkaline (8.5-9.0)': '#ff7f0e',        # Orange
                'Moderately alkaline (9.0-9.5)': '#ffdd55',      # Yellow
                'Alkaline (9.5-10.0)': '#2ca02c',                # Green
                'Highly alkaline (pH>10.0)': '#1f77b4'           # Blue
            }
        }
    
    def create_phase_map(self, 
                        R: float,
                        w_SS: float = 0.03,
                        w_b: float = 1.4,
                        classification_type: str = 'phase_diagram_class',
                        save_path: Optional[str] = None,
                        show_grid: bool = True,
                        marker_size: int = 200) -> plt.Figure:
        """
        Create a 2D phase map for fixed R, w_SS, and w_b
        
        Args:
            R: Binder-to-aggregate ratio
            w_SS: Sodium silicate dosage
            w_b: Water-to-binder ratio
            classification_type: Column name for phase classification
            save_path: Path to save figure (optional)
            show_grid: Whether to show grid lines
            marker_size: Size of scatter plot markers
            
        Returns:
            matplotlib Figure object
        """
        # Filter data for fixed parameters
        mask = (self.df['R'] == R) & (self.df['w_SS'] == w_SS) & (self.df['w_b'] == w_b)
        data_subset = self.df[mask].copy()
        
        if len(data_subset) == 0:
            raise ValueError(f"No data found for R={R}, w_SS={w_SS}, w_b={w_b}")
        
        print(f"\nCreating phase map for:")
        print(f"  R = {R}")
        print(f"  w_SS = {w_SS * 100}%")
        print(f"  w_b = {w_b}")
        print(f"  Classification: {classification_type}")
        print(f"  Data points: {len(data_subset)}")
        
        # Get unique phases and colors
        phases = data_subset[classification_type].unique()
        color_map = self.color_schemes.get(classification_type, {})
        
        # Assign colors (use defaults if not in color scheme)
        if not color_map:
            # Generate default colors if scheme not defined
            cmap = plt.cm.get_cmap('tab10')
            color_map = {phase: cmap(i % 10) for i, phase in enumerate(phases)}
        
        # Create figure
        fig, ax = plt.subplots(figsize=(10, 8))
        
        # Plot each phase type
        for phase in sorted(phases):
            phase_data = data_subset[data_subset[classification_type] == phase]
            color = color_map.get(phase, '#808080')  # Default to gray if not found
            
            ax.scatter(
                phase_data['f_FA'],
                phase_data['yCO2'],
                c=color,
                s=marker_size,
                marker='s',  # Square markers
                edgecolors='black',
                linewidths=0.5,
                alpha=0.8,
                label=phase
            )
        
        # Set labels and title
        ax.set_xlabel('Fly Ash Replacement Ratio (f_FA)', fontsize=12, fontweight='bold')
        ax.set_ylabel('CO₂ Concentration (yCO2)', fontsize=12, fontweight='bold')
        
        title = f'Phase Stability Map\nR={R}, w_SS={w_SS*100:.0f}%, w/b={w_b}'
        ax.set_title(title, fontsize=14, fontweight='bold', pad=20)
        
        # Set axis limits and ticks
        ax.set_xlim(-0.05, 1.05)
        ax.set_ylim(-0.02, 0.42)
        
        # Set tick labels
        f_FA_ticks = np.arange(0, 1.1, 0.1)
        yCO2_ticks = np.array([0, 0.15, 0.20, 0.25, 0.30, 0.35, 0.40])
        
        ax.set_xticks(f_FA_ticks)
        ax.set_yticks(yCO2_ticks)
        ax.set_xticklabels([f'{x:.1f}' for x in f_FA_ticks])
        ax.set_yticklabels([f'{y:.0%}' if y > 0 else '0%' for y in yCO2_ticks])
        
        # Grid
        if show_grid:
            ax.grid(True, linestyle='--', alpha=0.3, linewidth=0.5)
        
        # Legend
        ax.legend(
            loc='upper left',
            bbox_to_anchor=(1.02, 1),
            frameon=True,
            fancybox=True,
            shadow=True,
            fontsize=9
        )
        
        # Tight layout
        plt.tight_layout()
        
        # Save if path provided
        if save_path:
            save_path = Path(save_path)
            save_path.parent.mkdir(parents=True, exist_ok=True)
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
            print(f"Saved phase map to: {save_path}")
        
        return fig
    
    def create_multiple_phase_maps(self,
                                   R_values: List[float] = None,
                                   w_SS: float = 0.03,
                                   w_b: float = 1.4,
                                   classification_type: str = 'phase_diagram_class',
                                   output_dir: str = "outputs/figures/phase_maps"):
        """
        Create phase maps for multiple R values
        
        Args:
            R_values: List of R values to plot (default: all available)
            w_SS: Sodium silicate dosage
            w_b: Water-to-binder ratio
            classification_type: Column name for phase classification
            output_dir: Directory to save figures
        """
        if R_values is None:
            R_values = sorted(self.df['R'].unique())
        
        print("\n" + "="*70)
        print("GENERATING MULTIPLE PHASE MAPS")
        print("="*70)
        
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)
        
        figures = []
        
        for R in R_values:
            print(f"\n{'='*70}")
            
            # Create filename
            filename = f"phase_map_R{R:.1f}_wSS{w_SS*100:.0f}pct_wb{w_b:.1f}_{classification_type}.png"
            save_path = output_path / filename
            
            try:
                fig = self.create_phase_map(
                    R=R,
                    w_SS=w_SS,
                    w_b=w_b,
                    classification_type=classification_type,
                    save_path=str(save_path)
                )
                figures.append(fig)
                plt.close(fig)
            except Exception as e:
                print(f"Error creating phase map for R={R}: {e}")
        
        print("\n" + "="*70)
        print(f"PHASE MAP GENERATION COMPLETE")
        print("="*70)
        print(f"Generated {len(figures)} phase maps")
        print(f"Saved to: {output_dir}")
        
        return figures
    
    def create_comparison_figure(self,
                                 R_values: List[float],
                                 w_SS: float = 0.03,
                                 w_b: float = 1.4,
                                 classification_type: str = 'phase_diagram_class',
                                 save_path: Optional[str] = None) -> plt.Figure:
        """
        Create a multi-panel figure comparing phase maps for different R values
        
        Args:
            R_values: List of R values to compare
            w_SS: Sodium silicate dosage
            w_b: Water-to-binder ratio
            classification_type: Column name for phase classification
            save_path: Path to save figure (optional)
            
        Returns:
            matplotlib Figure object
        """
        n_maps = len(R_values)
        n_cols = 2
        n_rows = (n_maps + n_cols - 1) // n_cols
        
        fig, axes = plt.subplots(n_rows, n_cols, figsize=(16, 6*n_rows))
        if n_rows == 1 and n_cols == 1:
            axes = np.array([[axes]])
        elif n_rows == 1 or n_cols == 1:
            axes = axes.reshape(n_rows, n_cols)
        
        color_map = self.color_schemes.get(classification_type, {})
        
        for idx, R in enumerate(R_values):
            row = idx // n_cols
            col = idx % n_cols
            ax = axes[row, col]
            
            # Filter data
            mask = (self.df['R'] == R) & (self.df['w_SS'] == w_SS) & (self.df['w_b'] == w_b)
            data_subset = self.df[mask].copy()
            
            if len(data_subset) == 0:
                ax.text(0.5, 0.5, f'No data for R={R}', 
                       ha='center', va='center', transform=ax.transAxes)
                continue
            
            # Get unique phases
            phases = data_subset[classification_type].unique()
            
            # Plot each phase
            for phase in sorted(phases):
                phase_data = data_subset[data_subset[classification_type] == phase]
                color = color_map.get(phase, '#808080')
                
                ax.scatter(
                    phase_data['f_FA'],
                    phase_data['yCO2'],
                    c=color,
                    s=100,
                    marker='s',
                    edgecolors='black',
                    linewidths=0.5,
                    alpha=0.8,
                    label=phase
                )
            
            # Format subplot
            ax.set_xlabel('f_FA', fontsize=10, fontweight='bold')
            ax.set_ylabel('yCO2', fontsize=10, fontweight='bold')
            ax.set_title(f'R = {R}', fontsize=11, fontweight='bold')
            ax.set_xlim(-0.05, 1.05)
            ax.set_ylim(-0.02, 0.42)
            ax.grid(True, linestyle='--', alpha=0.3, linewidth=0.5)
            
            # Set ticks
            ax.set_xticks(np.arange(0, 1.1, 0.2))
            ax.set_yticks(np.array([0, 0.15, 0.25, 0.35]))
            ax.set_yticklabels(['0%', '15%', '25%', '35%'])
        
        # Remove empty subplots
        for idx in range(n_maps, n_rows * n_cols):
            row = idx // n_cols
            col = idx % n_cols
            fig.delaxes(axes[row, col])
        
        # Create legend for the entire figure
        if color_map:
            legend_elements = [
                mpatches.Patch(facecolor=color, edgecolor='black', label=phase)
                for phase, color in sorted(color_map.items())
                if phase in self.df[classification_type].unique()
            ]
            fig.legend(
                handles=legend_elements,
                loc='center right',
                bbox_to_anchor=(0.98, 0.5),
                frameon=True,
                fancybox=True,
                shadow=True,
                fontsize=10
            )
        
        # Super title
        fig.suptitle(
            f'Phase Stability Maps - {classification_type}\nw_SS={w_SS*100:.0f}%, w/b={w_b}',
            fontsize=14,
            fontweight='bold',
            y=0.995
        )
        
        plt.tight_layout(rect=[0, 0, 0.95, 0.99])
        
        # Save if path provided
        if save_path:
            save_path = Path(save_path)
            save_path.parent.mkdir(parents=True, exist_ok=True)
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
            print(f"Saved comparison figure to: {save_path}")
        
        return fig
    
    def create_all_classification_maps(self,
                                      R: float = 0.6,
                                      w_SS: float = 0.03,
                                      w_b: float = 1.4,
                                      output_dir: str = "outputs/figures/phase_maps"):
        """
        Create phase maps for all classification types
        
        Args:
            R: Binder-to-aggregate ratio
            w_SS: Sodium silicate dosage
            w_b: Water-to-binder ratio
            output_dir: Directory to save figures
        """
        classification_types = [
            'phase_diagram_class',
            'carbonation_state',
            'dominant_phase_by_mass',
            'pH_regime'
        ]
        
        print("\n" + "="*70)
        print("GENERATING MAPS FOR ALL CLASSIFICATION TYPES")
        print("="*70)
        
        for classification_type in classification_types:
            if classification_type not in self.df.columns:
                print(f"Warning: Classification '{classification_type}' not found in dataset")
                continue
            
            print(f"\nGenerating map for: {classification_type}")
            
            filename = f"phase_map_R{R:.1f}_{classification_type}.png"
            save_path = Path(output_dir) / filename
            
            try:
                fig = self.create_phase_map(
                    R=R,
                    w_SS=w_SS,
                    w_b=w_b,
                    classification_type=classification_type,
                    save_path=str(save_path)
                )
                plt.close(fig)
            except Exception as e:
                print(f"Error: {e}")


def main():
    """Main execution for phase map generation"""
    
    # Initialize plotter
    plotter = PhaseMapPlotter(
        classified_dataset_path="outputs/tables/master_dataset_classified.csv"
    )
    
    # Generate individual phase maps for all R values
    print("\n" + "="*70)
    print("PHASE 7: 2D PHASE MAP GENERATION")
    print("="*70)
    
    # Configuration
    R_values = [0.3, 0.6, 0.9, 1.2]
    w_SS = 0.03  # 3%
    w_b = 1.4
    
    # 1. Generate phase maps for all R values using phase_diagram_class
    print("\n1. Generating phase maps using 'phase_diagram_class'...")
    plotter.create_multiple_phase_maps(
        R_values=R_values,
        w_SS=w_SS,
        w_b=w_b,
        classification_type='phase_diagram_class',
        output_dir="outputs/figures/phase_maps"
    )
    
    # 2. Generate phase maps using carbonation_state
    print("\n2. Generating phase maps using 'carbonation_state'...")
    plotter.create_multiple_phase_maps(
        R_values=R_values,
        w_SS=w_SS,
        w_b=w_b,
        classification_type='carbonation_state',
        output_dir="outputs/figures/phase_maps"
    )
    
    # 3. Create comparison figure (all R values in one figure)
    print("\n3. Creating comparison figure...")
    comparison_path = "outputs/figures/phase_maps/phase_map_comparison_all_R.png"
    plotter.create_comparison_figure(
        R_values=R_values,
        w_SS=w_SS,
        w_b=w_b,
        classification_type='phase_diagram_class',
        save_path=comparison_path
    )
    
    # 4. Generate all classification types for R=0.6
    print("\n4. Generating all classification types for R=0.6...")
    plotter.create_all_classification_maps(
        R=0.6,
        w_SS=w_SS,
        w_b=w_b,
        output_dir="outputs/figures/phase_maps"
    )
    
    print("\n" + "="*70)
    print("PHASE 7 - 2D PHASE MAP GENERATION COMPLETE")
    print("="*70)
    print("\nGenerated figures:")
    print("  - Individual phase maps for R = 0.3, 0.6, 0.9, 1.2")
    print("  - Phase maps with phase_diagram_class classification")
    print("  - Phase maps with carbonation_state classification")
    print("  - Comparison figure with all R values")
    print("  - All classification types for R=0.6")
    print(f"\nAll figures saved to: outputs/figures/phase_maps/")


if __name__ == "__main__":
    main()
