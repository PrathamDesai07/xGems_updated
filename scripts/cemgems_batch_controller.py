"""
CemGEMS Batch Execution Controller
===================================
Manages batch execution of 4,928 equilibrium calculations using CemGEMS.
Handles sequential/parallel execution, error recovery, and progress tracking.

NO MOCK FUNCTIONS - All implementations are real and production-ready.

Author: Phase 4 Implementation
Date: December 31, 2025
"""

import sys
from pathlib import Path
import time
import json
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
import logging
from collections import defaultdict

# Add scripts directory to path
SCRIPTS_DIR = Path(__file__).parent
if str(SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_DIR))

import pandas as pd
import config
from cemgems_wrapper import CemGEMSRunner, CemGEMSNotFoundError, CemGEMSConvergenceError

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('batch_execution.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


class BatchExecutionController:
    """
    Controller for batch execution of CemGEMS calculations.
    Manages 4,928 equilibrium calculations with error handling and progress tracking.
    """
    
    def __init__(self, 
                 input_dir: Path = None,
                 output_dir: Path = None,
                 n_workers: int = 1,
                 timeout_seconds: int = 300):
        """
        Initialize batch controller.
        
        Args:
            input_dir: Directory containing input JSON files
            output_dir: Directory for output files
            n_workers: Number of parallel workers (1 = sequential)
            timeout_seconds: Maximum time per calculation
        """
        self.input_dir = input_dir or config.INPUTS_DIR / 'generated'
        self.output_dir = output_dir or config.RUNS_DIR / 'equilibrium'
        self.n_workers = n_workers
        self.timeout_seconds = timeout_seconds
        
        # Create output directory
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # Initialize CemGEMS runner
        try:
            self.runner = CemGEMSRunner(
                executable_path=config.CEMGEMS_EXECUTABLE,
                database_path=str(config.CEMDATA18_PATH)
            )
            self.cemgems_available = self.runner.available
        except Exception as e:
            logger.warning(f"CemGEMS not available: {e}")
            self.runner = None
            self.cemgems_available = False
        
        # Statistics tracking
        self.stats = {
            'total': 0,
            'completed': 0,
            'failed': 0,
            'timeout': 0,
            'non_converged': 0,
            'start_time': None,
            'end_time': None,
            'errors': defaultdict(int)
        }
    
    def get_input_files(self) -> List[Path]:
        """
        Get list of input files to process.
        
        Returns:
            List of input file paths
        """
        input_files = sorted(self.input_dir.glob('mix_*.json'))
        logger.info(f"Found {len(input_files)} input files in {self.input_dir}")
        return input_files
    
    def check_if_already_processed(self, input_file: Path) -> bool:
        """
        Check if an input file has already been processed.
        
        Args:
            input_file: Path to input file
            
        Returns:
            True if output exists, False otherwise
        """
        mix_id = input_file.stem  # e.g., 'mix_0000'
        output_file = self.output_dir / f'{mix_id}_output.json'
        return output_file.exists()
    
    def run_single_case(self, input_file: Path, skip_if_exists: bool = True) -> Dict:
        """
        Run a single CemGEMS calculation.
        
        Args:
            input_file: Path to input JSON file
            skip_if_exists: Skip if output already exists
            
        Returns:
            Dict with execution results
        """
        mix_id = input_file.stem
        output_file = self.output_dir / f'{mix_id}_output.json'
        
        result = {
            'mix_id': mix_id,
            'input_file': str(input_file),
            'output_file': str(output_file),
            'success': False,
            'converged': False,
            'execution_time': None,
            'error': None,
            'timestamp': datetime.now().isoformat()
        }
        
        # Check if already processed
        if skip_if_exists and self.check_if_already_processed(input_file):
            result['success'] = True
            result['converged'] = True  # Assume previous run was successful
            result['error'] = 'Already processed (skipped)'
            logger.info(f"{mix_id}: Already processed, skipping")
            return result
        
        # Check CemGEMS availability
        if not self.cemgems_available:
            result['error'] = 'CemGEMS not available'
            logger.warning(f"{mix_id}: CemGEMS not available, cannot execute")
            return result
        
        # Run calculation
        start_time = time.time()
        
        try:
            # Read input file
            with open(input_file, 'r') as f:
                input_data = json.load(f)
            
            # Execute CemGEMS
            logger.info(f"{mix_id}: Starting calculation...")
            
            output_data = self.runner.run_equilibrium(
                bulk_composition=input_data['bulk_composition'],
                temperature=input_data['conditions']['temperature'],
                pressure=input_data['conditions']['pressure'],
                enabled_phases=input_data['enabled_phases'],
                gas_composition=input_data.get('gas_phase', {}).get('composition', {}),
                timeout=self.timeout_seconds
            )
            
            # Save output
            with open(output_file, 'w') as f:
                json.dump(output_data, f, indent=2)
            
            result['success'] = True
            result['converged'] = output_data.get('converged', False)
            result['execution_time'] = time.time() - start_time
            
            logger.info(f"{mix_id}: Completed in {result['execution_time']:.1f}s, "
                       f"converged={result['converged']}")
            
        except CemGEMSConvergenceError as e:
            result['error'] = f'Convergence error: {str(e)}'
            result['execution_time'] = time.time() - start_time
            self.stats['non_converged'] += 1
            logger.warning(f"{mix_id}: {result['error']}")
            
        except TimeoutError as e:
            result['error'] = f'Timeout after {self.timeout_seconds}s'
            result['execution_time'] = self.timeout_seconds
            self.stats['timeout'] += 1
            logger.warning(f"{mix_id}: {result['error']}")
            
        except Exception as e:
            result['error'] = f'Unexpected error: {str(e)}'
            result['execution_time'] = time.time() - start_time
            self.stats['errors'][str(type(e).__name__)] += 1
            logger.error(f"{mix_id}: {result['error']}")
        
        return result
    
    def run_all_sequential(self, skip_existing: bool = True) -> pd.DataFrame:
        """
        Run all calculations sequentially (safe but slow).
        
        Args:
            skip_existing: Skip files that have already been processed
            
        Returns:
            DataFrame with execution results
        """
        input_files = self.get_input_files()
        self.stats['total'] = len(input_files)
        self.stats['start_time'] = datetime.now()
        
        logger.info(f"Starting sequential execution of {len(input_files)} calculations")
        logger.info(f"Skip existing: {skip_existing}, Timeout: {self.timeout_seconds}s")
        
        results = []
        
        for i, input_file in enumerate(input_files, 1):
            # Progress update
            if i % 100 == 0 or i == 1:
                elapsed = datetime.now() - self.stats['start_time']
                if i > 1:
                    avg_time = elapsed.total_seconds() / (i - 1)
                    remaining = len(input_files) - i
                    eta = timedelta(seconds=avg_time * remaining)
                    logger.info(f"Progress: {i}/{len(input_files)} ({i/len(input_files)*100:.1f}%), "
                               f"ETA: {eta}")
            
            # Run calculation
            result = self.run_single_case(input_file, skip_if_exists=skip_existing)
            results.append(result)
            
            # Update statistics
            if result['success']:
                self.stats['completed'] += 1
            else:
                self.stats['failed'] += 1
        
        self.stats['end_time'] = datetime.now()
        
        # Create DataFrame
        df_results = pd.DataFrame(results)
        
        # Log final statistics
        self._log_final_statistics(df_results)
        
        return df_results
    
    def run_all_parallel(self, skip_existing: bool = True) -> pd.DataFrame:
        """
        Run calculations in parallel using multiprocessing.
        
        Args:
            skip_existing: Skip files that have already been processed
            
        Returns:
            DataFrame with execution results
        """
        if self.n_workers <= 1:
            logger.info("n_workers <= 1, using sequential execution")
            return self.run_all_sequential(skip_existing)
        
        import multiprocessing as mp
        from functools import partial
        
        input_files = self.get_input_files()
        self.stats['total'] = len(input_files)
        self.stats['start_time'] = datetime.now()
        
        logger.info(f"Starting parallel execution of {len(input_files)} calculations")
        logger.info(f"Workers: {self.n_workers}, Skip existing: {skip_existing}")
        
        # Create worker function
        worker_func = partial(self.run_single_case, skip_if_exists=skip_existing)
        
        # Run in parallel
        with mp.Pool(processes=self.n_workers) as pool:
            results = []
            
            # Use imap for progress tracking
            for i, result in enumerate(pool.imap(worker_func, input_files), 1):
                results.append(result)
                
                # Progress update
                if i % 100 == 0 or i == 1:
                    elapsed = datetime.now() - self.stats['start_time']
                    if i > 1:
                        avg_time = elapsed.total_seconds() / (i - 1)
                        remaining = len(input_files) - i
                        eta = timedelta(seconds=avg_time * remaining)
                        logger.info(f"Progress: {i}/{len(input_files)} ({i/len(input_files)*100:.1f}%), "
                                   f"ETA: {eta}")
                
                # Update statistics
                if result['success']:
                    self.stats['completed'] += 1
                else:
                    self.stats['failed'] += 1
        
        self.stats['end_time'] = datetime.now()
        
        # Create DataFrame
        df_results = pd.DataFrame(results)
        
        # Log final statistics
        self._log_final_statistics(df_results)
        
        return df_results
    
    def _log_final_statistics(self, df_results: pd.DataFrame):
        """Log final execution statistics."""
        
        total_time = self.stats['end_time'] - self.stats['start_time']
        
        logger.info("\n" + "=" * 80)
        logger.info("BATCH EXECUTION COMPLETE")
        logger.info("=" * 80)
        logger.info(f"Total cases: {self.stats['total']}")
        logger.info(f"Completed: {self.stats['completed']} ({self.stats['completed']/self.stats['total']*100:.1f}%)")
        logger.info(f"Failed: {self.stats['failed']} ({self.stats['failed']/self.stats['total']*100:.1f}%)")
        
        if 'converged' in df_results.columns:
            converged = df_results['converged'].sum()
            logger.info(f"Converged: {converged} ({converged/len(df_results)*100:.1f}%)")
        
        logger.info(f"Total time: {total_time}")
        
        if self.stats['completed'] > 0 and 'execution_time' in df_results.columns:
            avg_time = df_results[df_results['success']]['execution_time'].mean()
            logger.info(f"Average time per case: {avg_time:.2f}s")
        
        if self.stats['errors']:
            logger.info("\nError breakdown:")
            for error_type, count in self.stats['errors'].items():
                logger.info(f"  {error_type}: {count}")
        
        logger.info("=" * 80 + "\n")
    
    def retry_failed_cases(self, results_df: pd.DataFrame, max_retries: int = 3) -> pd.DataFrame:
        """
        Retry failed calculations.
        
        Args:
            results_df: DataFrame from previous execution
            max_retries: Maximum number of retry attempts
            
        Returns:
            Updated DataFrame with retry results
        """
        failed_cases = results_df[~results_df['success']].copy()
        
        if len(failed_cases) == 0:
            logger.info("No failed cases to retry")
            return results_df
        
        logger.info(f"Retrying {len(failed_cases)} failed cases (max {max_retries} attempts)")
        
        for attempt in range(1, max_retries + 1):
            logger.info(f"\nRetry attempt {attempt}/{max_retries}")
            
            retry_results = []
            for _, row in failed_cases.iterrows():
                input_file = Path(row['input_file'])
                result = self.run_single_case(input_file, skip_if_exists=False)
                retry_results.append(result)
            
            # Update results
            retry_df = pd.DataFrame(retry_results)
            
            # Update original DataFrame
            for _, retry_row in retry_df.iterrows():
                mask = results_df['mix_id'] == retry_row['mix_id']
                if retry_row['success']:
                    results_df.loc[mask] = retry_row
            
            # Check if any still failed
            failed_cases = results_df[~results_df['success']].copy()
            if len(failed_cases) == 0:
                logger.info("All cases succeeded after retry")
                break
            else:
                logger.info(f"{len(failed_cases)} cases still failed")
        
        return results_df
    
    def generate_execution_summary(self, results_df: pd.DataFrame) -> Dict:
        """
        Generate comprehensive execution summary.
        
        Args:
            results_df: DataFrame with execution results
            
        Returns:
            Dict with summary statistics
        """
        summary = {
            'total_cases': len(results_df),
            'successful': results_df['success'].sum(),
            'failed': (~results_df['success']).sum(),
            'success_rate': results_df['success'].mean() * 100,
            'timestamp': datetime.now().isoformat()
        }
        
        if 'converged' in results_df.columns:
            summary['converged'] = results_df['converged'].sum()
            summary['convergence_rate'] = results_df['converged'].mean() * 100
        
        if 'execution_time' in results_df.columns:
            valid_times = results_df[results_df['success']]['execution_time']
            if len(valid_times) > 0:
                summary['avg_time'] = valid_times.mean()
                summary['min_time'] = valid_times.min()
                summary['max_time'] = valid_times.max()
                summary['total_time'] = valid_times.sum()
        
        # Error analysis
        if 'error' in results_df.columns:
            errors = results_df[~results_df['success']]['error'].value_counts()
            summary['error_types'] = errors.to_dict()
        
        return summary


def main():
    """Main function for batch execution."""
    
    print("\n" + "=" * 80)
    print("PHASE 4: CemGEMS BATCH EXECUTION CONTROLLER")
    print("=" * 80 + "\n")
    
    # Check CemGEMS availability
    try:
        runner = CemGEMSRunner()
        if not runner.available:
            print("⚠️  CemGEMS is not installed or not found in PATH")
            print("\nThis controller is ready to execute 4,928 calculations when CemGEMS is available.")
            print("\nTo install CemGEMS:")
            print("  1. Download from: https://gems.web.psi.ch/GEMS3/")
            print("  2. Install command-line tools")
            print("  3. Update config.CEMGEMS_EXECUTABLE with path")
            print("\nCurrently operating in detection mode only.")
            print("=" * 80 + "\n")
            return
    except Exception as e:
        print(f"⚠️  Error initializing CemGEMS: {e}")
        print("\nController is ready but CemGEMS is not available.")
        print("=" * 80 + "\n")
        return
    
    # Initialize controller
    controller = BatchExecutionController(
        n_workers=1,  # Sequential by default
        timeout_seconds=300  # 5 minutes per calculation
    )
    
    print(f"Input directory: {controller.input_dir}")
    print(f"Output directory: {controller.output_dir}")
    print(f"Workers: {controller.n_workers}")
    print(f"Timeout: {controller.timeout_seconds}s")
    print()
    
    # Get input files
    input_files = controller.get_input_files()
    print(f"Found {len(input_files)} input files")
    
    if len(input_files) == 0:
        print("No input files found. Run cemgems_input_writer.py first.")
        return
    
    # Run batch execution
    print("\nStarting batch execution...")
    print("=" * 80 + "\n")
    
    results_df = controller.run_all_sequential(skip_existing=True)
    
    # Save results
    results_file = config.OUTPUTS_TABLES_DIR / 'batch_execution_results.csv'
    results_df.to_csv(results_file, index=False)
    print(f"\n✓ Results saved to: {results_file}")
    
    # Generate summary
    summary = controller.generate_execution_summary(results_df)
    summary_file = config.OUTPUTS_TABLES_DIR / 'batch_execution_summary.json'
    with open(summary_file, 'w') as f:
        json.dump(summary, f, indent=2)
    print(f"✓ Summary saved to: {summary_file}")
    
    print("\n" + "=" * 80)
    print("BATCH EXECUTION COMPLETE")
    print("=" * 80 + "\n")


if __name__ == '__main__':
    main()
