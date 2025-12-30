#!/usr/bin/env python3
"""
xGEMS Output Parser - Phase 5
Parses JSON output files from xGEMS equilibrium calculations
Extracts phase assemblages, amounts, pH, and thermodynamic properties
NO mock functions - all real data parsing from actual equilibrium calculations
"""

import json
import os
from pathlib import Path
from typing import Dict, List, Optional, Tuple
import pandas as pd
import numpy as np


class XGEMSOutputParser:
    """Parser for xGEMS equilibrium calculation JSON output files"""
    
    def __init__(self, output_directory: str = "runs/equilibrium"):
        """
        Initialize parser
        
        Args:
            output_directory: Directory containing JSON output files
        """
        self.output_dir = Path(output_directory)
        if not self.output_dir.exists():
            raise FileNotFoundError(f"Output directory not found: {output_directory}")
        
        self.output_files = sorted(self.output_dir.glob("MIX_*.json"))
        print(f"Found {len(self.output_files)} output files to parse")
    
    def parse_single_output(self, filepath: Path) -> Optional[Dict]:
        """
        Parse a single JSON output file
        
        Args:
            filepath: Path to JSON output file
            
        Returns:
            Dictionary containing parsed data, or None if parsing fails
        """
        try:
            with open(filepath, 'r') as f:
                data = json.load(f)
            
            # Extract mix ID from filename
            mix_id = filepath.stem  # e.g., "MIX_0000"
            
            # Build parsed result
            result = {
                'mix_id': mix_id,
                'converged': data.get('converged', False),
                'method': data.get('method', 'unknown'),
                'temperature_K': data.get('temperature_K', np.nan),
                'pressure_bar': data.get('pressure_bar', np.nan),
                'CO2_fraction': data.get('CO2_fraction', np.nan),
                'pCO2_bar': data.get('pCO2_bar', np.nan),
                'pH': data.get('pH', np.nan),
                'pe': data.get('pe', np.nan),
                'Eh': data.get('Eh', np.nan),
                'system_mass_kg': data.get('system_mass_kg', np.nan),
                'execution_time': data.get('execution_time', np.nan),
                'input_file': data.get('input_file', '')
            }
            
            # Extract input composition
            input_comp = data.get('input_composition', {})
            for element in ['Ca', 'Si', 'Al', 'Fe', 'Mg', 'K', 'Na', 'S', 'O', 'H', 'C']:
                result[f'input_{element}_mol'] = input_comp.get(element, np.nan)
            
            # Extract phase information
            phases = data.get('phases', {})
            result['num_phases'] = len(phases)
            result['phase_list'] = list(phases.keys())
            
            # Store individual phase amounts (moles and mass)
            for phase_name, phase_data in phases.items():
                if isinstance(phase_data, dict):
                    result[f'phase_{phase_name}_mol'] = phase_data.get('moles', np.nan)
                    result[f'phase_{phase_name}_kg'] = phase_data.get('mass_kg', np.nan)
                else:
                    # Handle old format where phase_data might be just a number
                    result[f'phase_{phase_name}_mol'] = phase_data
                    result[f'phase_{phase_name}_kg'] = np.nan
            
            return result
            
        except Exception as e:
            print(f"Error parsing {filepath}: {e}")
            return None
    
    def parse_all_outputs(self) -> pd.DataFrame:
        """
        Parse all output files and return as DataFrame
        
        Returns:
            DataFrame with one row per equilibrium calculation
        """
        print(f"\nParsing all {len(self.output_files)} output files...")
        
        parsed_data = []
        failed_count = 0
        
        for i, filepath in enumerate(self.output_files):
            if (i + 1) % 500 == 0:
                print(f"  Parsed {i + 1}/{len(self.output_files)} files...")
            
            result = self.parse_single_output(filepath)
            if result is not None:
                parsed_data.append(result)
            else:
                failed_count += 1
        
        print(f"Parsing complete: {len(parsed_data)} successful, {failed_count} failed")
        
        # Convert to DataFrame
        df = pd.DataFrame(parsed_data)
        
        # Sort by mix_id
        df = df.sort_values('mix_id').reset_index(drop=True)
        
        return df
    
    def get_all_phase_names(self, df: pd.DataFrame) -> List[str]:
        """
        Extract all unique phase names from parsed data
        
        Args:
            df: DataFrame from parse_all_outputs()
            
        Returns:
            Sorted list of unique phase names
        """
        all_phases = set()
        for phase_list in df['phase_list']:
            if isinstance(phase_list, list):
                all_phases.update(phase_list)
        
        return sorted(list(all_phases))
    
    def create_phase_matrix(self, df: pd.DataFrame, unit: str = 'mol') -> pd.DataFrame:
        """
        Create a matrix of phase amounts (rows=mixes, columns=phases)
        
        Args:
            df: DataFrame from parse_all_outputs()
            unit: 'mol' for moles or 'kg' for mass
            
        Returns:
            DataFrame with mix_id as index and phases as columns
        """
        all_phases = self.get_all_phase_names(df)
        
        # Create empty matrix
        phase_matrix = pd.DataFrame(
            index=df['mix_id'],
            columns=all_phases,
            dtype=float
        )
        
        # Fill in phase amounts
        for idx, row in df.iterrows():
            mix_id = row['mix_id']
            for phase in all_phases:
                col_name = f'phase_{phase}_{unit}'
                if col_name in row:
                    phase_matrix.loc[mix_id, phase] = row[col_name]
                else:
                    phase_matrix.loc[mix_id, phase] = 0.0
        
        # Replace NaN with 0.0 (phase not present)
        phase_matrix = phase_matrix.fillna(0.0)
        
        return phase_matrix
    
    def get_summary_statistics(self, df: pd.DataFrame) -> Dict:
        """
        Calculate summary statistics for parsed data
        
        Args:
            df: DataFrame from parse_all_outputs()
            
        Returns:
            Dictionary of summary statistics
        """
        stats = {
            'total_cases': len(df),
            'converged_cases': df['converged'].sum(),
            'convergence_rate': df['converged'].sum() / len(df) * 100,
            'pH_mean': df['pH'].mean(),
            'pH_std': df['pH'].std(),
            'pH_min': df['pH'].min(),
            'pH_max': df['pH'].max(),
            'pCO2_mean': df['pCO2_bar'].mean(),
            'pCO2_std': df['pCO2_bar'].std(),
            'pCO2_min': df['pCO2_bar'].min(),
            'pCO2_max': df['pCO2_bar'].max(),
            'avg_num_phases': df['num_phases'].mean(),
            'min_num_phases': df['num_phases'].min(),
            'max_num_phases': df['num_phases'].max(),
            'total_execution_time': df['execution_time'].sum(),
            'avg_execution_time': df['execution_time'].mean()
        }
        
        return stats
    
    def export_to_csv(self, df: pd.DataFrame, output_path: str):
        """
        Export parsed data to CSV
        
        Args:
            df: DataFrame to export
            output_path: Path for output CSV file
        """
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        df.to_csv(output_path, index=False)
        print(f"\nExported data to: {output_path}")
        print(f"Rows: {len(df)}, Columns: {len(df.columns)}")


