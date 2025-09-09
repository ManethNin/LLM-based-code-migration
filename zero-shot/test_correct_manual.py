#!/usr/bin/env python3
"""
Test pipeline with the correct file and diff for MySQL timeout exception fix.
"""

import logging
from pathlib import Path

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def test_with_correct_manual_diff():
    """Test the pipeline with the correct manually crafted diff."""
    
    try:
        # Import existing functions
        from groq_pipeline_experiment import test_project_with_pipeline, load_dataset_entry
        
        # Use the feedzai/pdb project
        project_hash = "0305beafdecb0b28f7c94264ed20cdc4e41ff067"
        project_path = Path(f"dataset/{project_hash}")
        
        logger.info(f"🧪 Testing pipeline with correct manual diff")
        logger.info(f"📁 Project: {project_hash} (feedzai/pdb)")
        
        # Load the dataset entry to verify it exists
        dataset_entry = load_dataset_entry(project_path)
        logger.info(f"✅ Dataset loaded: {dataset_entry.repo_slug}")
        logger.info(f"   📋 API changes: {len(dataset_entry.api_changes)} chars")
        logger.info(f"   🔧 Dependency: {dataset_entry.version_upgrade_str}")
        
        # Create the correct manual diff for MySqlQueryExceptionHandler.java
        manual_diff = '''```diff
--- a/src/main/java/com/feedzai/commons/sql/abstraction/engine/impl/mysql/MySqlQueryExceptionHandler.java
+++ b/src/main/java/com/feedzai/commons/sql/abstraction/engine/impl/mysql/MySqlQueryExceptionHandler.java
@@ -18,7 +18,7 @@ package com.feedzai.commons.sql.abstraction.engine.impl.mysql;

 import com.feedzai.commons.sql.abstraction.engine.handler.QueryExceptionHandler;

-import com.mysql.jdbc.exceptions.MySQLTimeoutException;
+import java.sql.SQLTimeoutException;

 import java.sql.SQLException;

@@ -36,7 +36,7 @@ public class MySqlQueryExceptionHandler extends QueryExceptionHandler {

     @Override
     public boolean isTimeoutException(final SQLException exception) {
-        return exception instanceof MySQLTimeoutException || super.isTimeoutException(exception);
+        return exception instanceof SQLTimeoutException || super.isTimeoutException(exception);
     }

     @Override
```'''
        
        # Save the manual diff to a temporary file for reference
        manual_diff_file = project_path / "correct_manual_fix.diff"
        manual_diff_file.write_text(manual_diff)
        logger.info(f"✅ Correct manual diff saved to {manual_diff_file}")
        
        # Now we need to modify the groq diff generator temporarily
        import groq_pipeline_experiment
        
        # Store the original function
        original_groq_diff_generator = groq_pipeline_experiment.groq_diff_generator
        
        def correct_manual_diff_generator(diff_params):
            """Replace the LLM generator with our correct manual diff."""
            logger.info("🛠️ Using CORRECT manual diff instead of LLM generation")
            logger.info(f"   📝 Targeting file: MySqlQueryExceptionHandler.java")
            logger.info(f"   🔧 Fix: MySQLTimeoutException -> SQLTimeoutException")
            return [manual_diff]
        
        # Temporarily replace the function
        groq_pipeline_experiment.groq_diff_generator = correct_manual_diff_generator
        
        try:
            # Run the existing pipeline with our correct manual diff
            logger.info("🚀 Running pipeline with CORRECT manual diff...")
            result = test_project_with_pipeline(project_path, "correct-manual-diff-test")
            
            if result:
                logger.info("🎉 COMPLETE SUCCESS! Pipeline works end-to-end with correct diff!")
            else:
                logger.info("⚠️ Pipeline ran but had issues - checking what happened...")
            
            return result
            
        finally:
            # Restore the original function
            groq_pipeline_experiment.groq_diff_generator = original_groq_diff_generator
            # Clean up
            if manual_diff_file.exists():
                manual_diff_file.unlink()
                
    except Exception as e:
        logger.error(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_with_correct_manual_diff()
    logger.info(f"\n🎯 FINAL CONCLUSION:")
    if success:
        logger.info("✅ PROVEN: Pipeline infrastructure works perfectly!")
        logger.info("✅ PROVEN: Correct diffs compile and pass tests!")
        logger.info("🔧 NEXT STEP: Improve LLM prompt to generate correct diffs!")
    else:
        logger.info("🔍 ANALYSIS: Let's check what specific issues remain...")
    
    exit(0 if success else 1)
