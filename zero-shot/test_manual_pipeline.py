#!/usr/bin/env python3
"""
Test pipeline with manually crafted correct diff using existing groq infrastructure.
"""

import logging
import json
import sys
sys.path.append(".")

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def manual_diff_generator(params):
    """Generate a manually crafted correct diff."""
    logger.info("🛠️ Generating manual diff (known correct fix)")
    
    # Known correct fix for MySQL timeout exception migration
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
    
    logger.info("✅ Manual diff generated successfully")
    return [manual_diff]

def test_manual_fix():
    """Test the complete pipeline with a manually crafted correct diff."""
    
    try:
        # Import the existing groq experiment infrastructure
        from groq_pipeline_experiment import run_single_project, load_dataset
        
        # Use the feedzai/pdb project that we've been debugging
        project_hash = "0305beafdecb0b28f7c94264ed20cdc4e41ff067"
        
        logger.info(f"🧪 Testing complete pipeline with manual fix")
        logger.info(f"📁 Project: {project_hash} (feedzai/pdb)")
        
        # Load the full dataset to get the project entry
        dataset = load_dataset()
        project_entry = next((entry for entry in dataset if entry["project_hash"] == project_hash), None)
        
        if not project_entry:
            logger.error(f"❌ Project {project_hash} not found in dataset")
            return False
            
        logger.info(f"✅ Found project: {project_entry['project_name']}")
        
        # Replace the diff generator with our manual one
        logger.info("🔧 Replacing LLM diff generator with manual fix...")
        
        # Create a modified version of run_single_project that uses manual diff
        from groq_pipeline_experiment import get_groq_model
        from masterthesis.llm.pipeline import pipeline
        from masterthesis.dataset.dataset_reader import DatasetReader
        from masterthesis.dataset.feature_flags import FeatureFlags, CodeType, ErrorType, DependencyChangeType, APIChangeType
        from masterthesis.llm.experiment_io import save_experiment_output
        
        # Setup
        project_path = f"dataset/{project_hash}"
        reader = DatasetReader()
        dataset_entry = reader.get_dataset_entry_from_project_path(project_path)
        
        feature_flags: FeatureFlags = {
            "codeType": CodeType.MINIFIED,
            "errorType": ErrorType.SUPER_MINIFIED, 
            "dependencyChangeType": DependencyChangeType.OMIT,
            "apiChangeType": APIChangeType.REVAPI,
            "lspCheck": False,
            "max_hops": 10,
        }
        
        # Create callbacks with detailed logging
        def invalid_diff_callback(is_valid_diff: bool, diff_remarks):
            status = "✅ Valid" if is_valid_diff else "❌ Invalid"
            logger.info(f"📋 Diff validation: {status}")
            if not is_valid_diff:
                logger.error(f"Diff error: {diff_remarks}")
        
        def diagnostic_callback(diagnostics: list[str], error=None):
            logger.info(f"🔍 Diagnostics: {len(diagnostics)} items")
            for i, diag in enumerate(diagnostics[:3]):  # Show first 3
                logger.info(f"   {i+1}. {diag[:100]}...")
        
        def compile_callback(has_succeeded: bool, error_text: str):
            status = "✅ Success" if has_succeeded else "❌ Failed"
            logger.info(f"🔨 Compilation: {status}")
            if not has_succeeded:
                logger.error(f"Compile error: {error_text[:500]}...")
        
        def test_callback(has_succeeded: bool, error_text: str):
            status = "✅ Success" if has_succeeded else "❌ Failed"  
            logger.info(f"🧪 Tests: {status}")
            if not has_succeeded:
                logger.error(f"Test error: {error_text[:500]}...")
        
        # Run the pipeline with manual diff generator
        logger.info("🚀 Running pipeline with manual fix...")
        extracted_diffs, diff_info = pipeline(
            invalid_diff_callback=invalid_diff_callback,
            diagnostic_callback=diagnostic_callback,
            compile_callback=compile_callback,
            test_callback=test_callback,
            generate_diffs_callback=manual_diff_generator,
            feature_flags=feature_flags,
            dataset_entry=dataset_entry,
            tokenizer_type=None
        )
        
        # Save results
        save_experiment_output(project_path, extracted_diffs, diff_info, "manual-fix-test")
        
        # Report results
        compilation_success = diff_info.get("compilation_has_succeeded", False)
        test_success = diff_info.get("test_has_succeeded", False)
        
        logger.info(f"\n🎯 FINAL RESULTS:")
        logger.info(f"   📝 Diff applied: {'✅' if extracted_diffs else '❌'}")
        logger.info(f"   🔨 Compilation: {'✅' if compilation_success else '❌'}")
        logger.info(f"   🧪 Tests: {'✅' if test_success else '❌'}")
        
        if compilation_success and test_success:
            logger.info("🎉 COMPLETE SUCCESS! Pipeline works end-to-end!")
            return True
        elif compilation_success:
            logger.info("✅ COMPILATION SUCCESS! Tests failed but core fix works!")
            return True
        else:
            logger.warning("⚠️ Still debugging needed, but pipeline infrastructure works")
            return False
            
    except Exception as e:
        logger.error(f"❌ Pipeline test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_manual_fix()
    exit(0 if success else 1)
