"""
xGEMS Input Writer
==================
Generates GEMS3K/xGEMS input files for all 4,928 mix designs.

For each mix design:
- Reads bulk composition from Phase 2 data
- Generates complete GEMS input file
- Sets appropriate CO₂ gas phase composition
- Writes to inputs/generated/ directory

Author: Thermodynamic Modeling Project
Date: December 27, 2025
"""

import sys
from pathlib import Path

SCRIPTS_DIR = Path(__file__).parent
if str(SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_DIR))

import pandas as pd
import config
from xgems_template import GEMSTemplate


class GEMSInputWriter:
    """Generate GEMS input files from mix design data."""
    
    def __init__(self):
        """Initialize the input writer."""
        self.template = GEMSTemplate()
        self.output_dir = config.INPUTS_GENERATED_DIR
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
    def load_mix_designs_with_compositions(self):
        """
        Load mix designs with elemental compositions from Phase 2.
        
        Returns:
        --------
        pandas.DataFrame : Mix designs with compositions
        """
        data_path = config.OUTPUTS_TABLES_DIR / 'mix_designs_with_compositions.csv'
        
        if not data_path.exists():
            raise FileNotFoundError(
                f"Mix designs with compositions not found: {data_path}\n"
                "Run oxide_calculator.py first."
            )
        
        df = pd.read_csv(data_path)
        print(f"✓ Loaded {len(df)} mix designs with compositions")
        
        return df
    
    def generate_input_file_content(self, row):
        """
        Generate complete input file content for a mix design.
        
        Parameters:
        -----------
        row : pandas.Series
            Row from mix design DataFrame
            
        Returns:
        --------
        str : Complete input file content
        """
        mix_id = row['mix_id']
        
        # Build description
        description = (
            f"R={row['R']:.2f}, f_FA={row['f_FA']:.2f}, "
            f"yCO2={row['yCO2']:.2f}, w_SS={row['w_SS']:.2f}, w_b={row['w_b']:.2f}"
        )
        
        # Start with header
        content = self.template.generate_input_header(mix_id, description)
        
        # System definition
        content += self.template.generate_system_definition()
        
        # Phases definition
        content += self.template.generate_phases_definition()
        
        # Conditions
        content += self.template.generate_conditions_section()
        
        # Bulk composition (actual values from Phase 2)
        content += self._generate_bulk_composition(row)
        
        # Gas phase (with actual CO2 fraction)
        content += self._generate_gas_phase(row)
        
        # Solver options
        content += self.template.generate_solver_options_section()
        
        # Additional metadata
        content += self._generate_metadata(row)
        
        return content
    
    def _generate_bulk_composition(self, row):
        """
        Generate bulk composition section with actual values.
        
        Parameters:
        -----------
        row : pandas.Series
            Row with element moles
            
        Returns:
        --------
        str : Bulk composition text
        """
        components = self.template.get_independent_components()
        
        text = "# BULK COMPOSITION (moles)\n"
        text += "bulk_composition:\n"
        
        for comp in components:
            col_name = f'{comp}_mol'
            if col_name in row:
                moles = row[col_name]
                text += f"  {comp}: {moles:.10f}\n"
            else:
                text += f"  {comp}: 0.0000000000\n"
        
        text += "\n"
        return text
    
    def _generate_gas_phase(self, row):
        """
        Generate gas phase section with CO2 fraction.
        
        Parameters:
        -----------
        row : pandas.Series
            Row with yCO2 value
            
        Returns:
        --------
        str : Gas phase text
        """
        yCO2 = row['yCO2']
        yN2 = 1.0 - yCO2  # Assuming CO2 + N2 = 1 (simplified)
        
        text = "# GAS PHASE\n"
        text += "gas_phase:\n"
        text += "  enabled: true\n"
        text += f"  CO2_fraction: {yCO2:.6f}  # Volume fraction\n"
        text += f"  N2_fraction: {yN2:.6f}   # Volume fraction\n"
        text += f"  total_pressure_bar: {config.TOTAL_PRESSURE_BAR}\n"
        
        # Additional info
        if 'CO2_moles' in row:
            text += f"  # Estimated CO2 moles: {row['CO2_moles']:.6f}\n"
        
        text += "\n"
        return text
    
    def _generate_metadata(self, row):
        """
        Generate metadata section with mix design parameters.
        
        Parameters:
        -----------
        row : pandas.Series
            Row with mix design data
            
        Returns:
        --------
        str : Metadata text
        """
        text = "# METADATA\n"
        text += "metadata:\n"
        text += f"  mix_id: {row['mix_id']}\n"
        text += f"  R: {row['R']}\n"
        text += f"  f_FA: {row['f_FA']}\n"
        text += f"  yCO2: {row['yCO2']}\n"
        text += f"  w_SS: {row['w_SS']}\n"
        text += f"  w_b: {row['w_b']}\n"
        
        # Raw material masses
        text += "  raw_materials_g:\n"
        text += f"    cement: {row['cement_mass_g']:.6f}\n"
        text += f"    flyash: {row['flyash_mass_g']:.6f}\n"
        text += f"    gangue: {row['gangue_mass_g']:.6f}\n"
        text += f"    water: {row['water_mass_g']:.6f}\n"
        text += f"    sodium_silicate: {row['sodium_silicate_mass_g']:.6f}\n"
        text += f"    total: {row['total_mass_g']:.6f}\n"
        
        # Elemental mass total
        if 'total_element_mass_g' in row:
            text += f"  total_element_mass_g: {row['total_element_mass_g']:.6f}\n"
        
        text += "\n"
        return text
    
    def write_input_file(self, row, filename=None):
        """
        Write input file for a single mix design.
        
        Parameters:
        -----------
        row : pandas.Series
            Row from mix design DataFrame
        filename : str, optional
            Output filename (default: {mix_id}.inp)
            
        Returns:
        --------
        Path : Path to written file
        """
        if filename is None:
            filename = f"{row['mix_id']}.inp"
        
        content = self.generate_input_file_content(row)
        
        output_path = self.output_dir / filename
        with open(output_path, 'w') as f:
            f.write(content)
        
        return output_path
    
    def generate_all_input_files(self, max_files=None):
        """
        Generate all input files.
        
        Parameters:
        -----------
        max_files : int, optional
            Maximum number of files to generate (for testing)
            
        Returns:
        --------
        list : List of generated file paths
        """
        # Load data
        df = self.load_mix_designs_with_compositions()
        
        # Limit for testing
        if max_files is not None:
            df = df.head(max_files)
            print(f"⚠ Limiting to first {max_files} files for testing")
        
        print(f"\nGenerating {len(df)} input files...")
        
        generated_files = []
        
        for idx, row in df.iterrows():
            output_path = self.write_input_file(row)
            generated_files.append(output_path)
            
            if (idx + 1) % 500 == 0:
                print(f"  Generated {idx + 1}/{len(df)} files...")
        
        print(f"✓ Generated all {len(generated_files)} input files")
        
        return generated_files
    
    def verify_generated_files(self, sample_size=5):
        """
        Verify generated files by checking a sample.
        
        Parameters:
        -----------
        sample_size : int
            Number of files to check
        """
        print(f"\nVerifying generated files (sampling {sample_size})...")
        
        files = list(self.output_dir.glob('*.inp'))
        
        if len(files) == 0:
            print("  ✗ No input files found")
            return
        
        print(f"  Found {len(files)} input files")
        
        # Check sample
        import random
        sample_files = random.sample(files, min(sample_size, len(files)))
        
        for fpath in sample_files:
            # Check file size
            size = fpath.stat().st_size
            
            # Check content
            with open(fpath, 'r') as f:
                content = f.read()
                
            has_header = '# GEMS3K Input File' in content
            has_components = 'components:' in content
            has_composition = 'bulk_composition:' in content
            has_gas = 'gas_phase:' in content
            
            status = "✓" if all([has_header, has_components, has_composition, has_gas]) else "✗"
            print(f"  {status} {fpath.name}: {size} bytes")
        
        print("  Verification complete")


