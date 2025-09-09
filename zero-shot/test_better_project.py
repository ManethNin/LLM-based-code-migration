#!/usr/bin/env python3

import logging
from pathlib import Path
from groq_pipeline_experiment import test_project_with_pipeline

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def main():
    """Test with the first project which had compilation success before"""
    # Test with the project that worked better in previous runs
    project_hash = "0305beafdecb0b28f7c94264ed20cdc4e41ff067"  # feedzai/pdb - had diff applied successfully
    project_path = Path(f"dataset/{project_hash}")
    
    if not project_path.exists():
        logger.error(f"Project path {project_path} does not exist")
        return
    
    logger.info(f"🔍 Testing with better project: {project_hash}")
    logger.info(f"📁 This project had 'Diff applied successfully' in previous runs")
    
    # Run the test
    try:
        result = test_project_with_pipeline(project_path, "better-project-test")
        if result:
            logger.info("✅ Better project test completed successfully")
        else:
            logger.warning("⚠️ Better project test had issues")
    except Exception as e:
        logger.error(f"❌ Better project test failed: {e}")

if __name__ == "__main__":
    main()