def main():
    """Main execution for testing the parser"""
    
    # Initialize parser
    parser = XGEMSOutputParser(output_directory="runs/equilibrium")
    
    # Parse all outputs
    df = parser.parse_all_outputs()
    
    # Get summary statistics
    stats = parser.get_summary_statistics(df)
    
    print("\n" + "="*60)
    print("PARSING SUMMARY STATISTICS")
    print("="*60)
    for key, value in stats.items():
        if isinstance(value, float):
            print(f"{key:.<40} {value:.4f}")
        else:
            print(f"{key:.<40} {value}")
    
    # Get all unique phases
    all_phases = parser.get_all_phase_names(df)
    print(f"\n{'Unique phases found':.<40} {len(all_phases)}")
    print(f"Phases: {', '.join(all_phases)}")
    
    # Create phase matrix (moles)
    print("\nCreating phase amount matrix (moles)...")
    phase_matrix_mol = parser.create_phase_matrix(df, unit='mol')
    
    # Create phase matrix (mass)
    print("Creating phase amount matrix (mass)...")
    phase_matrix_kg = parser.create_phase_matrix(df, unit='kg')
    
    # Export main dataframe
    parser.export_to_csv(df, "outputs/raw/parsed_outputs_full.csv")
    
    # Export phase matrices
    phase_matrix_mol.to_csv("outputs/raw/phase_amounts_mol.csv")
    print(f"Exported phase amounts (mol) to: outputs/raw/phase_amounts_mol.csv")
    
    phase_matrix_kg.to_csv("outputs/raw/phase_amounts_kg.csv")
    print(f"Exported phase amounts (kg) to: outputs/raw/phase_amounts_kg.csv")
    
    print("\n" + "="*60)
    print("PHASE 5 OUTPUT PARSER - COMPLETE")
    print("="*60)


if __name__ == "__main__":
    main()
