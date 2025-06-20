#!/usr/bin/env python3
"""Collect all usage function results for external verification"""

import json
import subprocess
from datetime import datetime
from pathlib import Path

def run_all_usage_functions():
    """Run all usage functions and collect results"""
    
    usage_files = [
        "functional/basic_operations.py",
        "functional/model_routing.py", 
        "validation/json_validation.py",
        "multimodal/image_analysis.py",
        "conversation/persistence.py"
    ]
    
    all_results = {
        "timestamp": datetime.now().isoformat(),
        "results": {}
    }
    
    for usage_file in usage_files:
        print(f"Running {usage_file}...")
        try:
            # Run the usage function
            subprocess.run(["python", f"src/llm_call/usage/{usage_file}"], check=True)
            
            # Find the output file
            output_file = Path(f"{Path(usage_file).stem}_results.json")
            if output_file.exists():
                with open(output_file) as f:
                    all_results["results"][usage_file] = json.load(f)
        except Exception as e:
            all_results["results"][usage_file] = {"error": str(e)}
    
    # Save combined results
    output_name = f"all_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(output_name, "w") as f:
        json.dump(all_results, f, indent=2)
    
    print(f"\nALL RESULTS COLLECTED IN: {output_name}")
    print("NEXT STEP: Send this file to Gemini/Perplexity for verification")

if __name__ == "__main__":
    run_all_usage_functions()