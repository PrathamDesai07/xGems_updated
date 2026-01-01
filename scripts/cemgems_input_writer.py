"""
CemGEMS Input File Generator
=============================
Generates CemGEMS/GEMS input files from phase-based mix designs with bulk compositions.

This module reads the mix_designs_phases_with_compositions.csv file and creates
input files for thermodynamic equilibrium calculations in CemGEMS.

Input Format: JSON-based structure for CemGEMS v3+ (GEMS3K format)
Output: One input file per mix design (4,928 files total)

Author: Thermodynamic Modeling Project
Date: December 31, 2025
"""

import sys
from pathlib import Path
import json
from typing import Dict, List, Optional, Tuple

# Add scripts directory to path
SCRIPTS_DIR = Path(__file__).parent
if str(SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_DIR))

import numpy as np
import pandas as pd
import config


class CemGEMSInputWriter:
    """
    Generate CemGEMS input files from bulk compositions.
    
    Supports both JSON format (GEMS3K) and text format (legacy).
    """
    
    def __init__(self, output_dir=None, format='json'):
        """
        Initialize the CemGEMS input writer.
        
        Parameters:
        -----------
        output_dir : Path or str, optional
            Directory for generated input files. Default: config.INPUTS_GENERATED_DIR
        format : str, optional
            Input file format: 'json' (default) or 'text'
        """
        self.output_dir = Path(output_dir) if output_dir else config.INPUTS_GENERATED_DIR
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.format = format.lower()
        
        # Load element data
        self.elements = config.SYSTEM_COMPONENTS
        self.element_masses = config.ELEMENT_ATOMIC_MASSES
        
        # Load phase data
        self.enabled_phases = self._flatten_phase_dict(config.ENABLED_PHASES)
        
        # Thermodynamic conditions
        self.temperature_k = config.TEMPERATURE_K
        self.pressure_bar = config.TOTAL_PRESSURE_BAR
        
    def _flatten_phase_dict(self, phase_dict: Dict[str, List[str]]) -> List[str]:
        """
        Flatten nested phase dictionary to single list.
        
        Parameters:
        -----------
        phase_dict : dict
            Nested dictionary of phase categories and phase names
            
        Returns:
        --------
        list
            Flat list of all phase names
        """
        phases = []
        for category, phase_list in phase_dict.items():
            phases.extend(phase_list)
        return phases
    
    def create_bulk_composition(self, row: pd.Series) -> Dict[str, float]:
        """
        Extract bulk composition (element moles) from mix design row.
        
        Parameters:
        -----------
        row : pd.Series
            Row from mix_designs_phases_with_compositions.csv
            
        Returns:
        --------
        dict
            Bulk composition: {element: moles}
        """
        composition = {}
        for element in self.elements:
            col_name = f"{element}_mol"
            if col_name in row.index:
                moles = float(row[col_name])
                if moles > 0:  # Only include non-zero elements
                    composition[element] = moles
            else:
                # Fallback: check without suffix
                if element in row.index:
                    composition[element] = float(row[element])
        
        return composition
    
    def calculate_pco2(self, yCO2: float, total_pressure_bar: float = None) -> float:
        """
        Calculate CO2 partial pressure from volume fraction.
        
        Parameters:
        -----------
        yCO2 : float
            CO2 volume fraction (0.0 to 1.0)
        total_pressure_bar : float, optional
            Total pressure in bar. Default: config.TOTAL_PRESSURE_BAR
            
        Returns:
        --------
        float
            CO2 partial pressure in bar
        """
        if total_pressure_bar is None:
            total_pressure_bar = self.pressure_bar
        return yCO2 * total_pressure_bar
    
    def create_gas_phase_composition(self, yCO2: float) -> Dict[str, float]:
        """
        Create gas phase composition for CemGEMS.
        
        Parameters:
        -----------
        yCO2 : float
            CO2 volume fraction
            
        Returns:
        --------
        dict
            Gas phase composition with partial pressures (bar)
        """
        total_p = self.pressure_bar
        pCO2 = self.calculate_pco2(yCO2, total_p)
        pH2O = total_p - pCO2  # Remainder is water vapor
        
        gas_composition = {}
        # Only include gas phase if CO2 is present
        # (otherwise system is assumed to be in aqueous solution only)
        if pCO2 > 1e-10:  # Small threshold to handle floating point
            gas_composition['CO2'] = pCO2
            if pH2O > 0:
                gas_composition['H2O_gas'] = pH2O
            
        return gas_composition
    
    def create_json_input(self, row: pd.Series, mix_id: str) -> Dict:
        """
        Create JSON-format CemGEMS input structure.
        
        This creates a GEMS3K-compatible JSON input file.
        
        Parameters:
        -----------
        row : pd.Series
            Mix design row with bulk composition
        mix_id : str
            Mix design identifier (e.g., 'MIX_0000')
            
        Returns:
        --------
        dict
            Complete GEMS3K input structure
        """
        # Extract bulk composition
        bulk_composition = self.create_bulk_composition(row)
        
        # Get mix parameters
        R = float(row['R'])
        f_FA = float(row['f_FA'])
        yCO2 = float(row['yCO2'])
        w_SS = float(row['w_SS'])
        w_b = float(row['w_b'])
        
        # Calculate gas phase
        gas_composition = self.create_gas_phase_composition(yCO2)
        pCO2 = self.calculate_pco2(yCO2)
        
        # Create GEMS3K input structure
        input_data = {
            "task": {
                "name": f"Carbonation equilibrium - {mix_id}",
                "description": f"Fly ash + cement + sodium silicate + coal gangue system",
                "calculation_type": "equilibrium",
                "database": config.DATABASE,
                "database_version": config.DATABASE_VERSION
            },
            
            "conditions": {
                "temperature_K": self.temperature_k,
                "pressure_bar": self.pressure_bar,
                "pCO2_bar": pCO2
            },
            
            "mix_parameters": {
                "R_binder_aggregate": R,
                "f_FA_replacement": f_FA,
                "yCO2_volume_fraction": yCO2,
                "w_SS_dosage": w_SS,
                "w_b_ratio": w_b
            },
            
            "system": {
                "components": list(bulk_composition.keys()),
                "component_amounts": bulk_composition,
                "component_units": "moles"
            },
            
            "phases": {
                "enabled": self.enabled_phases,
                "aqueous_solution": {
                    "enabled": True,
                    "name": "AqueousSolution"
                },
                "gas_phase": {
                    "enabled": len(gas_composition) > 0,
                    "composition": gas_composition,
                    "units": "bar"
                }
            },
            
            "solver": {
                "method": config.CEMGEMS_SOLVER_OPTIONS['gibbs_method'],
                "max_iterations": config.CEMGEMS_SOLVER_OPTIONS['max_iterations'],
                "tolerance": config.CEMGEMS_SOLVER_OPTIONS['convergence_tolerance'],
                "timeout_seconds": config.CEMGEMS_SOLVER_OPTIONS['timeout_seconds']
            },
            
            "output": {
                "phases": True,
                "phase_amounts": True,
                "aqueous_species": True,
                "element_distribution": True,
                "format": "json"
            }
        }
        
        return input_data
    
    def create_text_input(self, row: pd.Series, mix_id: str) -> str:
        """
        Create text-format CemGEMS input file (legacy format).
        
        Parameters:
        -----------
        row : pd.Series
            Mix design row with bulk composition
        mix_id : str
            Mix design identifier
            
        Returns:
        --------
        str
            Text input file content
        """
        # Extract data
        bulk_composition = self.create_bulk_composition(row)
        R = float(row['R'])
        f_FA = float(row['f_FA'])
        yCO2 = float(row['yCO2'])
        w_SS = float(row['w_SS'])
        w_b = float(row['w_b'])
        pCO2 = self.calculate_pco2(yCO2)
        
        # Build text input
        lines = []
        lines.append(f"# CemGEMS Input File - {mix_id}")
        lines.append(f"# Generated: {pd.Timestamp.now()}")
        lines.append("#" + "="*70)
        lines.append("")
        
        # Task definition
        lines.append("[TASK]")
        lines.append(f"NAME = Carbonation equilibrium - {mix_id}")
        lines.append(f"TYPE = equilibrium")
        lines.append(f"DATABASE = {config.DATABASE}")
        lines.append("")
        
        # Conditions
        lines.append("[CONDITIONS]")
        lines.append(f"TEMPERATURE = {self.temperature_k:.2f}  # K")
        lines.append(f"PRESSURE = {self.pressure_bar:.6f}  # bar")
        lines.append(f"PCO2 = {pCO2:.8f}  # bar")
        lines.append("")
        
        # Mix parameters (for documentation)
        lines.append("[MIX_PARAMETERS]")
        lines.append(f"R = {R:.8f}  # Binder/aggregate ratio")
        lines.append(f"f_FA = {f_FA:.8f}  # Fly ash replacement")
        lines.append(f"yCO2 = {yCO2:.8f}  # CO2 volume fraction")
        lines.append(f"w_SS = {w_SS:.8f}  # Sodium silicate dosage")
        lines.append(f"w_b = {w_b:.8f}  # Water/binder ratio")
        lines.append("")
        
        # Bulk composition
        lines.append("[BULK_COMPOSITION]")
        lines.append("# Element amounts in moles")
        for element in sorted(bulk_composition.keys()):
            moles = bulk_composition[element]
            lines.append(f"{element:<4} = {moles:18.10e}")
        lines.append("")
        
        # Enabled phases
        lines.append("[PHASES]")
        lines.append("# Solid phases")
        for phase in self.enabled_phases:
            lines.append(f"  {phase}")
        lines.append("")
        lines.append("# Aqueous solution")
        lines.append("  AqueousSolution")
        lines.append("")
        if pCO2 > 0 or yCO2 > 0:
            lines.append("# Gas phase")
            lines.append("  GasPhase")
            lines.append(f"    CO2 = {pCO2:.8f} bar")
            pH2O = self.pressure_bar - pCO2
            if pH2O > 0:
                lines.append(f"    H2O = {pH2O:.8f} bar")
        lines.append("")
        
        # Solver options
        lines.append("[SOLVER]")
        lines.append(f"METHOD = {config.CEMGEMS_SOLVER_OPTIONS['gibbs_method']}")
        lines.append(f"MAX_ITERATIONS = {config.CEMGEMS_SOLVER_OPTIONS['max_iterations']}")
        lines.append(f"TOLERANCE = {config.CEMGEMS_SOLVER_OPTIONS['convergence_tolerance']:.2e}")
        lines.append(f"TIMEOUT = {config.CEMGEMS_SOLVER_OPTIONS['timeout_seconds']} seconds")
        lines.append("")
        
        # End marker
        lines.append("#" + "="*70)
        lines.append("# End of input file")
        
        return '\n'.join(lines)
    
    def write_input_file(self, row: pd.Series, mix_id: str = None) -> Path:
        """
        Write input file for a single mix design.
        
        Parameters:
        -----------
        row : pd.Series
            Mix design row from DataFrame
        mix_id : str, optional
            Mix identifier. If None, extracted from row['mix_id']
            
        Returns:
        --------
        Path
            Path to created input file
        """
        if mix_id is None:
            mix_id = str(row['mix_id'])
        
        # Create input data
        if self.format == 'json':
            input_data = self.create_json_input(row, mix_id)
            extension = '.json'
        else:
            input_data = self.create_text_input(row, mix_id)
            extension = '.inp'
        
        # Determine output path
        output_path = self.output_dir / f"{mix_id}{extension}"
        
        # Write file
        if self.format == 'json':
            with open(output_path, 'w') as f:
                json.dump(input_data, f, indent=2)
        else:
            with open(output_path, 'w') as f:
                f.write(input_data)
        
        return output_path
    
    def generate_all_inputs(self, df: pd.DataFrame = None, 
                           input_csv: str = None,
                           max_files: int = None,
                           verbose: bool = True) -> List[Path]:
        """
        Generate input files for all mix designs.
        
        Parameters:
        -----------
        df : pd.DataFrame, optional
            DataFrame with mix designs and compositions
        input_csv : str or Path, optional
            Path to CSV file with mix designs. Required if df is None.
        max_files : int, optional
            Maximum number of files to generate (for testing). None = all
        verbose : bool, optional
            Print progress messages
            
        Returns:
        --------
        list
            List of paths to created input files
        """
        # Load data if needed
        if df is None:
            if input_csv is None:
                input_csv = config.OUTPUTS_TABLES_DIR / "mix_designs_phases_with_compositions.csv"
            if verbose:
                print(f"Loading mix designs from: {input_csv}")
            df = pd.read_csv(input_csv)
        
        # Limit number of files if requested
        if max_files is not None:
            df = df.head(max_files)
            if verbose:
                print(f"Limiting to first {max_files} mix designs")
        
        # Generate input files
        output_paths = []
        total = len(df)
        
        if verbose:
            print(f"\nGenerating {total} CemGEMS input files ({self.format} format)...")
            print(f"Output directory: {self.output_dir}")
        
        for idx, row in df.iterrows():
            # Write input file
            output_path = self.write_input_file(row)
            output_paths.append(output_path)
            
            # Progress reporting
            if verbose and (idx + 1) % 500 == 0:
                print(f"  Progress: {idx + 1}/{total} files ({100*(idx+1)/total:.1f}%)")
        
        if verbose:
            print(f"\n✓ Successfully generated {len(output_paths)} input files")
            print(f"  Files saved to: {self.output_dir}")
            
            # Show sample file
            if len(output_paths) > 0:
                sample_file = output_paths[0]
                file_size_kb = sample_file.stat().st_size / 1024
                print(f"\n  Sample file: {sample_file.name}")
                print(f"  File size: {file_size_kb:.2f} KB")
        
        return output_paths
    
    def validate_input_file(self, input_path: Path) -> Tuple[bool, str]:
        """
        Validate a generated input file.
        
        Parameters:
        -----------
        input_path : Path
            Path to input file to validate
            
        Returns:
        --------
        tuple
            (is_valid: bool, message: str)
        """
        if not input_path.exists():
            return False, f"File does not exist: {input_path}"
        
        try:
            if self.format == 'json':
                # Validate JSON structure
                with open(input_path, 'r') as f:
                    data = json.load(f)
                
                # Check required sections
                required_sections = ['task', 'conditions', 'system', 'phases']
                for section in required_sections:
                    if section not in data:
                        return False, f"Missing required section: {section}"
                
                # Check bulk composition
                if 'component_amounts' not in data['system']:
                    return False, "Missing bulk composition (component_amounts)"
                
                bulk = data['system']['component_amounts']
                if len(bulk) == 0:
                    return False, "Empty bulk composition"
                
                # Check all values are positive
                for element, moles in bulk.items():
                    if moles <= 0:
                        return False, f"Non-positive amount for {element}: {moles}"
                
            else:
                # Validate text format
                with open(input_path, 'r') as f:
                    content = f.read()
                
                # Check required sections
                required_sections = ['[TASK]', '[CONDITIONS]', '[BULK_COMPOSITION]', '[PHASES]']
                for section in required_sections:
                    if section not in content:
                        return False, f"Missing required section: {section}"
            
            return True, "Valid input file"
            
        except Exception as e:
            return False, f"Validation error: {str(e)}"


