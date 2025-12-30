"""
Mix Design Generator
====================
Generates all 4,928 mix design combinations for the full factorial design.

For each combination of (R, f_FA, yCO2, w_SS, w/b):
- Calculates raw material masses
- Outputs structured data

Author: Thermodynamic Modeling Project
Date: December 27, 2025
"""

import sys
from pathlib import Path
from itertools import product

# Add scripts directory to path
SCRIPTS_DIR = Path(__file__).parent
if str(SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_DIR))

import numpy as np
import pandas as pd
import config


class MixDesignGenerator:
    """Generate mix designs from independent variables."""
    
    def __init__(self, reference_gangue_mass=None):
        """
        Initialize the mix design generator.
        
        Parameters:
        -----------
        reference_gangue_mass : float, optional
            Reference mass of coal gangue (g). Default from config.
        """
        self.reference_gangue_mass = reference_gangue_mass or config.REFERENCE_GANGUE_MASS
        
    def calculate_raw_material_masses(self, R, f_FA, w_SS, w_b):
        """
        Calculate raw material masses for given mix parameters.
        
        Parameters:
        -----------
        R : float
            Binder-to-aggregate ratio: (Cement + Fly ash) / Coal gangue
        f_FA : float
            Fly ash replacement ratio: Fly ash / (Cement + Fly ash)
        w_SS : float
            Sodium silicate dosage: sodium silicate / total slurry mass
        w_b : float
            Water-to-binder ratio: Water / (Cement + Fly ash)
            
        Returns:
        --------
        dict : Dictionary with masses of all raw materials
        """
        # Reference coal gangue mass
        m_gangue = self.reference_gangue_mass
        
        # Calculate total binder mass from R
        m_binder_total = R * m_gangue  # (Cement + Fly ash)
        
        # Calculate individual binder masses from f_FA
        m_flyash = f_FA * m_binder_total
        m_cement = (1 - f_FA) * m_binder_total
        
        # Calculate water mass from w/b (before accounting for water in sodium silicate)
        m_water_from_wb = w_b * m_binder_total
        
        # Sodium silicate calculation is iterative because w_SS = m_SS / m_total
        # and m_total includes m_SS, water, and other materials
        # We need to solve: w_SS = m_SS / (m_cement + m_flyash + m_gangue + m_water + m_SS)
        
        # Let m_dry = m_cement + m_flyash + m_gangue
        m_dry = m_cement + m_flyash + m_gangue
        
        # From w_SS definition: m_SS = w_SS * m_total
        # m_total = m_dry + m_water + m_SS
        # m_SS = w_SS * (m_dry + m_water + m_SS)
        # m_SS = w_SS * m_dry + w_SS * m_water + w_SS * m_SS
        # m_SS * (1 - w_SS) = w_SS * (m_dry + m_water)
        # m_SS = w_SS * (m_dry + m_water) / (1 - w_SS)
        
        m_sodium_silicate = w_SS * (m_dry + m_water_from_wb) / (1 - w_SS)
        
        # Water from sodium silicate
        water_fraction_in_SS = config.SODIUM_SILICATE_COMPOSITION['H2O'] / 100.0
        m_water_from_SS = m_sodium_silicate * water_fraction_in_SS
        
        # Total water (adjust for water in sodium silicate)
        m_water_total = m_water_from_wb - m_water_from_SS
        
        # If calculated water becomes negative, set to zero and adjust
        if m_water_total < 0:
            m_water_total = 0.0
        
        # Calculate total mass
        m_total = m_cement + m_flyash + m_gangue + m_water_total + m_sodium_silicate
        
        # Verify w_SS
        w_SS_check = m_sodium_silicate / m_total
        
        return {
            'cement_mass_g': m_cement,
            'flyash_mass_g': m_flyash,
            'gangue_mass_g': m_gangue,
            'water_mass_g': m_water_total,
            'sodium_silicate_mass_g': m_sodium_silicate,
            'total_mass_g': m_total,
            'w_SS_check': w_SS_check,
        }
    
    def generate_all_combinations(self):
        """
        Generate all 4,928 mix design combinations.
        
        Returns:
        --------
        pandas.DataFrame : DataFrame with all mix designs
        """
        # Get all variable arrays from config
        R_values = config.BINDER_AGGREGATE_RATIOS
        f_FA_values = config.FLY_ASH_REPLACEMENT_RATIOS
        yCO2_values = config.CO2_CONCENTRATIONS
        w_SS_values = config.SODIUM_SILICATE_DOSAGES
        w_b_values = config.WATER_BINDER_RATIOS
        
        # Generate all combinations
        combinations = list(product(
            R_values,
            f_FA_values,
            yCO2_values,
            w_SS_values,
            w_b_values
        ))
        
        print(f"Generating {len(combinations)} mix designs...")
        
        # Create list to store results
        mix_designs = []
        
        for idx, (R, f_FA, yCO2, w_SS, w_b) in enumerate(combinations):
            # Calculate raw material masses
            masses = self.calculate_raw_material_masses(R, f_FA, w_SS, w_b)
            
            # Create mix design record
            mix_design = {
                'mix_id': f'MIX_{idx:04d}',
                'R': R,
                'f_FA': f_FA,
                'yCO2': yCO2,
                'w_SS': w_SS,
                'w_b': w_b,
                'cement_mass_g': masses['cement_mass_g'],
                'flyash_mass_g': masses['flyash_mass_g'],
                'gangue_mass_g': masses['gangue_mass_g'],
                'water_mass_g': masses['water_mass_g'],
                'sodium_silicate_mass_g': masses['sodium_silicate_mass_g'],
                'total_mass_g': masses['total_mass_g'],
            }
            
            mix_designs.append(mix_design)
        
        # Create DataFrame
        df = pd.DataFrame(mix_designs)
        
        print(f"✓ Generated {len(df)} mix designs")
        
        return df
    
    def save_to_csv(self, df, filename='mix_designs.csv'):
        """
        Save mix designs to CSV file.
        
        Parameters:
        -----------
        df : pandas.DataFrame
            DataFrame with mix designs
        filename : str
            Output filename
        """
        output_path = config.OUTPUTS_TABLES_DIR / filename
        df.to_csv(output_path, index=False, float_format='%.6f')
        print(f"✓ Saved to: {output_path}")
        
    def print_summary(self, df):
        """
        Print summary statistics of generated mix designs.
        
        Parameters:
        -----------
        df : pandas.DataFrame
            DataFrame with mix designs
        """
        print("\n" + "=" * 80)
        print("Mix Design Generation Summary")
        print("=" * 80)
        
        print(f"\nTotal mix designs: {len(df)}")
        
        print("\nVariable ranges:")
        for var in ['R', 'f_FA', 'yCO2', 'w_SS', 'w_b']:
            print(f"  {var:8s}: {df[var].min():.3f} to {df[var].max():.3f} ({df[var].nunique()} levels)")
        
        print("\nMass ranges (g):")
        mass_cols = ['cement_mass_g', 'flyash_mass_g', 'gangue_mass_g', 
                     'water_mass_g', 'sodium_silicate_mass_g', 'total_mass_g']
        for col in mass_cols:
            print(f"  {col:30s}: {df[col].min():8.2f} to {df[col].max():8.2f}")
        
        print("\nSample mix designs:")
        print(df.head(10).to_string(index=False))
        
        print("\n" + "=" * 80)


def main():
    """Main function to generate all mix designs."""
    
    print("\n" + "=" * 80)
    print("Phase 2.1: Mix Design Generator")
    print("=" * 80 + "\n")
    
    # Create generator
    generator = MixDesignGenerator()
    
    # Generate all combinations
    df_mix_designs = generator.generate_all_combinations()
    
    # Print summary
    generator.print_summary(df_mix_designs)
    
    # Save to CSV
    generator.save_to_csv(df_mix_designs)
    
    print("\n" + "=" * 80)
    print("Mix Design Generation: COMPLETE ✓")
    print("=" * 80 + "\n")
    
    return df_mix_designs


if __name__ == '__main__':
    df = main()
