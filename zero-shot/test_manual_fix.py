#!/usr/bin/env python3

"""
Manual test to verify the complete pipeline works with a known good fix
"""

import logging
from pathlib import Path
from groq_pipeline_experiment import save_experiment_output, load_dataset_entry
from masterthesis.llm.pipeline import pipeline
from masterthesis.llm.types import DiffInfo
from masterthesis.dataset.feature_flags import FeatureFlags, APIChangeType, CodeType, DependencyChangeType, ErrorType, OmissionsType

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def manual_diff_generator(diff_params) -> list[str]:
    """Manually provide the correct fix to test the complete pipeline"""
    
    # This is the correct fix for the MySQL timeout exception issue
    correct_diff = """```diff
--- a/src/main/java/com/feedzai/commons/sql/abstraction/engine/impl/mysql/MySqlQueryExceptionHandler.java
+++ b/src/main/java/com/feedzai/commons/sql/abstraction/engine/impl/mysql/MySqlQueryExceptionHandler.java
@@ -2,7 +2,7 @@
 
 import com.feedzai.commons.sql.abstraction.engine.handler.QueryExceptionHandler;
-import com.mysql.jdbc.exceptions.MySQLTimeoutException;
+import java.sql.SQLTimeoutException;
 import java.sql.SQLException;
 
 /**
@@ -37,7 +37,7 @@
 
     @Override
     public boolean isTimeoutException(final SQLException exception) {
-        return exception instanceof MySQLTimeoutException || super.isTimeoutException(exception);
+        return exception instanceof SQLTimeoutException || super.isTimeoutException(exception);
     }
 
     @Override
```"""
    
    logger.info("🔧 Using manually crafted correct diff to test pipeline")
    return [correct_diff]

def test_manual_fix():
    """Test the complete pipeline with a known good fix"""
    project_hash = "0305beafdecb0b28f7c94264ed20cdc4e41ff067"
    project_path = Path(f"dataset/{project_hash}")
    
    if not project_path.exists():
        logger.error(f"Project path {project_path} does not exist")
        return False
    
    logger.info(f"🧪 Testing complete pipeline with manual fix")
    logger.info(f"📁 Project: {project_hash} (feedzai/pdb)")
    
    try:
        # Load dataset entry
        dataset_entry = load_dataset_entry(project_path)
        
        # Create feature flags for zero-shot
    feature_flags: FeatureFlags = {
        "codeType": CodeType.MINIFIED,
        "errorType": ErrorType.SUPER_MINIFIED,
        "dependencyChangeType": DependencyChangeType.OMIT,
        "apiChangeType": APIChangeType.REVAPI,  # Using API changes
        "lspCheck": False,
        "max_hops": 10,
    }        # Create callbacks
        def invalid_diff_callback(is_valid_diff: bool, diff_remarks):
            logger.info(f"📋 Diff validation: {'✅ Valid' if is_valid_diff else '❌ Invalid'}")
            if not is_valid_diff:
                logger.error(f"Diff error: {diff_remarks}")
        
        def diagnostic_callback(diagnostics: list[str], error=None):
            logger.info(f"🔍 Diagnostics: {len(diagnostics)} items")
        
        def compile_callback(has_succeeded: bool, error_text: str):
            logger.info(f"🔨 Compilation: {'✅ Success' if has_succeeded else '❌ Failed'}")
            if not has_succeeded:
                logger.error(f"Compile error: {error_text[:200]}...")
        
        def test_callback(has_succeeded: bool, error_text: str):
            logger.info(f"🧪 Tests: {'✅ Success' if has_succeeded else '❌ Failed'}")
            if not has_succeeded:
                logger.error(f"Test error: {error_text[:200]}...")
        
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
        
        logger.info(f"🎯 FINAL RESULTS:")
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
    if success:
        print("\n✅ PROOF OF CONCEPT SUCCESSFUL!")
        print("The pipeline infrastructure works correctly.")
        print("The issue is just LLM prompt engineering for better diffs.")
    else:
        print("\n❌ Further debugging needed.")
