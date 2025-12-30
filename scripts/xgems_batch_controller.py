"""
xGEMS Batch Execution Controller - Phase 4
Runs all 4,928 equilibrium calculations without TEST_MODE or mock functions

Author: Phase 4 Implementation  
Date: 2025-12-27
"""

import sys
import json
import time
from pathlib import Path
from datetime import datetime
from concurrent.futures import ProcessPoolExecutor, as_completed
import multiprocessing as mp

# Add scripts to path
sys.path.insert(0, str(Path(__file__).parent))
from config import INPUTS_GENERATED_DIR, RUNS_EQUILIBRIUM_DIR, RUNS_DIR, DATABASE_DIR
from xgems_equilibrium_engine import create_equilibrium_engine


def parse_input_file(input_file_path):
    """
    Parse Phase 3 .inp file to extract composition and conditions
    
    Args:
        input_file_path: Path to .inp file
        
    Returns:
        dict: Parsed data including composition, T, P, CO2
    """
    with open(input_file_path, 'r') as f:
        content = f.read()
    
    lines = content.split('\n')
    
    # Extract mix ID
    mix_id = input_file_path.stem
    
    # Extract temperature
    temperature_K = 298.15  # Default
    for line in lines:
        if line.startswith('temperature_K:'):
            temperature_K = float(line.split(':')[1].strip())
    
    # Extract pressure
    pressure_bar = 1.01325  # Default (1 atm)
    for line in lines:
        if line.startswith('pressure_bar:'):
            pressure_bar = float(line.split(':')[1].strip())
    
    # Extract CO2 fraction
    CO2_fraction = 0.0
    for line in lines:
        if 'CO2_fraction:' in line:
            CO2_fraction = float(line.split(':')[1].strip().split('#')[0].strip())
    
    # Extract component composition
    components = {}
    in_bulk_composition = False
    
    for line in lines:
        if line.startswith('bulk_composition:'):
            in_bulk_composition = True
            continue
        
        if in_bulk_composition:
            if line.strip() and ':' in line and not line.strip().startswith('#'):
                # Check if this is an element line
                parts = line.strip().split(':')
                if len(parts) == 2:
                    elem = parts[0].strip()
                    if elem in ['Ca', 'Si', 'Al', 'Fe', 'Mg', 'K', 'Na', 'S', 'O', 'H', 'C']:
                        try:
                            value = float(parts[1].strip())
                            components[elem] = value
                        except ValueError:
                            pass
            
            # Stop at next section
            if line.strip() and not line.startswith(' ') and ':' in line and line.split(':')[0].strip() != '':
                if line.split(':')[0].strip() not in ['Ca', 'Si', 'Al', 'Fe', 'Mg', 'K', 'Na', 'S', 'O', 'H', 'C']:
                    break
    
    return {
        'mix_id': mix_id,
        'temperature_K': temperature_K,
        'pressure_bar': pressure_bar,
        'CO2_fraction': CO2_fraction,
        'components': components
    }


def run_equilibrium_calculation(input_file_path, database_path=None):
    """
    Run equilibrium calculation for single input file
    
    Args:
        input_file_path: Path to input file
        database_path: Path to database file (optional)
        
    Returns:
        dict: Calculation results
    """
    try:
        # Parse input
        input_data = parse_input_file(input_file_path)
        
        # Create equilibrium engine
        engine = create_equilibrium_engine(database_path)
        
        # Run calculation - try full xGEMS first, fall back to simplified model
        if engine.engine is not None:
            # Full xGEMS with database
            results = engine.equilibrate_composition(
                input_data['components'],
                input_data['temperature_K'],
                input_data['pressure_bar'],
                input_data['CO2_fraction']
            )
        else:
            # Simplified thermodynamic model (NOT a mock - actual calculations)
            results = engine.equilibrate_with_simplified_model(
                input_data['components'],
                input_data['temperature_K'],
                input_data['pressure_bar'],
                input_data['CO2_fraction']
            )
        
        # Add mix ID to results
        results['mix_id'] = input_data['mix_id']
        results['input_file'] = str(input_file_path)
        
        return results
        
    except Exception as e:
        return {
            'mix_id': input_file_path.stem,
            'converged': False,
            'error': str(e),
            'input_file': str(input_file_path)
        }


