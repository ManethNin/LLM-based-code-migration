#!/usr/bin/env python3
"""
Simple test to validate pipeline infrastructure with a known correct diff.
This modifies the existing groq pipeline to use a manual diff instead of LLM generation.
"""

import logging
from pathlib import Path

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def test_with_manual_diff():
    """Test the pipeline with a manually crafted correct diff."""
    
    try:
        # Import existing functions
        from groq_pipeline_experiment import test_project_with_pipeline, load_dataset_entry
        
        # Use the feedzai/pdb project
        project_hash = "0305beafdecb0b28f7c94264ed20cdc4e41ff067"
        project_path = Path(f"dataset/{project_hash}")
        
        logger.info(f"🧪 Testing pipeline with manual diff")
        logger.info(f"📁 Project: {project_hash} (feedzai/pdb)")
        
        # Load the dataset entry to verify it exists
        dataset_entry = load_dataset_entry(project_path)
        logger.info(f"✅ Dataset loaded: {dataset_entry.repo_slug}")
        logger.info(f"   📋 API changes: {len(dataset_entry.api_changes)} chars")
        logger.info(f"   🔧 Dependency: {dataset_entry.version_upgrade_str}")
        
        # Create manual diff as a string that will be returned by a mock generator
        manual_diff = '''--- a/src/main/java/com/feedzai/commons/sql/abstraction/engine/impl/mysql/MySQLEngine.java
+++ b/src/main/java/com/feedzai/commons/sql/abstraction/engine/impl/mysql/MySQLEngine.java
@@ -56,7 +56,7 @@ import com.feedzai.commons.sql.abstraction.util.PreparedStatementCapsule;
 import com.feedzai.commons.sql.abstraction.util.StringUtils;
 import com.mysql.cj.exceptions.CJTimeoutException;
 import com.mysql.cj.exceptions.MySQLTimeoutException;
-import com.mysql.cj.exceptions.MySQLTimeoutException;
+import java.sql.SQLTimeoutException;
 import com.mysql.cj.jdbc.exceptions.MySQLTransactionRollbackException;
 import org.slf4j.Logger;
 import org.slf4j.LoggerFactory;
@@ -308,7 +308,7 @@ public class MySQLEngine extends AbstractDatabaseEngine {
                 return DatabaseEngineRuntimeException.fromCause(de.getCause(), de.getMessage());
             }
 
-            if (de.getCause() instanceof MySQLTimeoutException) {
+            if (de.getCause() instanceof SQLTimeoutException) {
                 return new DatabaseEngineTimeoutException(de.getMessage(), de.getCause());
             }
 
'''
        
        # Save the manual diff to a temporary file for the pipeline to use
        manual_diff_file = project_path / "manual_fix.diff"
        manual_diff_file.write_text(manual_diff)
        logger.info(f"✅ Manual diff saved to {manual_diff_file}")
        
        # Now we need to modify the groq diff generator temporarily
        # This is a quick hack to test the infrastructure
        import groq_pipeline_experiment
        
        # Store the original function
        original_groq_diff_generator = groq_pipeline_experiment.groq_diff_generator
        
        def manual_diff_generator(diff_params):
            """Replace the LLM generator with our manual diff."""
            logger.info("🛠️ Using manual diff instead of LLM generation")
            return [manual_diff]
        
        # Temporarily replace the function
        groq_pipeline_experiment.groq_diff_generator = manual_diff_generator
        
        try:
            # Run the existing pipeline with our manual diff
            logger.info("🚀 Running existing pipeline with manual diff...")
            result = test_project_with_pipeline(project_path, "manual-diff-test")
            
            if result:
                logger.info("🎉 SUCCESS! Pipeline infrastructure works with correct diff!")
            else:
                logger.info("⚠️ Pipeline ran but had issues - this is normal for debugging")
            
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
    success = test_with_manual_diff()
    logger.info(f"\n🎯 CONCLUSION:")
    if success:
        logger.info("✅ Pipeline infrastructure is working correctly!")
        logger.info("🔧 The issue is just LLM prompt engineering for better diffs.")
    else:
        logger.info("⚠️ Pipeline had issues, but this helps isolate the problem.")
    
    exit(0 if success else 1)
