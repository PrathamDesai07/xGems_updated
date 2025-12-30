"""
Oxide Calculator
================
Converts raw material masses to oxide masses and elemental mole compositions.

For each mix design:
- Converts material masses → oxide masses (using XRF data)
- Converts oxide masses → elemental masses
- Converts elemental masses → moles
- Accounts for CO₂ from gas phase
- Validates mass balance

Author: Thermodynamic Modeling Project
Date: December 27, 2025
"""

import sys
from pathlib import Path

# Add scripts directory to path
SCRIPTS_DIR = Path(__file__).parent
if str(SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_DIR))

import numpy as np
import pandas as pd
import config


class OxideCalculator:
    """Calculate oxide and elemental compositions from raw material masses."""
    
    def __init__(self):
        """Initialize the oxide calculator."""
        self.oxide_masses = config.OXIDE_MOLAR_MASSES
        self.element_masses = config.ELEMENT_ATOMIC_MASSES
        self.conversion_factors = config.OXIDE_TO_ELEMENT_FACTORS
        
    def calculate_oxides_from_material(self, material_mass, material_composition):
        """
        Calculate oxide masses from raw material mass and composition.
        
        Parameters:
        -----------
        material_mass : float
            Mass of the raw material (g)
        material_composition : dict
            XRF composition (wt% of each oxide)
            
        Returns:
        --------
        dict : Oxide masses (g)
        """
        oxide_masses = {}
        
        for oxide, wt_percent in material_composition.items():
            oxide_mass = material_mass * wt_percent / 100.0
            oxide_masses[oxide] = oxide_mass
            
        return oxide_masses
    
    def calculate_elements_from_oxides(self, oxide_masses):
        """
        Calculate elemental masses from oxide masses.
        
        Parameters:
        -----------
        oxide_masses : dict
            Masses of each oxide (g)
            
        Returns:
        --------
        dict : Elemental masses (g)
        """
        element_masses = {}
        
        for oxide, oxide_mass in oxide_masses.items():
            if oxide_mass > 0 and oxide in self.conversion_factors:
                factors = self.conversion_factors[oxide]
                
                for element, factor in factors.items():
                    element_mass = oxide_mass * factor
                    
                    if element in element_masses:
                        element_masses[element] += element_mass
                    else:
                        element_masses[element] = element_mass
        
        return element_masses
    
    def calculate_sodium_silicate_contribution(self, sodium_silicate_mass):
        """
        Calculate elemental contributions from sodium silicate.
        
        Parameters:
        -----------
        sodium_silicate_mass : float
            Mass of sodium silicate (g)
            
        Returns:
        --------
        dict : Elemental masses from sodium silicate (g)
        """
        # Sodium silicate composition: Na2O, SiO2, H2O
        ss_comp = config.SODIUM_SILICATE_COMPOSITION
        
        # Calculate oxide masses
        m_Na2O = sodium_silicate_mass * ss_comp['Na2O'] / 100.0
        m_SiO2 = sodium_silicate_mass * ss_comp['SiO2'] / 100.0
        m_H2O = sodium_silicate_mass * ss_comp['H2O'] / 100.0
        
        # Convert to elements
        oxide_masses = {
            'Na2O': m_Na2O,
            'SiO2': m_SiO2,
            'H2O': m_H2O,
        }
        
        element_masses = self.calculate_elements_from_oxides(oxide_masses)
        
        return element_masses
    
    def calculate_water_contribution(self, water_mass):
        """
        Calculate elemental contributions from water.
        
        Parameters:
        -----------
        water_mass : float
            Mass of water (g)
            
        Returns:
        --------
        dict : Elemental masses from water (g)
        """
        # Water: H2O
        factors = self.conversion_factors['H2O']
        
        element_masses = {
            'H': water_mass * factors['H'],
            'O': water_mass * factors['O'],
        }
        
        return element_masses
    
    def calculate_co2_contribution(self, yCO2, total_mass):
        """
        Calculate CO₂ contribution based on gas phase concentration.
        
        For a closed system with gas phase, we need to estimate the amount
        of CO₂ in the system. This is simplified - assuming equilibrium
        with a certain gas volume.
        
        Parameters:
        -----------
        yCO2 : float
            CO₂ volume fraction in gas phase
        total_mass : float
            Total mass of solids + water (g)
            
        Returns:
        --------
        dict : Elemental masses from CO₂ (g)
        """
        # Simplified approach: assume a fixed gas/solid ratio
        # For closed system carbonation, we can estimate CO2 amount
        # This is a simplification - actual amount would depend on vessel volume
        
        # Assume gas volume ~ 10x the slurry volume
        # Slurry density ~ 2 g/cm³, so volume ~ total_mass / 2 cm³
        slurry_volume_cm3 = total_mass / 2.0
        gas_volume_cm3 = 10.0 * slurry_volume_cm3  # 10x gas volume
        
        # At 25°C and 1 atm, ideal gas: n = PV/RT
        # P = 1 atm, V in L, R = 0.08206 L·atm/(mol·K), T = 298.15 K
        T_K = config.TEMPERATURE_K
        P_atm = config.TOTAL_PRESSURE_ATM
        R = 0.08206  # L·atm/(mol·K)
        
        gas_volume_L = gas_volume_cm3 / 1000.0
        
        # Total moles of gas
        n_total = (P_atm * gas_volume_L) / (R * T_K)
        
        # Moles of CO₂
        n_CO2 = yCO2 * n_total
        
        # Mass of CO₂
        m_CO2 = n_CO2 * self.oxide_masses['CO2']
        
        # Convert to elements
        factors = self.conversion_factors['CO2']
        element_masses = {
            'C': m_CO2 * factors['C'],
            'O': m_CO2 * factors['O'],
        }
        
        return element_masses, n_CO2
    
    def calculate_total_composition(self, mix_design_row):
        """
        Calculate total elemental composition for a mix design.
        
        Parameters:
        -----------
        mix_design_row : pandas.Series or dict
            Row from mix design DataFrame
            
        Returns:
        --------
        dict : Contains elemental masses, moles, and metadata
        """
        # Extract masses from mix design
        m_cement = mix_design_row['cement_mass_g']
        m_flyash = mix_design_row['flyash_mass_g']
        m_gangue = mix_design_row['gangue_mass_g']
        m_water = mix_design_row['water_mass_g']
        m_sodium_silicate = mix_design_row['sodium_silicate_mass_g']
        yCO2 = mix_design_row['yCO2']
        
        # Initialize total element masses
        total_elements = {}
        
        # 1. Coal gangue contribution
        if m_gangue > 0:
            gangue_oxides = self.calculate_oxides_from_material(
                m_gangue, config.COAL_GANGUE_COMPOSITION
            )
            gangue_elements = self.calculate_elements_from_oxides(gangue_oxides)
            
            for element, mass in gangue_elements.items():
                total_elements[element] = total_elements.get(element, 0) + mass
        
        # 2. Cement contribution
        if m_cement > 0:
            cement_oxides = self.calculate_oxides_from_material(
                m_cement, config.CEMENT_COMPOSITION
            )
            cement_elements = self.calculate_elements_from_oxides(cement_oxides)
            
            for element, mass in cement_elements.items():
                total_elements[element] = total_elements.get(element, 0) + mass
        
        # 3. Fly ash contribution
        if m_flyash > 0:
            flyash_oxides = self.calculate_oxides_from_material(
                m_flyash, config.FLY_ASH_COMPOSITION
            )
            flyash_elements = self.calculate_elements_from_oxides(flyash_oxides)
            
            for element, mass in flyash_elements.items():
                total_elements[element] = total_elements.get(element, 0) + mass
        
        # 4. Sodium silicate contribution
        if m_sodium_silicate > 0:
            ss_elements = self.calculate_sodium_silicate_contribution(m_sodium_silicate)
            
            for element, mass in ss_elements.items():
                total_elements[element] = total_elements.get(element, 0) + mass
        
        # 5. Water contribution
        if m_water > 0:
            water_elements = self.calculate_water_contribution(m_water)
            
            for element, mass in water_elements.items():
                total_elements[element] = total_elements.get(element, 0) + mass
        
        # 6. CO₂ contribution (from gas phase)
        total_mass = mix_design_row['total_mass_g']
        co2_elements, n_CO2 = self.calculate_co2_contribution(yCO2, total_mass)
        
        for element, mass in co2_elements.items():
            total_elements[element] = total_elements.get(element, 0) + mass
        
        # Convert elemental masses to moles
        element_moles = {}
        for element in config.SYSTEM_COMPONENTS:
            if element in total_elements:
                element_moles[element] = total_elements[element] / self.element_masses[element]
            else:
                element_moles[element] = 0.0
        
        # Calculate total mass (including CO₂)
        total_element_mass = sum(total_elements.values())
        
        return {
            'element_masses_g': total_elements,
            'element_moles': element_moles,
            'total_element_mass_g': total_element_mass,
            'CO2_moles': n_CO2,
        }
    
    def process_all_mix_designs(self, df_mix_designs):
        """
        Process all mix designs to calculate compositions.
        
        Parameters:
        -----------
        df_mix_designs : pandas.DataFrame
            DataFrame with mix designs
            
        Returns:
        --------
        pandas.DataFrame : DataFrame with compositions added
        """
        print(f"\nProcessing {len(df_mix_designs)} mix designs...")
        
        compositions = []
        
        for idx, row in df_mix_designs.iterrows():
            comp = self.calculate_total_composition(row)
            
            # Create composition record
            comp_record = {
                'mix_id': row['mix_id'],
            }
            
            # Add element moles
            for element in config.SYSTEM_COMPONENTS:
                comp_record[f'{element}_mol'] = comp['element_moles'].get(element, 0.0)
            
            # Add metadata
            comp_record['total_element_mass_g'] = comp['total_element_mass_g']
            comp_record['CO2_moles'] = comp['CO2_moles']
            
            compositions.append(comp_record)
            
            if (idx + 1) % 1000 == 0:
                print(f"  Processed {idx + 1}/{len(df_mix_designs)} mix designs...")
        
        df_compositions = pd.DataFrame(compositions)
        
        # Merge with original mix designs
        df_full = df_mix_designs.merge(df_compositions, on='mix_id', how='left')
        
        print(f"✓ Processed all {len(df_full)} mix designs")
        
        return df_full
    
    def validate_mass_balance(self, df_full):
        """
        Validate mass balance for all mix designs.
        
        Parameters:
        -----------
        df_full : pandas.DataFrame
            Full DataFrame with mix designs and compositions
            
        Returns:
        --------
        dict : Validation statistics
        """
        print("\nValidating mass balance...")
        
        # Calculate input total mass (raw materials)
        df_full['input_mass'] = (
            df_full['cement_mass_g'] + 
            df_full['flyash_mass_g'] + 
            df_full['gangue_mass_g'] + 
            df_full['water_mass_g'] + 
            df_full['sodium_silicate_mass_g']
        )
        
        # Compare with calculated element mass
        df_full['mass_balance_error'] = (
            (df_full['total_element_mass_g'] - df_full['input_mass']) / 
            df_full['input_mass'] * 100.0
        )
        
        max_error = df_full['mass_balance_error'].abs().max()
        mean_error = df_full['mass_balance_error'].abs().mean()
        
        print(f"  Maximum mass balance error: {max_error:.6f}%")
        print(f"  Mean mass balance error: {mean_error:.6f}%")
        
        if max_error < 1.0:
            print("  ✓ Mass balance validated (error < 1%)")
        else:
            print("  ⚠ Mass balance errors detected")
        
        return {
            'max_error_percent': max_error,
            'mean_error_percent': mean_error,
        }


