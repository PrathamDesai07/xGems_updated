"""
Improved Phase Classification Module
=====================================
Classifies phase assemblages and identifies dominant phases from CemGEMS output.

This version properly handles:
- Column names with 'phase_' prefix and '_mol' suffix
- Dynamic phase detection from actual data
- Multiple classification strategies
- Proper handling of complex assemblages

NO MOCK FUNCTIONS - All real implementations.

Author: Phase 6 Implementation (Improved)
Date: January 1, 2026
"""

import pandas as pd
import numpy as np
from pathlib import Path
from typing import Dict, List, Tuple, Optional
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ImprovedPhaseClassifier:
    """
    Improved classifier for cement hydration/carbonation phase assemblages.
    Works with real Phase 5 output data structure.
    """
    
    # Phase importance hierarchy (higher = more important for classification)
    PHASE_HIERARCHY = {
        'Calcite': 100,           # Carbonation product
        'Portlandite': 90,        # Ca(OH)2 - key hydration product
        'CSH': 85,                # C-S-H gel - main binding phase
        'CSH_TobH': 85,           # Tobermorite-like C-S-H
        'CSH_JenH': 85,           # Jennite-like C-S-H
        'Ettringite': 70,         # AFt phase
        'Monosulfate': 65,        # AFm phase
        'Monocarboaluminate': 68, # Carbonated AFm
        'Hydrotalcite': 60,       # Mg-Al LDH
        'Brucite': 55,            # Mg(OH)2
        'Gypsum': 50,             # CaSO4·2H2O
        'C3S': 40,                # Unreacted clinker
        'C2S': 40,
        'C3A': 40,
        'C4AF': 40,
        'Quartz': 20,             # Inert filler
        'Mullite': 20,
        'Hematite': 20,
        'Magnetite': 20,
    }
    
    # Phase groups for assemblage classification
    PHASE_GROUPS = {
        'Carbonated': ['Calcite', 'Monocarboaluminate', 'Vaterite', 'Aragonite'],
        'Hydrated': ['Portlandite', 'CSH', 'CSH_TobH', 'CSH_JenH', 'Ettringite', 'Monosulfate'],
        'Unreacted': ['C3S', 'C2S', 'C3A', 'C4AF'],
        'Inert': ['Quartz', 'Mullite', 'Hematite', 'Magnetite'],
    }
    
    def __init__(self, min_phase_threshold: float = 0.001):
        """
        Initialize classifier.
        
        Args:
            min_phase_threshold: Minimum mol amount to consider a phase present
        """
        self.min_threshold = min_phase_threshold
        logger.info(f"Initialized ImprovedPhaseClassifier (threshold={min_phase_threshold} mol)")
    
    def get_phase_columns(self, df: pd.DataFrame) -> List[str]:
        """Extract phase column names from DataFrame."""
        phase_cols = [col for col in df.columns 
                     if col.startswith('phase_') and col.endswith('_mol')]
        logger.info(f"Found {len(phase_cols)} phase columns")
        return phase_cols
    
    def clean_phase_name(self, col_name: str) -> str:
        """
        Convert column name to clean phase name.
        
        Example: 'phase_Calcite_mol' -> 'Calcite'
        """
        return col_name.replace('phase_', '').replace('_mol', '')
    
    def get_phase_importance(self, phase_name: str) -> int:
        """Get importance score for a phase."""
        # Exact match
        if phase_name in self.PHASE_HIERARCHY:
            return self.PHASE_HIERARCHY[phase_name]
        
        # Partial match (e.g., CSH_TobH contains CSH)
        for key, value in self.PHASE_HIERARCHY.items():
            if key in phase_name or phase_name in key:
                return value
        
        # Default for unknown phases
        return 30
    
    def classify_dominant_phase(self, row: pd.Series, phase_cols: List[str]) -> str:
        """
        Classify the dominant phase for a single mix.
        
        Strategy:
        1. Find all phases above threshold
        2. Weight by amount × importance
        3. Return most important phase
        """
        if not row.get('converged', False):
            return 'Non-converged'
        
        # Get phase amounts
        phase_amounts = {}
        for col in phase_cols:
            amount = row.get(col, 0.0)
            if pd.notna(amount) and amount >= self.min_threshold:
                phase_name = self.clean_phase_name(col)
                phase_amounts[phase_name] = amount
        
        if not phase_amounts:
            return 'No major phases'
        
        # Find dominant phase by weighted score
        max_score = 0
        dominant = 'Unknown'
        
        for phase, amount in phase_amounts.items():
            importance = self.get_phase_importance(phase)
            score = amount * importance
            
            if score > max_score:
                max_score = score
                dominant = phase
        
        return dominant
    
    def classify_assemblage(self, row: pd.Series, phase_cols: List[str]) -> str:
        """
        Classify the phase assemblage type.
        
        Returns a descriptive string of present phases.
        """
        if not row.get('converged', False):
            return 'Non-converged'
        
        # Get significant phases (sorted by amount)
        significant_phases = []
        for col in phase_cols:
            amount = row.get(col, 0.0)
            if pd.notna(amount) and amount >= self.min_threshold:
                phase_name = self.clean_phase_name(col)
                significant_phases.append((phase_name, amount))
        
        if not significant_phases:
            return 'No major phases'
        
        # Sort by amount (descending)
        significant_phases.sort(key=lambda x: x[1], reverse=True)
        
        # Create assemblage string (top phases)
        top_phases = [f"phase_{name}" for name, _ in significant_phases[:6]]
        return ' + '.join(top_phases)
    
    def classify_by_group(self, row: pd.Series, phase_cols: List[str]) -> str:
        """
        Classify by phase group (Carbonated/Hydrated/Unreacted/Inert).
        """
        if not row.get('converged', False):
            return 'Non-converged'
        
        # Calculate total amount per group
        group_totals = {group: 0.0 for group in self.PHASE_GROUPS}
        
        for col in phase_cols:
            amount = row.get(col, 0.0)
            if pd.notna(amount) and amount >= self.min_threshold:
                phase_name = self.clean_phase_name(col)
                
                # Assign to groups
                for group, phases in self.PHASE_GROUPS.items():
                    if any(p in phase_name for p in phases):
                        group_totals[group] += amount
                        break
        
        # Find dominant group
        total = sum(group_totals.values())
        if total < self.min_threshold:
            return 'Unknown'
        
        max_group = max(group_totals, key=group_totals.get)
        percentage = group_totals[max_group] / total * 100
        
        return f"{max_group} ({percentage:.0f}%)"
    
    def add_classifications(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Add classification columns to DataFrame.
        
        Adds:
        - dominant_phase: Most important phase
        - assemblage: List of significant phases
        - phase_group: Carbonated/Hydrated/etc.
        """
        logger.info("Adding phase classifications...")
        
        df = df.copy()
        phase_cols = self.get_phase_columns(df)
        
        if not phase_cols:
            logger.warning("No phase columns found!")
            return df
        
        # Add classifications
        df['dominant_phase'] = df.apply(
            lambda row: self.classify_dominant_phase(row, phase_cols), axis=1
        )
        
        df['assemblage'] = df.apply(
            lambda row: self.classify_assemblage(row, phase_cols), axis=1
        )
        
        df['phase_group'] = df.apply(
            lambda row: self.classify_by_group(row, phase_cols), axis=1
        )
        
        # Statistics
        converged = df['converged'].sum()
        logger.info(f"✓ Classified {len(df)} mixes ({converged} converged)")
        
        # Phase distribution
        phase_counts = df['dominant_phase'].value_counts()
        logger.info(f"  Dominant phases found: {len(phase_counts)}")
        for phase, count in phase_counts.head(10).items():
            logger.info(f"    {phase}: {count} ({count/len(df)*100:.1f}%)")
        
        return df
    
    def get_classification_summary(self, df: pd.DataFrame) -> Dict:
        """Generate summary statistics of classifications."""
        summary = {
            'total_mixes': len(df),
            'converged': df['converged'].sum() if 'converged' in df.columns else len(df),
            'dominant_phases': df['dominant_phase'].value_counts().to_dict() if 'dominant_phase' in df.columns else {},
            'phase_groups': df['phase_group'].value_counts().to_dict() if 'phase_group' in df.columns else {},
            'unique_assemblages': df['assemblage'].nunique() if 'assemblage' in df.columns else 0,
        }
        
        return summary


def main():
    """Test the improved classifier."""
    
    print("\n" + "=" * 80)
    print("IMPROVED PHASE CLASSIFIER TEST")
    print("=" * 80)
    
    # Load Phase 5 demo data
    demo_file = Path(__file__).parent.parent / 'outputs' / 'phase5_demo' / 'aggregated_results' / 'phase5_demo.csv'
    
    if not demo_file.exists():
        print(f"✗ Demo file not found: {demo_file}")
        return False
    
    df = pd.read_csv(demo_file)
    print(f"✓ Loaded {len(df)} mixes")
    print(f"  Columns: {len(df.columns)}")
    
    # Classify
    classifier = ImprovedPhaseClassifier(min_phase_threshold=0.005)
    df_classified = classifier.add_classifications(df)
    
    # Display results
    print("\n" + "=" * 80)
    print("CLASSIFICATION RESULTS")
    print("=" * 80)
    
    print("\nDominant Phases:")
    for phase, count in df_classified['dominant_phase'].value_counts().head(10).items():
        print(f"  {phase}: {count}")
    
    print("\nPhase Groups:")
    for group, count in df_classified['phase_group'].value_counts().items():
        print(f"  {group}: {count}")
    
    # Summary
    summary = classifier.get_classification_summary(df_classified)
    print("\n" + "=" * 80)
    print("SUMMARY")
    print("=" * 80)
    print(f"Total mixes: {summary['total_mixes']}")
    print(f"Converged: {summary['converged']}")
    print(f"Unique assemblages: {summary['unique_assemblages']}")
    
    # Save
    output_file = demo_file.parent / 'phase5_demo_classified.csv'
    df_classified.to_csv(output_file, index=False)
    print(f"\n✓ Saved classified data: {output_file.name}")
    
    return True


if __name__ == '__main__':
    import sys
    success = main()
    sys.exit(0 if success else 1)
