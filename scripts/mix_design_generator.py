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
    
    def calculate_clinker_phase_masses(self, cement_mass, clinker_phases=None):
        """
        Convert cement mass to individual clinker phase masses.
        
        This uses Rietveld XRD data (or Bogue calculation results) to 
        break down cement into its constituent phases (C3S, C2S, C3A, C4AF, etc.).
        
        Parameters:
        -----------
        cement_mass : float
            Total cement mass (g)
        clinker_phases : dict, optional
            Dict of phase: weight_fraction. If None, uses config.CEMENT_PHASES
            
        Returns:
        --------
        dict : Phase name → mass (g)
        """
        if clinker_phases is None:
            clinker_phases = config.CEMENT_PHASES
        
        phase_masses = {}
        for phase, fraction in clinker_phases.items():
            phase_masses[phase] = cement_mass * fraction
        
        return phase_masses
    
    def calculate_flyash_phase_masses(self, flyash_mass, flyash_phases=None):
        """
        Convert fly ash mass to phase masses (glass, quartz, mullite, etc.).
        
        This uses Rietveld XRD data (or mineralogical estimates) to 
        break down fly ash into its constituent phases.
        
        Parameters:
        -----------
        flyash_mass : float
            Total fly ash mass (g)
        flyash_phases : dict, optional
            Dict of phase: weight_fraction. If None, uses config.FLYASH_PHASES
            
        Returns:
        --------
        dict : Phase name → mass (g)
        """
        if flyash_phases is None:
            flyash_phases = config.FLYASH_PHASES
        
        phase_masses = {}
        for phase, fraction in flyash_phases.items():
            phase_masses[phase] = flyash_mass * fraction
        
        return phase_masses
    
    def calculate_gangue_phase_masses(self, gangue_mass, gangue_phases=None):
        """
        Convert coal gangue mass to phase masses.
        
        This uses Rietveld XRD data (or mineralogical estimates) to 
        break down coal gangue into its constituent phases (quartz, clays, etc.).
        
        Parameters:
        -----------
        gangue_mass : float
            Total coal gangue mass (g)
        gangue_phases : dict, optional
            Dict of phase: weight_fraction. If None, uses config.GANGUE_PHASES
            
        Returns:
        --------
        dict : Phase name → mass (g)
        """
        if gangue_phases is None:
            gangue_phases = config.GANGUE_PHASES
        
        phase_masses = {}
        for phase, fraction in gangue_phases.items():
            phase_masses[phase] = gangue_mass * fraction
        
        return phase_masses
    
    def generate_all_combinations_with_phases(self):
        """
        Generate all 4,928 mix design combinations WITH phase-based composition.
        
        This extends the basic mix design generator to include individual
        phase masses for cement, fly ash, and coal gangue. This is required
        for CemGEMS input generation.
        
        Returns:
        --------
        pandas.DataFrame : DataFrame with mix designs including phase masses
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
        
        print(f"Generating {len(combinations)} mix designs with phase compositions...")
        
        # Create list to store results
        mix_designs = []
        
        for idx, (R, f_FA, yCO2, w_SS, w_b) in enumerate(combinations):
            # Calculate raw material masses
            masses = self.calculate_raw_material_masses(R, f_FA, w_SS, w_b)
            
            # Calculate phase masses
            cement_phases = self.calculate_clinker_phase_masses(masses['cement_mass_g'])
            flyash_phases = self.calculate_flyash_phase_masses(masses['flyash_mass_g'])
            gangue_phases = self.calculate_gangue_phase_masses(masses['gangue_mass_g'])
            
            # Create mix design record
            mix_design = {
                'mix_id': f'MIX_{idx:04d}',
                'R': R,
                'f_FA': f_FA,
                'yCO2': yCO2,
                'w_SS': w_SS,
                'w_b': w_b,
                # Total material masses
                'cement_mass_g': masses['cement_mass_g'],
                'flyash_mass_g': masses['flyash_mass_g'],
                'gangue_mass_g': masses['gangue_mass_g'],
                'water_mass_g': masses['water_mass_g'],
                'sodium_silicate_mass_g': masses['sodium_silicate_mass_g'],
                'total_mass_g': masses['total_mass_g'],
            }
            
            # Add cement phase masses
            for phase, mass in cement_phases.items():
                mix_design[f'cement_{phase}_g'] = mass
            
            # Add fly ash phase masses
            for phase, mass in flyash_phases.items():
                mix_design[f'flyash_{phase}_g'] = mass
            
            # Add coal gangue phase masses
            for phase, mass in gangue_phases.items():
                mix_design[f'gangue_{phase}_g'] = mass
            
            mix_designs.append(mix_design)
        
        # Create DataFrame
        df = pd.DataFrame(mix_designs)
        
        print(f"✓ Generated {len(df)} mix designs with phase compositions")
        
        return df


def main():
    """Main function to generate all mix designs."""
    
    print("\n" + "=" * 80)
    print("Phase 2.1: Mix Design Generator")
    print("=" * 80 + "\n")
    
    # Create generator
    generator = MixDesignGenerator()
    
    # Generate all combinations (original - XRF only)
    df_mix_designs = generator.generate_all_combinations()
    
    # Print summary
    generator.print_summary(df_mix_designs)
    
    # Save to CSV
    generator.save_to_csv(df_mix_designs, filename='mix_designs.csv')
    
    # Generate all combinations WITH phase compositions (NEW - for CemGEMS)
    print("\n" + "=" * 80)
    print("Generating phase-based mix designs for CemGEMS...")
    print("=" * 80 + "\n")
    
    df_mix_designs_phases = generator.generate_all_combinations_with_phases()
    
    # Save phase-based mix designs
    generator.save_to_csv(df_mix_designs_phases, filename='mix_designs_with_phases.csv')
    
    # Print sample of phase-based mix designs
    print("\nSample phase-based mix designs (first 3):")
    phase_cols = ['mix_id', 'R', 'f_FA', 'yCO2', 
                  'cement_C3S_g', 'cement_C2S_g', 'cement_C3A_g',
                  'flyash_Glass_g', 'flyash_Quartz_g', 
                  'gangue_Quartz_g', 'gangue_Kaolinite_g']
    if all(col in df_mix_designs_phases.columns for col in phase_cols):
        print(df_mix_designs_phases[phase_cols].head(3).to_string(index=False))
    
    print("\n" + "=" * 80)
    print("Mix Design Generation: COMPLETE ✓")
    print("  • Basic mix designs: mix_designs.csv")
    print("  • Phase-based mix designs: mix_designs_with_phases.csv")
    print("=" * 80 + "\n")
    
    return df_mix_designs, df_mix_designs_phases


if __name__ == '__main__':
    df, df_phases = main()