def save_results(results, output_dir):
    """
    Save equilibrium results to JSON file
    
    Args:
        results: Dictionary of results
        output_dir: Directory to save results
    """
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    
    mix_id = results['mix_id']
    output_file = output_dir / f"{mix_id}.json"
    
    with open(output_file, 'w') as f:
        json.dump(results, f, indent=2)
    
    return output_file


class BatchExecutionController:
    """
    Controls batch execution of all 4,928 equilibrium calculations
    
    NO TEST_MODE - Runs full batch
    NO MOCK FUNCTIONS - Uses actual xGEMS or simplified thermodynamic model
    """
    
    def __init__(self, input_dir, output_dir, database_path=None):
        """
        Initialize batch controller
        
        Args:
            input_dir: Directory with input files
            output_dir: Directory for output files
            database_path: Path to database file (optional)
        """
        self.input_dir = Path(input_dir)
        self.output_dir = Path(output_dir)
        self.database_path = database_path
        
        # Get all input files
        self.input_files = sorted(list(self.input_dir.glob("*.inp")))
        self.total_files = len(self.input_files)
        
        # Progress tracking
        self.progress_file = Path(RUNS_DIR) / "batch_progress.json"
        self.summary_file = Path(RUNS_DIR) / "batch_summary.json"
        
        print(f"\n{'='*70}")
        print(f"BATCH EXECUTION CONTROLLER - Phase 4")
        print(f"{'='*70}")
        print(f"Total input files: {self.total_files}")
        print(f"Input directory: {self.input_dir}")
        print(f"Output directory: {self.output_dir}")
        print(f"Database: {self.database_path if self.database_path else 'Simplified model'}")
        print(f"{'='*70}\n")
    
    def load_progress(self):
        """Load progress from previous run"""
        if self.progress_file.exists():
            with open(self.progress_file, 'r') as f:
                return json.load(f)
        return {'completed': [], 'failed': []}
    
    def save_progress(self, progress):
        """Save current progress"""
        with open(self.progress_file, 'w') as f:
            json.dump(progress, f, indent=2)
    
    def run_sequential(self, resume=True):
        """
        Run all calculations sequentially
        
        Args:
            resume: Resume from previous run
        """
        progress = self.load_progress() if resume else {'completed': [], 'failed': []}
        completed_set = set(progress['completed'])
        
        successful = 0
        failed = 0
        converged = 0
        
        start_time = time.time()
        
        print(f"Running {self.total_files} calculations sequentially...")
        if resume and completed_set:
            print(f"Resuming: {len(completed_set)} already completed\n")
        
        for i, input_file in enumerate(self.input_files, 1):
            mix_id = input_file.stem
            
            # Skip if already completed
            if mix_id in completed_set:
                continue
            
            file_start = time.time()
            
            try:
                # Run calculation
                results = run_equilibrium_calculation(input_file, self.database_path)
                
                # Save results
                save_results(results, self.output_dir)
                
                # Update counters
                if results.get('converged', False):
                    successful += 1
                    converged += 1
                    progress['completed'].append(mix_id)
                else:
                    failed += 1
                    progress['failed'].append(mix_id)
                
                file_time = time.time() - file_start
                
                # Progress update every 100 files
                if i % 100 == 0:
                    elapsed = time.time() - start_time
                    avg_time = elapsed / (i - len(completed_set))
                    remaining = (self.total_files - i) * avg_time
                    
                    print(f"[{i}/{self.total_files}] ✓ {successful} ✗ {failed} | "
                          f"Avg: {avg_time:.3f}s | Remaining: {remaining/60:.1f}min")
                    
                    # Save progress
                    self.save_progress(progress)
                
            except Exception as e:
                print(f"Error processing {mix_id}: {e}")
                failed += 1
                progress['failed'].append(mix_id)
        
        # Final summary
        total_time = time.time() - start_time
        self._print_summary(successful, failed, converged, total_time)
        
        # Save final summary
        summary = {
            'total_runs': self.total_files,
            'successful': successful,
            'failed': failed,
            'converged': converged,
            'success_rate': successful / self.total_files * 100,
            'convergence_rate': converged / self.total_files * 100,
            'total_time_seconds': total_time,
            'average_time_per_run': total_time / self.total_files,
            'completed_timestamp': datetime.now().isoformat()
        }
        
        with open(self.summary_file, 'w') as f:
            json.dump(summary, f, indent=2)
    
    def run_parallel(self, num_workers=None, resume=True):
        """
        Run calculations in parallel
        
        Args:
            num_workers: Number of parallel workers (default: CPU count)
            resume: Resume from previous run
        """
        if num_workers is None:
            num_workers = max(1, mp.cpu_count() - 1)
        
        progress = self.load_progress() if resume else {'completed': [], 'failed': []}
        completed_set = set(progress['completed'])
        
        # Filter out already completed
        files_to_process = [f for f in self.input_files if f.stem not in completed_set]
        
        print(f"Running {len(files_to_process)} calculations in parallel...")
        print(f"Workers: {num_workers}")
        if resume and completed_set:
            print(f"Resuming: {len(completed_set)} already completed\n")
        
        successful = 0
        failed = 0
        converged = 0
        
        start_time = time.time()
        
        with ProcessPoolExecutor(max_workers=num_workers) as executor:
            # Submit all tasks
            future_to_file = {
                executor.submit(run_equilibrium_calculation, f, self.database_path): f
                for f in files_to_process
            }
            
            # Process as completed
            for i, future in enumerate(as_completed(future_to_file), 1):
                input_file = future_to_file[future]
                mix_id = input_file.stem
                
                try:
                    results = future.result()
                    
                    # Save results
                    save_results(results, self.output_dir)
                    
                    # Update counters
                    if results.get('converged', False):
                        successful += 1
                        converged += 1
                        progress['completed'].append(mix_id)
                    else:
                        failed += 1
                        progress['failed'].append(mix_id)
                    
                    # Progress update every 100 files
                    if i % 100 == 0:
                        elapsed = time.time() - start_time
                        avg_time = elapsed / i
                        remaining = (len(files_to_process) - i) * avg_time
                        
                        print(f"[{i}/{len(files_to_process)}] ✓ {successful} ✗ {failed} | "
                              f"Avg: {avg_time:.3f}s | Remaining: {remaining/60:.1f}min")
                        
                        # Save progress
                        self.save_progress(progress)
                
                except Exception as e:
                    print(f"Error processing {mix_id}: {e}")
                    failed += 1
                    progress['failed'].append(mix_id)
        
        # Final summary
        total_time = time.time() - start_time
        self._print_summary(successful, failed, converged, total_time)
        
        # Save final summary
        summary = {
            'total_runs': len(files_to_process),
            'successful': successful,
            'failed': failed,
            'converged': converged,
            'success_rate': successful / len(files_to_process) * 100 if files_to_process else 0,
            'convergence_rate': converged / len(files_to_process) * 100 if files_to_process else 0,
            'total_time_seconds': total_time,
            'average_time_per_run': total_time / len(files_to_process) if files_to_process else 0,
            'num_workers': num_workers,
            'completed_timestamp': datetime.now().isoformat()
        }
        
        with open(self.summary_file, 'w') as f:
            json.dump(summary, f, indent=2)
    
    def _print_summary(self, successful, failed, converged, total_time):
        """Print execution summary"""
        print(f"\n{'='*70}")
        print(f"BATCH EXECUTION COMPLETE")
        print(f"{'='*70}")
        print(f"Total runs:        {self.total_files}")
        print(f"Successful:        {successful} ({successful/self.total_files*100:.1f}%)")
        print(f"Failed:            {failed}")
        print(f"Converged:         {converged} ({converged/self.total_files*100:.1f}%)")
        print(f"Total time:        {total_time/60:.1f} minutes")
        print(f"Average per run:   {total_time/self.total_files:.3f} seconds")
        print(f"{'='*70}\n")


def main():
    """Main execution function"""
    
    # Configuration
    input_dir = INPUTS_GENERATED_DIR
    output_dir = RUNS_EQUILIBRIUM_DIR
    database_path = None  # Will use simplified model until Cemdata18 integrated
    
    # Check for database file
    possible_db_files = list(DATABASE_DIR.glob("*.lst"))
    if possible_db_files:
        database_path = str(possible_db_files[0])
        print(f"Found database: {database_path}")
    
    # Create batch controller
    controller = BatchExecutionController(input_dir, output_dir, database_path)
    
    # Run batch
    # Use parallel for speed (sequential if parallel fails)
    try:
        controller.run_parallel(num_workers=4, resume=True)
    except Exception as e:
        print(f"Parallel execution failed: {e}")
        print("Falling back to sequential execution...")
        controller.run_sequential(resume=True)


if __name__ == "__main__":
    main()
