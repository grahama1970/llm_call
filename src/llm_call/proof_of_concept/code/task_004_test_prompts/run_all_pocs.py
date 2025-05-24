#!/usr/bin/env python3
"""
Run all POCs from Task 004 to verify complete functionality.

This script executes all 29 POCs and aggregates results to ensure
the complete validation framework is operational.
"""

import asyncio
import subprocess
import sys
from pathlib import Path
from typing import Dict, List, Tuple
from datetime import datetime
from loguru import logger

# Configure logger
logger.add("poc_verification.log", rotation="10 MB")


class POCVerifier:
    """Verify all POCs execute successfully."""
    
    def __init__(self):
        self.poc_dir = Path(__file__).parent
        self.results: Dict[str, Tuple[bool, str]] = {}
        
    def get_all_pocs(self) -> List[Path]:
        """Get all POC files in order."""
        pocs = []
        
        # Task 1: POCs 1-5
        for i in range(1, 6):
            poc = self.poc_dir / f"poc_{i:02d}_*.py"
            pocs.extend(self.poc_dir.glob(str(poc.name)))
            
        # Task 2: POCs 6-10
        for i in range(6, 11):
            poc = self.poc_dir / f"poc_{i:02d}_*.py"
            pocs.extend(self.poc_dir.glob(str(poc.name)))
            
        # Task 3: POCs 11-13
        for i in range(11, 14):
            poc = self.poc_dir / f"poc_{i:02d}_*.py"
            pocs.extend(self.poc_dir.glob(str(poc.name)))
            
        # Task 4: POCs 14-16
        for i in range(14, 17):
            poc = self.poc_dir / f"poc_{i:02d}_*.py"
            pocs.extend(self.poc_dir.glob(str(poc.name)))
            
        # Task 5: POCs 17-19
        for i in range(17, 20):
            poc = self.poc_dir / f"poc_{i:02d}_*.py"
            pocs.extend(self.poc_dir.glob(str(poc.name)))
            
        # Task 6: POCs 26-30
        for i in range(26, 31):
            poc = self.poc_dir / f"poc_{i:02d}_*.py"
            pocs.extend(self.poc_dir.glob(str(poc.name)))
            
        # Task 7: POCs 31-35
        for i in range(31, 36):
            poc = self.poc_dir / f"poc_{i:02d}_*.py"
            pocs.extend(self.poc_dir.glob(str(poc.name)))
            
        # Sort by number
        return sorted(set(pocs), key=lambda p: int(p.stem.split('_')[1]))
    
    async def run_poc(self, poc_path: Path) -> Tuple[bool, str]:
        """Run a single POC and capture results."""
        logger.info(f"Running {poc_path.name}...")
        
        try:
            # Run POC as subprocess
            result = subprocess.run(
                [sys.executable, str(poc_path)],
                capture_output=True,
                text=True,
                timeout=30
            )
            
            # Check for success
            if result.returncode == 0:
                # Look for validation passed in output or stderr (loguru outputs to stderr)
                output = result.stdout + result.stderr
                success_patterns = [
                    "VALIDATION PASSED",
                    "ALL TESTS PASSED",
                    "Test runner framework working correctly",
                    "Result aggregation working correctly",
                    "Performance tracking working correctly",
                    "Failure reporting working correctly",
                    "Parallel test execution working correctly",
                    "ALL PERFORMANCE BENCHMARKS COMPLETED SUCCESSFULLY",
                    "Debug mode testing complete"
                ]
                
                if any(pattern in output for pattern in success_patterns):
                    return True, "✅ Passed"
                else:
                    # Show last bit of output for debugging
                    last_output = output[-200:] if output else "No output"
                    return False, f"❌ No validation confirmation\n{last_output}"
            else:
                error_output = result.stderr[-200:] if result.stderr else "No error output"
                return False, f"❌ Exit code {result.returncode}\n{error_output}"
                
        except subprocess.TimeoutExpired:
            return False, "❌ Timeout (>30s)"
        except Exception as e:
            return False, f"❌ Error: {str(e)}"
    
    async def run_all(self):
        """Run all POCs and collect results."""
        pocs = self.get_all_pocs()
        logger.info(f"Found {len(pocs)} POCs to verify")
        
        # Run each POC
        for poc in pocs:
            success, message = await self.run_poc(poc)
            self.results[poc.name] = (success, message)
            
        # Generate report
        self.generate_report()
    
    def generate_report(self):
        """Generate verification report."""
        print("\n" + "="*80)
        print("Task 004: Complete POC Verification Report")
        print("="*80)
        print(f"Generated: {datetime.now().isoformat()}")
        print(f"Total POCs: {len(self.results)}")
        
        # Group by task
        tasks = {
            "Task 1 (Routing)": range(1, 6),
            "Task 2 (JSON)": range(6, 11),
            "Task 3 (Multimodal)": range(11, 14),
            "Task 4 (Agent)": range(14, 17),
            "Task 5 (String)": range(17, 20),
            "Task 6 (Retry)": range(26, 31),
            "Task 7 (Integration)": range(31, 36),
        }
        
        total_passed = 0
        total_failed = 0
        
        for task_name, poc_range in tasks.items():
            print(f"\n## {task_name}")
            task_passed = 0
            task_failed = 0
            
            for poc_num in poc_range:
                # Find POC with this number
                for poc_name, (success, message) in self.results.items():
                    if f"poc_{poc_num:02d}_" in poc_name:
                        if success:
                            task_passed += 1
                            total_passed += 1
                        else:
                            task_failed += 1
                            total_failed += 1
                        print(f"  {poc_name}: {message}")
                        break
            
            print(f"  Task Summary: {task_passed} passed, {task_failed} failed")
        
        # Overall summary
        print(f"\n{'='*80}")
        print("OVERALL SUMMARY")
        print(f"{'='*80}")
        print(f"✅ Passed: {total_passed}")
        print(f"❌ Failed: {total_failed}")
        print(f"📊 Success Rate: {total_passed / len(self.results) * 100:.1f}%")
        
        if total_failed == 0:
            print("\n🎉 ALL POCS VALIDATED SUCCESSFULLY!")
            print("Ready for core module integration.")
        else:
            print(f"\n⚠️  {total_failed} POCs need attention before integration.")
            print("Review failed POCs and fix issues.")


async def main():
    """Main verification entry point."""
    verifier = POCVerifier()
    await verifier.run_all()


if __name__ == "__main__":
    asyncio.run(main())