def create_input_template(output_path: Path = None, format: str = 'json') -> Path:
    """
    Create a template input file for manual editing.
    
    Parameters:
    -----------
    output_path : Path, optional
        Output path for template. Default: inputs/templates/template.{format}
    format : str, optional
        'json' or 'text'
        
    Returns:
    --------
    Path
        Path to created template file
    """
    if output_path is None:
        ext = '.json' if format == 'json' else '.inp'
        output_path = config.INPUTS_TEMPLATES_DIR / f"template{ext}"
    
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    # Create dummy row with example values
    example_row = pd.Series({
        'mix_id': 'TEMPLATE',
        'R': 0.6,
        'f_FA': 0.5,
        'yCO2': 0.20,
        'w_SS': 0.03,
        'w_b': 1.4,
        'Ca_mol': 1.0,
        'Si_mol': 1.5,
        'Al_mol': 0.4,
        'Fe_mol': 0.1,
        'Mg_mol': 0.05,
        'K_mol': 0.02,
        'Na_mol': 0.08,
        'S_mol': 0.15,
        'O_mol': 5.0,
        'H_mol': 8.0,
        'C_mol': 0.05
    })
    
    # Create writer and generate template
    writer = CemGEMSInputWriter(format=format)
    
    if format == 'json':
        template_data = writer.create_json_input(example_row, 'TEMPLATE')
        with open(output_path, 'w') as f:
            json.dump(template_data, f, indent=2)
    else:
        template_data = writer.create_text_input(example_row, 'TEMPLATE')
        with open(output_path, 'w') as f:
            f.write(template_data)
    
    print(f"✓ Template created: {output_path}")
    return output_path


