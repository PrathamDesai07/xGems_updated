#!/usr/bin/env python3
"""
Data Aggregator - Phase 5
Builds master dataset by combining mix design parameters with equilibrium results
Creates comprehensive dataset with all independent variables and phase amounts
NO mock functions - all real data processing from actual calculations
"""

import json
import re
from pathlib import Path
from typing import Dict, List, Tuple
import pandas as pd
import numpy as np
from xgems_output_parser import XGEMSOutputParser


class DataAggregator:
    """Aggregates mix design parameters with equilibrium calculation results"""
    
    def __init__(self, 
                 input_directory: str = "inputs/generated",
                 output_directory: str = "runs/equilibrium"):
        """
        Initialize data aggregator
        
        Args:
            input_directory: Directory containing input files with mix design parameters
            output_directory: Directory containing JSON equilibrium output files
        """
        self.input_dir = Path(input_directory)
        self.output_dir = Path(output_directory)
        
        if not self.input_dir.exists():
            raise FileNotFoundError(f"Input directory not found: {input_directory}")
        if not self.output_dir.exists():
            raise FileNotFoundError(f"Output directory not found: {output_directory}")
        
        # Initialize output parser
        self.parser = XGEMSOutputParser(output_directory=str(self.output_dir))
        
        print(f"Initialized DataAggregator")
        print(f"  Input directory: {self.input_dir}")
        print(f"  Output directory: {self.output_dir}")
    
    def extract_mix_parameters(self, input_filepath: Path) -> Dict:
        """
        Extract mix design parameters from input file
        
        Args:
            input_filepath: Path to input file
            
        Returns:
            Dictionary with R, f_FA, yCO2, w_SS, w_b
        """
        try:
            with open(input_filepath, 'r') as f:
                content = f.read()
            
            # Extract mix ID from filename
            mix_id = input_filepath.stem  # e.g., "MIX_0000"
            
            # Find description line: # Description: R=0.30, f_FA=0.00, yCO2=0.00, w_SS=0.02, w_b=1.10
            pattern = r'# Description: R=([\d.]+), f_FA=([\d.]+), yCO2=([\d.]+), w_SS=([\d.]+), w_b=([\d.]+)'
            match = re.search(pattern, content)
            
            if match:
                return {
                    'mix_id': mix_id,
                    'R': float(match.group(1)),
                    'f_FA': float(match.group(2)),
                    'yCO2': float(match.group(3)),
                    'w_SS': float(match.group(4)),
                    'w_b': float(match.group(5))
                }
            else:
                print(f"Warning: Could not extract parameters from {input_filepath}")
                return {
                    'mix_id': mix_id,
                    'R': np.nan,
                    'f_FA': np.nan,
                    'yCO2': np.nan,
                    'w_SS': np.nan,
                    'w_b': np.nan
                }
                
        except Exception as e:
            print(f"Error reading {input_filepath}: {e}")
            return None
    
    def build_master_dataset(self) -> pd.DataFrame:
        """
        Build master dataset combining mix parameters and equilibrium results
        
        Returns:
            DataFrame with one row per mix design containing:
            - Independent variables: R, f_FA, yCO2, w_SS, w_b
            - Equilibrium results: pH, phases, convergence, etc.
        """
        print("\n" + "="*60)
        print("BUILDING MASTER DATASET")
        print("="*60)
        
        # Step 1: Parse all equilibrium outputs
        print("\nStep 1: Parsing equilibrium output files...")
        equilibrium_df = self.parser.parse_all_outputs()
        
        # Step 2: Extract mix parameters from input files
        print("\nStep 2: Extracting mix design parameters from input files...")
        input_files = sorted(self.input_dir.glob("MIX_*.inp"))
        
        mix_params = []
        for i, filepath in enumerate(input_files):
            if (i + 1) % 500 == 0:
                print(f"  Processed {i + 1}/{len(input_files)} input files...")
            
            params = self.extract_mix_parameters(filepath)
            if params is not None:
                mix_params.append(params)
        
        mix_params_df = pd.DataFrame(mix_params)
        print(f"Extracted parameters for {len(mix_params_df)} mixes")
        
        # Step 3: Merge mix parameters with equilibrium results
        print("\nStep 3: Merging mix parameters with equilibrium results...")
        master_df = pd.merge(
            mix_params_df,
            equilibrium_df,
            on='mix_id',
            how='inner'
        )
        
        print(f"Master dataset created: {len(master_df)} rows, {len(master_df.columns)} columns")
        
        # Reorder columns for better readability
        # Put independent variables first
        priority_cols = ['mix_id', 'R', 'f_FA', 'yCO2', 'w_SS', 'w_b', 
                        'converged', 'pH', 'pCO2_bar', 'num_phases']
        
        other_cols = [col for col in master_df.columns if col not in priority_cols]
        master_df = master_df[priority_cols + other_cols]
        
        return master_df
    
    def create_phase_summary_table(self, master_df: pd.DataFrame) -> pd.DataFrame:
        """
        Create a compact summary table with phase amounts as separate columns
        
        Args:
            master_df: Master dataset from build_master_dataset()
            
        Returns:
            DataFrame with independent variables + main phase amounts
        """
        # Get all unique phases
        all_phases = self.parser.get_all_phase_names(master_df)
        
        # Start with independent variables and key properties
        summary_cols = ['mix_id', 'R', 'f_FA', 'yCO2', 'w_SS', 'w_b', 
                       'converged', 'pH', 'pCO2_bar', 'temperature_K', 'pressure_bar']
        
        summary_df = master_df[summary_cols].copy()
        
        # Add phase amounts (moles) as columns
        for phase in all_phases:
            col_name = f'phase_{phase}_mol'
            if col_name in master_df.columns:
                summary_df[f'{phase}_mol'] = master_df[col_name]
            else:
                summary_df[f'{phase}_mol'] = 0.0
        
        # Add phase amounts (mass in kg) as columns
        for phase in all_phases:
            col_name = f'phase_{phase}_kg'
            if col_name in master_df.columns:
                summary_df[f'{phase}_kg'] = master_df[col_name]
            else:
                summary_df[f'{phase}_kg'] = 0.0
        
        # Fill NaN with 0.0 for phases not present
        phase_cols = [col for col in summary_df.columns if '_mol' in col or '_kg' in col]
        summary_df[phase_cols] = summary_df[phase_cols].fillna(0.0)
        
        return summary_df
    
    def calculate_derived_properties(self, master_df: pd.DataFrame) -> pd.DataFrame:
        """
        Calculate derived properties and ratios
        
        Args:
            master_df: Master dataset
            
        Returns:
            DataFrame with additional calculated columns
        """
        df = master_df.copy()
        
        # Calculate Ca/Si ratio from input composition
        df['Ca_Si_ratio'] = df['input_Ca_mol'] / (df['input_Si_mol'] + 1e-10)
        
        # Calculate total solid mass (sum of all phase masses)
        phase_mass_cols = [col for col in df.columns if col.startswith('phase_') and col.endswith('_kg')]
        df['total_solid_mass_kg'] = df[phase_mass_cols].sum(axis=1)
        
        # Calculate mass fractions for major phases
        major_phases = ['Calcite', 'CSH_1.00', 'Portlandite', 'Ettringite', 
                       'Silica_gel', 'Hydrotalcite', 'C-S-H_1.0']
        
        for phase in major_phases:
            mass_col = f'phase_{phase}_kg'
            if mass_col in df.columns:
                df[f'{phase}_mass_fraction'] = df[mass_col] / (df['total_solid_mass_kg'] + 1e-10)
        
        # Calculate carbonation degree (if calcite present)
        if 'phase_Calcite_mol' in df.columns:
            df['carbonation_degree'] = df['phase_Calcite_mol'] / (df['input_Ca_mol'] + 1e-10)
        
        return df
    
    def export_datasets(self, master_df: pd.DataFrame, output_dir: str = "outputs/tables"):
        """
        Export all datasets to CSV files
        
        Args:
            master_df: Master dataset
            output_dir: Output directory for CSV files
        """
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)
        
        print("\n" + "="*60)
        print("EXPORTING DATASETS")
        print("="*60)
        
        # Export full master dataset
        full_path = output_path / "master_dataset_full.csv"
        master_df.to_csv(full_path, index=False)
        print(f"\n1. Full master dataset:")
        print(f"   Path: {full_path}")
        print(f"   Rows: {len(master_df)}, Columns: {len(master_df.columns)}")
        
        # Create and export phase summary table
        summary_df = self.create_phase_summary_table(master_df)
        summary_path = output_path / "master_dataset.csv"
        summary_df.to_csv(summary_path, index=False)
        print(f"\n2. Phase summary dataset:")
        print(f"   Path: {summary_path}")
        print(f"   Rows: {len(summary_df)}, Columns: {len(summary_df.columns)}")
        
        # Calculate and export derived properties
        derived_df = self.calculate_derived_properties(master_df)
        derived_path = output_path / "master_dataset_with_derived.csv"
        derived_df.to_csv(derived_path, index=False)
        print(f"\n3. Dataset with derived properties:")
        print(f"   Path: {derived_path}")
        print(f"   Rows: {len(derived_df)}, Columns: {len(derived_df.columns)}")
        
        # Export convergence summary
        convergence_summary = master_df.groupby(['R', 'f_FA', 'yCO2', 'w_SS', 'w_b']).agg({
            'converged': 'sum',
            'mix_id': 'count'
        }).rename(columns={'converged': 'converged_count', 'mix_id': 'total_count'})
        convergence_summary['convergence_rate'] = (
            convergence_summary['converged_count'] / convergence_summary['total_count'] * 100
        )
        
        conv_path = output_path / "convergence_summary.csv"
        convergence_summary.to_csv(conv_path)
        print(f"\n4. Convergence summary:")
        print(f"   Path: {conv_path}")
        print(f"   Rows: {len(convergence_summary)}")
        
        print("\n" + "="*60)
        print("EXPORT COMPLETE")
        print("="*60)
    
    def print_dataset_statistics(self, master_df: pd.DataFrame):
        """
        Print comprehensive statistics for the master dataset
        
        Args:
            master_df: Master dataset
        """
        print("\n" + "="*60)
        print("MASTER DATASET STATISTICS")
        print("="*60)
        
        # Overall statistics
        print(f"\nTotal cases: {len(master_df)}")
        print(f"Converged cases: {master_df['converged'].sum()}")
        print(f"Convergence rate: {master_df['converged'].sum()/len(master_df)*100:.2f}%")
        
        # Independent variable ranges
        print("\nIndependent Variable Ranges:")
        for var in ['R', 'f_FA', 'yCO2', 'w_SS', 'w_b']:
            unique_vals = sorted(master_df[var].unique())
            print(f"  {var:.<15} {len(unique_vals)} levels: {unique_vals}")
        
        # pH statistics
        print(f"\npH Statistics:")
        print(f"  Mean: {master_df['pH'].mean():.3f}")
        print(f"  Std:  {master_df['pH'].std():.3f}")
        print(f"  Min:  {master_df['pH'].min():.3f}")
        print(f"  Max:  {master_df['pH'].max():.3f}")
        
        # pCO2 statistics
        print(f"\npCO2 Statistics (bar):")
        print(f"  Mean: {master_df['pCO2_bar'].mean():.4f}")
        print(f"  Std:  {master_df['pCO2_bar'].std():.4f}")
        print(f"  Min:  {master_df['pCO2_bar'].min():.4f}")
        print(f"  Max:  {master_df['pCO2_bar'].max():.4f}")
        
        # Phase statistics
        all_phases = self.parser.get_all_phase_names(master_df)
        print(f"\nPhase Statistics:")
        print(f"  Total unique phases: {len(all_phases)}")
        print(f"  Phases: {', '.join(all_phases)}")
        
        # Count how many cases have each phase
        print(f"\nPhase Occurrence:")
        for phase in all_phases:
            col_name = f'phase_{phase}_mol'
            if col_name in master_df.columns:
                count = (master_df[col_name] > 0).sum()
                percentage = count / len(master_df) * 100
                print(f"  {phase:.<30} {count:>5} cases ({percentage:>5.1f}%)")


def main():
    """Main execution for building master dataset"""
    
    # Initialize aggregator
    aggregator = DataAggregator(
        input_directory="inputs/generated",
        output_directory="runs/equilibrium"
    )
    
    # Build master dataset
    master_df = aggregator.build_master_dataset()
    
    # Print statistics
    aggregator.print_dataset_statistics(master_df)
    
    # Export all datasets
    aggregator.export_datasets(master_df, output_dir="outputs/tables")
    
    print("\n" + "="*60)
    print("PHASE 5 DATA AGGREGATION - COMPLETE")
    print("="*60)
    print("\nGenerated files:")
    print("  - outputs/tables/master_dataset_full.csv")
    print("  - outputs/tables/master_dataset.csv")
    print("  - outputs/tables/master_dataset_with_derived.csv")
    print("  - outputs/tables/convergence_summary.csv")
    print("  - outputs/raw/parsed_outputs_full.csv")
    print("  - outputs/raw/phase_amounts_mol.csv")
    print("  - outputs/raw/phase_amounts_kg.csv")


if __name__ == "__main__":
    main()
