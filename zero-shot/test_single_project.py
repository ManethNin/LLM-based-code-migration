#!/usr/bin/env python3

import logging
from pathlib import Path
from groq_pipeline_experiment import test_project_with_pipeline

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def main():
    """Test a single project to debug diff quality"""
    # Test with one of the failing projects
    project_hash = "067f5d2c81ff87c90755f4ed48f62eb5faa8ecf9"  # pinterest/singer
    project_path = Path(f"dataset/{project_hash}")
    
    if not project_path.exists():
        logger.error(f"Project path {project_path} does not exist")
        return
    
    logger.info(f"🔍 Testing single project: {project_hash}")
    
    # Run the test
    try:
        result = test_project_with_pipeline(project_path, "single-project-test")
        if result:
            logger.info("✅ Single project test completed successfully")
        else:
            logger.warning("⚠️ Single project test had issues")
    except Exception as e:
        logger.error(f"❌ Single project test failed: {e}")

if __name__ == "__main__":
    main()
