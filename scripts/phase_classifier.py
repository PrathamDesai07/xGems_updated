#!/usr/bin/env python3
"""
Phase Classifier - Phase 6
Implements multiple classification schemes to identify dominant phases and assemblages
Used for creating phase diagrams and understanding phase stability regions
NO mock functions - all real data classification from equilibrium calculations
"""

import pandas as pd
import numpy as np
from pathlib import Path
from typing import Dict, List, Tuple, Optional


class PhaseClassifier:
    """
    Classifier for identifying dominant phases and phase assemblages
    Implements multiple classification schemes for different visualization needs
    """
    
    def __init__(self, master_dataset_path: str = "outputs/tables/master_dataset.csv"):
        """
        Initialize phase classifier
        
        Args:
            master_dataset_path: Path to master dataset CSV
        """
        self.dataset_path = Path(master_dataset_path)
        if not self.dataset_path.exists():
            raise FileNotFoundError(f"Dataset not found: {master_dataset_path}")
        
        # Load master dataset
        self.df = pd.read_csv(self.dataset_path)
        print(f"Loaded dataset: {len(self.df)} rows")
        
        # Identify phase columns
        self.phase_mol_cols = [col for col in self.df.columns if '_mol' in col and col != 'mix_id']
        self.phase_kg_cols = [col for col in self.df.columns if '_kg' in col]
        
        # Extract phase names (remove _mol or _kg suffix)
        self.phase_names = [col.replace('_mol', '') for col in self.phase_mol_cols]
        
        print(f"Identified {len(self.phase_names)} phases: {', '.join(self.phase_names)}")
    
    def classify_by_max_mass(self) -> pd.Series:
        """
        Classification Method 1: Dominant phase by maximum solid mass
        
        Returns:
            Series with dominant phase name for each case
        """
        print("\nClassifying by maximum solid mass...")
        
        dominant_phases = []
        
        for idx, row in self.df.iterrows():
            # Get mass of each phase
            phase_masses = {}
            for phase_name in self.phase_names:
                mass_col = f'{phase_name}_kg'
                if mass_col in row:
                    phase_masses[phase_name] = row[mass_col]
            
            # Find phase with maximum mass
            if phase_masses:
                dominant_phase = max(phase_masses.items(), key=lambda x: x[1])[0]
            else:
                dominant_phase = 'Unknown'
            
            dominant_phases.append(dominant_phase)
        
        return pd.Series(dominant_phases, name='dominant_phase_by_mass')
    
    def classify_by_max_mole_fraction(self) -> pd.Series:
        """
        Classification Method 2: Dominant phase by maximum mole fraction
        
        Returns:
            Series with dominant phase name for each case
        """
        print("\nClassifying by maximum mole fraction...")
        
        dominant_phases = []
        
        for idx, row in self.df.iterrows():
            # Get moles of each phase
            phase_moles = {}
            for phase_name in self.phase_names:
                mol_col = f'{phase_name}_mol'
                if mol_col in row:
                    phase_moles[phase_name] = row[mol_col]
            
            # Find phase with maximum moles
            if phase_moles:
                dominant_phase = max(phase_moles.items(), key=lambda x: x[1])[0]
            else:
                dominant_phase = 'Unknown'
            
            dominant_phases.append(dominant_phase)
        
        return pd.Series(dominant_phases, name='dominant_phase_by_mole')
    
    def classify_by_assemblage(self, threshold: float = 0.01) -> pd.Series:
        """
        Classification Method 3: Phase assemblage classification
        Groups cases by which phases are present above threshold
        
        Args:
            threshold: Minimum mole amount to consider phase present
            
        Returns:
            Series with phase assemblage label for each case
        """
        print(f"\nClassifying by phase assemblage (threshold={threshold} mol)...")
        
        assemblages = []
        
        for idx, row in self.df.iterrows():
            # Get phases present above threshold
            present_phases = []
            for phase_name in self.phase_names:
                mol_col = f'{phase_name}_mol'
                if mol_col in row and row[mol_col] > threshold:
                    present_phases.append(phase_name)
            
            # Sort alphabetically for consistency
            present_phases.sort()
            
            # Create assemblage label
            if present_phases:
                assemblage = ' + '.join(present_phases)
            else:
                assemblage = 'No major phases'
            
            assemblages.append(assemblage)
        
        return pd.Series(assemblages, name='phase_assemblage')
    
    def classify_by_carbonation_state(self) -> pd.Series:
        """
        Classification Method 4: Carbonation state
        Based on presence and amount of calcite
        
        Returns:
            Series with carbonation state label
        """
        print("\nClassifying by carbonation state...")
        
        carbonation_states = []
        
        for idx, row in self.df.iterrows():
            calcite_mol = row.get('Calcite_mol', 0.0)
            
            if calcite_mol == 0.0:
                state = 'Uncarbonated'
            elif calcite_mol < 0.005:
                state = 'Low carbonation'
            elif calcite_mol < 0.015:
                state = 'Medium carbonation'
            elif calcite_mol < 0.025:
                state = 'High carbonation'
            else:
                state = 'Very high carbonation'
            
            carbonation_states.append(state)
        
        return pd.Series(carbonation_states, name='carbonation_state')
    
    def classify_by_csh_silica_ratio(self) -> pd.Series:
        """
        Classification Method 5: C-S-H vs Silica dominance
        Categorizes based on relative amounts of C-S-H and silica gel
        
        Returns:
            Series with C-S-H/Silica classification
        """
        print("\nClassifying by C-S-H vs Silica ratio...")
        
        classifications = []
        
        for idx, row in self.df.iterrows():
            csh_mol = row.get('C-S-H_1.0_mol', 0.0)
            silica_mol = row.get('Silica_gel_mol', 0.0)
            
            total = csh_mol + silica_mol
            if total > 0:
                csh_fraction = csh_mol / total
                
                if csh_fraction > 0.7:
                    classification = 'C-S-H dominant'
                elif csh_fraction > 0.4:
                    classification = 'C-S-H + Silica'
                elif csh_fraction > 0.1:
                    classification = 'Silica dominant'
                else:
                    classification = 'High silica'
            else:
                classification = 'Unknown'
            
            classifications.append(classification)
        
        return pd.Series(classifications, name='csh_silica_class')
    
    def classify_by_ph_regime(self) -> pd.Series:
        """
        Classification Method 6: pH regime
        Categorizes based on pH ranges relevant to cement chemistry
        
        Returns:
            Series with pH regime label
        """
        print("\nClassifying by pH regime...")
        
        ph_regimes = []
        
        for idx, row in self.df.iterrows():
            pH = row.get('pH', np.nan)
            
            if pH < 8.5:
                regime = 'Neutral (pH<8.5)'
            elif pH < 9.0:
                regime = 'Slightly alkaline (8.5-9.0)'
            elif pH < 9.5:
                regime = 'Moderately alkaline (9.0-9.5)'
            elif pH < 10.0:
                regime = 'Alkaline (9.5-10.0)'
            else:
                regime = 'Highly alkaline (pH>10.0)'
            
            ph_regimes.append(regime)
        
        return pd.Series(ph_regimes, name='pH_regime')
    
    def classify_for_phase_diagram(self) -> pd.Series:
        """
        Classification Method 7: Simplified classification for phase diagrams
        Uses combination of dominant phase and carbonation state
        
        Returns:
            Series with simplified phase diagram label
        """
        print("\nClassifying for phase diagrams...")
        
        diagram_classes = []
        
        for idx, row in self.df.iterrows():
            calcite_mol = row.get('Calcite_mol', 0.0)
            csh_mol = row.get('C-S-H_1.0_mol', 0.0)
            silica_mol = row.get('Silica_gel_mol', 0.0)
            ettringite_mol = row.get('Ettringite_mol', 0.0)
            
            # Simplified classification for clear phase diagrams
            if calcite_mol > 0.02:
                label = 'Calcite-rich'
            elif calcite_mol > 0.01:
                label = 'Calcite + C-S-H'
            elif csh_mol > silica_mol * 0.5:
                label = 'C-S-H dominant'
            elif ettringite_mol > 0.015:
                label = 'C-S-H + AFt'
            else:
                label = 'Silica-rich'
            
            diagram_classes.append(label)
        
        return pd.Series(diagram_classes, name='phase_diagram_class')
    
    def calculate_phase_statistics(self) -> pd.DataFrame:
        """
        Calculate statistics for each phase across all cases
        
        Returns:
            DataFrame with phase statistics
        """
        print("\nCalculating phase statistics...")
        
        stats = []
        
        for phase_name in self.phase_names:
            mol_col = f'{phase_name}_mol'
            kg_col = f'{phase_name}_kg'
            
            if mol_col in self.df.columns:
                phase_mols = self.df[mol_col]
                phase_mass = self.df[kg_col] if kg_col in self.df.columns else None
                
                # Calculate presence
                present_count = (phase_mols > 0).sum()
                present_pct = present_count / len(self.df) * 100
                
                # Calculate statistics for cases where phase is present
                if present_count > 0:
                    present_data = phase_mols[phase_mols > 0]
                    
                    stat = {
                        'phase': phase_name,
                        'present_count': present_count,
                        'present_percentage': present_pct,
                        'mean_mol': present_data.mean(),
                        'std_mol': present_data.std(),
                        'min_mol': present_data.min(),
                        'max_mol': present_data.max(),
                        'median_mol': present_data.median()
                    }
                    
                    if phase_mass is not None:
                        present_mass = phase_mass[phase_mols > 0]
                        stat['mean_kg'] = present_mass.mean()
                        stat['std_kg'] = present_mass.std()
                else:
                    stat = {
                        'phase': phase_name,
                        'present_count': 0,
                        'present_percentage': 0.0,
                        'mean_mol': 0.0,
                        'std_mol': 0.0,
                        'min_mol': 0.0,
                        'max_mol': 0.0,
                        'median_mol': 0.0,
                        'mean_kg': 0.0,
                        'std_kg': 0.0
                    }
                
                stats.append(stat)
        
        return pd.DataFrame(stats)
    
    def apply_all_classifications(self) -> pd.DataFrame:
        """
        Apply all classification methods and add to dataset
        
        Returns:
            DataFrame with all original columns plus classification columns
        """
        print("\n" + "="*70)
        print("APPLYING ALL CLASSIFICATION METHODS")
        print("="*70)
        
        result_df = self.df.copy()
        
        # Apply each classification method
        result_df['dominant_phase_by_mass'] = self.classify_by_max_mass()
        result_df['dominant_phase_by_mole'] = self.classify_by_max_mole_fraction()
        result_df['phase_assemblage'] = self.classify_by_assemblage(threshold=0.01)
        result_df['carbonation_state'] = self.classify_by_carbonation_state()
        result_df['csh_silica_class'] = self.classify_by_csh_silica_ratio()
        result_df['pH_regime'] = self.classify_by_ph_regime()
        result_df['phase_diagram_class'] = self.classify_for_phase_diagram()
        
        print(f"\nAdded 7 classification columns to dataset")
        print(f"Total columns: {len(result_df.columns)}")
        
        return result_df
    
    def print_classification_summary(self, classified_df: pd.DataFrame):
        """
        Print summary statistics for all classifications
        
        Args:
            classified_df: DataFrame with classification columns
        """
        print("\n" + "="*70)
        print("CLASSIFICATION SUMMARY")
        print("="*70)
        
        classification_cols = [
            'dominant_phase_by_mass',
            'dominant_phase_by_mole',
            'phase_assemblage',
            'carbonation_state',
            'csh_silica_class',
            'pH_regime',
            'phase_diagram_class'
        ]
        
        for col in classification_cols:
            if col in classified_df.columns:
                print(f"\n{col}:")
                value_counts = classified_df[col].value_counts()
                for label, count in value_counts.items():
                    pct = count / len(classified_df) * 100
                    print(f"  {label:.<50} {count:>5} ({pct:>5.1f}%)")
    
    def export_classified_dataset(self, classified_df: pd.DataFrame, 
                                  output_path: str = "outputs/tables/master_dataset_classified.csv"):
        """
        Export classified dataset to CSV
        
        Args:
            classified_df: DataFrame with classifications
            output_path: Output file path
        """
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        classified_df.to_csv(output_path, index=False)
        
        print(f"\n" + "="*70)
        print(f"EXPORTED CLASSIFIED DATASET")
        print(f"="*70)
        print(f"Path: {output_path}")
        print(f"Rows: {len(classified_df)}")
        print(f"Columns: {len(classified_df.columns)}")


def main():
    """Main execution for phase classification"""
    
    # Initialize classifier
    classifier = PhaseClassifier(master_dataset_path="outputs/tables/master_dataset.csv")
    
    # Calculate and display phase statistics
    phase_stats = classifier.calculate_phase_statistics()
    print("\n" + "="*70)
    print("PHASE STATISTICS")
    print("="*70)
    print(phase_stats.to_string(index=False))
    
    # Apply all classifications
    classified_df = classifier.apply_all_classifications()
    
    # Print classification summary
    classifier.print_classification_summary(classified_df)
    
    # Export classified dataset
    classifier.export_classified_dataset(
        classified_df, 
        output_path="outputs/tables/master_dataset_classified.csv"
    )
    
    # Export phase statistics
    phase_stats.to_csv("outputs/tables/phase_statistics.csv", index=False)
    print(f"\nExported phase statistics to: outputs/tables/phase_statistics.csv")
    
    print("\n" + "="*70)
    print("PHASE 6 CLASSIFICATION - COMPLETE")
    print("="*70)


if __name__ == "__main__":
    main()