def main():
    """Main execution: generate all CemGEMS input files."""
    import argparse
    
    parser = argparse.ArgumentParser(
        description='Generate CemGEMS input files from mix designs'
    )
    parser.add_argument(
        '--input', '-i',
        type=str,
        default=None,
        help='Input CSV file with mix designs and compositions'
    )
    parser.add_argument(
        '--output-dir', '-o',
        type=str,
        default=None,
        help='Output directory for input files'
    )
    parser.add_argument(
        '--format', '-f',
        type=str,
        choices=['json', 'text'],
        default='json',
        help='Input file format (default: json)'
    )
    parser.add_argument(
        '--max-files', '-n',
        type=int,
        default=None,
        help='Maximum number of files to generate (for testing)'
    )
    parser.add_argument(
        '--template', '-t',
        action='store_true',
        help='Create template file only (no bulk generation)'
    )
    parser.add_argument(
        '--validate', '-v',
        type=str,
        default=None,
        help='Validate a specific input file'
    )
    
    args = parser.parse_args()
    
    # Template mode
    if args.template:
        print("Creating template input file...")
        template_path = create_input_template(format=args.format)
        print(f"\nTemplate created: {template_path}")
        print(f"Edit this file to customize your CemGEMS input structure.")
        return
    
    # Validation mode
    if args.validate:
        writer = CemGEMSInputWriter(format=args.format)
        is_valid, message = writer.validate_input_file(Path(args.validate))
        if is_valid:
            print(f"✓ VALID: {message}")
            return 0
        else:
            print(f"✗ INVALID: {message}")
            return 1
    
    # Bulk generation mode
    print("="*70)
    print("CemGEMS Input File Generator - Phase 3")
    print("="*70)
    
    # Create writer
    writer = CemGEMSInputWriter(
        output_dir=args.output_dir,
        format=args.format
    )
    
    # Generate all input files
    try:
        output_paths = writer.generate_all_inputs(
            input_csv=args.input,
            max_files=args.max_files,
            verbose=True
        )
        
        # Validate a sample
        if len(output_paths) > 0:
            print("\nValidating sample input file...")
            is_valid, message = writer.validate_input_file(output_paths[0])
            if is_valid:
                print(f"  ✓ {message}")
            else:
                print(f"  ✗ {message}")
        
        print("\n" + "="*70)
        print("Phase 3 Complete: All input files generated successfully!")
        print("="*70)
        print(f"\nNext step (Phase 4): Run batch CemGEMS calculations")
        print(f"  Input files: {writer.output_dir}")
        print(f"  Total files: {len(output_paths)}")
        
        return 0
        
    except Exception as e:
        print(f"\n✗ Error during input generation: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == '__main__':
    exit(main())
