#!/usr/bin/env python3
"""
Run the full 65-project experiment with background processing
"""

import subprocess
import sys
from pathlib import Path

def run_full_experiment():
    """Run the full experiment in background with logging"""
    
    print("🚀 Starting Full Zero-Shot Experiment with Verification")
    print("This will process all 65 projects...")
    print()
    
    # Run the improved experiment
    cmd = ["pdm", "run", "python", "improved_experiment.py"]
    
    try:
        # For full experiment, modify the script to process all projects
        result = subprocess.run(cmd, check=True, capture_output=True, text=True)
        print("✅ Experiment completed successfully!")
        print(result.stdout)
        
    except subprocess.CalledProcessError as e:
        print(f"❌ Experiment failed: {e}")
        print(f"Output: {e.stdout}")
        print(f"Error: {e.stderr}")
    except KeyboardInterrupt:
        print("⚠️ Experiment interrupted by user")
    
    print("\n📊 Check the results JSON file for detailed analysis")

if __name__ == "__main__":
    run_full_experiment()