def main():
    """Main function to generate all input files."""
    print("\n" + "=" * 80)
    print("Phase 3.2: xGEMS Input Writer")
    print("=" * 80 + "\n")
    
    # Create writer
    writer = GEMSInputWriter()
    
    # Generate all files
    # For initial testing, you can use max_files=10
    # For full generation, remove max_files parameter
    generated_files = writer.generate_all_input_files()  # Full: 4,928 files
    
    # Verify
    writer.verify_generated_files(sample_size=10)
    
    # Display sample
    if len(generated_files) > 0:
        print("\nSample input file (MIX_0000.inp):")
        print("-" * 80)
        sample_file = config.INPUTS_GENERATED_DIR / 'MIX_0000.inp'
        if sample_file.exists():
            with open(sample_file, 'r') as f:
                for i, line in enumerate(f):
                    if i >= 50:
                        print("...")
                        break
                    print(line, end='')
        print("-" * 80)
    
    # Statistics
    total_size = sum(f.stat().st_size for f in generated_files if f.exists())
    avg_size = total_size / len(generated_files) if generated_files else 0
    
    print(f"\nStatistics:")
    print(f"  Total files: {len(generated_files)}")
    print(f"  Total size: {total_size / 1024:.2f} KB ({total_size / (1024*1024):.2f} MB)")
    print(f"  Average file size: {avg_size:.2f} bytes")
    
    print("\n" + "=" * 80)
    print("Input File Generation: COMPLETE ✓")
    print("=" * 80 + "\n")
    
    print("Generated files location:")
    print(f"  {config.INPUTS_GENERATED_DIR}")
    print(f"\nReady for Phase 4: Batch Execution")
    
    return writer


if __name__ == '__main__':
    writer = main()