def main():
    """Main function to calculate compositions."""
    
    print("\n" + "=" * 80)
    print("Phase 2.2: Oxide Calculator")
    print("=" * 80 + "\n")
    
    # Load mix designs
    mix_designs_path = config.OUTPUTS_TABLES_DIR / 'mix_designs.csv'
    
    if not mix_designs_path.exists():
        print("ERROR: Mix designs not found. Run mix_design_generator.py first.")
        return None
    
    print(f"Loading mix designs from: {mix_designs_path}")
    df_mix_designs = pd.read_csv(mix_designs_path)
    print(f"✓ Loaded {len(df_mix_designs)} mix designs")
    
    # Create calculator
    calculator = OxideCalculator()
    
    # Process all mix designs
    df_full = calculator.process_all_mix_designs(df_mix_designs)
    
    # Validate mass balance
    validation = calculator.validate_mass_balance(df_full)
    
    # Save full dataset
    output_path = config.OUTPUTS_TABLES_DIR / 'mix_designs_with_compositions.csv'
    df_full.to_csv(output_path, index=False, float_format='%.8f')
    print(f"\n✓ Saved full dataset to: {output_path}")
    
    # Print sample
    print("\nSample compositions (first 5 mix designs):")
    sample_cols = ['mix_id', 'R', 'f_FA', 'yCO2', 'Ca_mol', 'Si_mol', 'Al_mol', 'C_mol', 'O_mol', 'H_mol']
    print(df_full[sample_cols].head(5).to_string(index=False))
    
    print("\n" + "=" * 80)
    print("Oxide Calculation: COMPLETE ✓")
    print("=" * 80 + "\n")
    
    return df_full


if __name__ == '__main__':
    df = main()
