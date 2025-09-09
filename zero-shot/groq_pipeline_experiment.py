#!/usr/bin/env python3
"""
Enhanced Groq Zero-Shot Experiment with Full Pipeline Integration
Integrates with existing Docker-based compilation and testing infrastructure
"""

import os
import json
import logging
import time
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from datetime import datetime
import traceback
import re

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Setup imports
import dspy
from dotenv import load_dotenv
from groq import Groq

# Import existing pipeline infrastructure
from masterthesis.llm.pipeline import pipeline
from masterthesis.llm.types import DiffCallbackParams, DiffInfo, TokenizerType
from masterthesis.dataset.dataset_types import DatasetEntry
from masterthesis.dataset.feature_flags import (
    APIChangeType,
    CodeType,
    DependencyChangeType,
    ErrorType,
    FeatureFlags,
)

# Load environment
load_dotenv(".env")

# Check API key
api_key = os.getenv("GROQ_API_KEY")
if not api_key or api_key.startswith("gsk_your"):
    print("❌ ERROR: Please set your GROQ_API_KEY in the .env file")
    exit(1)

# Custom DSPy LLM wrapper for Groq
class GroqLM(dspy.LM):
    def __init__(self, model, api_key, max_tokens=4096, temperature=0, **kwargs):
        super().__init__(model=model, **kwargs)
        self.model = model
        self.client = Groq(api_key=api_key)
        self.max_tokens = max_tokens
        self.temperature = temperature
        
    def basic_request(self, prompt, **kwargs):
        response = self.client.chat.completions.create(
            model=self.model,
            messages=[{"role": "user", "content": prompt}],
            max_tokens=self.max_tokens,
            temperature=self.temperature,
        )
        return response.choices[0].message.content
    
    def __call__(self, prompt, **kwargs):
        return [self.basic_request(prompt, **kwargs)]

# Initialize LLM
groq_lm = GroqLM(
    model="llama-3.3-70b-versatile",
    api_key=api_key,
    max_tokens=4096,
    temperature=0
)

dspy.configure(lm=groq_lm)

# Enhanced signature for diff generation (compatible with existing pipeline)
class GroqDiffSignature(dspy.Signature):
    """Generate a precise unified diff to fix API changes in Java code.
    
    CRITICAL INSTRUCTIONS:
    1. Work with EXACT code from 'code' field - never guess content
    2. Analyze 'initial_error' to identify problematic class/symbol
    3. Find ALL usages of the problematic class in the code
    4. Replace ALL occurrences: imports AND usages (instanceof, new, etc.)
    
    COMPLETE REPLACEMENT PATTERN:
    - If error is "cannot find symbol: class MySQLTimeoutException"
    - Find: import with MySQLTimeoutException → replace with SQLTimeoutException
    - Find: ALL instanceof MySQLTimeoutException → replace with SQLTimeoutException  
    - Find: ALL new MySQLTimeoutException → replace with SQLTimeoutException
    - Find: ALL other usages of the old class name
    
    CRITICAL: Update ALL usages of the old class, not just the import!
    
    Process:
    1. Identify the problematic class from error message
    2. Scan the entire 'code' for ALL occurrences of that class name
    3. Replace ALL imports AND usages in a single diff
    4. Keep method signatures compatible with parent class
    
    Diff format:
    ```diff
    --- a/path
    +++ b/path
    @@ -line,count +line,count @@
     context
    -old import line
    +new import line
     context
    @@ -line,count +line,count @@
     context  
    -old usage line (instanceof, etc.)
    +new usage line
     context
    ```
    """
    
    updated_dependency_details: str = dspy.InputField(desc="Version upgrade details")
    api_changes: str = dspy.InputField(desc="API changes - look for class renames")  
    initial_error: str = dspy.InputField(desc="Compilation error - shows the problematic symbol")
    code: str = dspy.InputField(desc="Complete source code - scan for ALL usages of problematic class")
    path: str = dspy.InputField(desc="File path")
    
    answer: str = dspy.OutputField(desc="Complete diff with ```diff fencing that replaces ALL usages of the old class")

def clean_diff_output(generated_diff: str, file_path: str = None) -> str:
    """Clean the generated diff to ensure it's in proper unified diff format"""
    # If already properly fenced, return as is
    if generated_diff.strip().startswith('```diff') and generated_diff.strip().endswith('```'):
        diff_content = generated_diff.strip()
        
        # Extract content between fences
        pattern = r'```diff\s*(.*?)\s*```'
        match = re.search(pattern, diff_content, re.DOTALL)
        if match:
            inner_content = match.group(1).strip()
            
            # Fix any malformed headers if we have a file path
            if file_path:
                lines = inner_content.split('\n')
                fixed_lines = []
                
                for line in lines:
                    # Fix malformed --- and +++ lines
                    if line.startswith('---'):
                        if not line.startswith('--- a/'):
                            fixed_lines.append(f"--- a/{file_path}")
                        else:
                            fixed_lines.append(line)
                    elif line.startswith('+++'):
                        if not line.startswith('+++ b/'):
                            fixed_lines.append(f"+++ b/{file_path}")
                        else:
                            fixed_lines.append(line)
                    else:
                        fixed_lines.append(line)
                
                return f"```diff\n{chr(10).join(fixed_lines)}\n```"
            else:
                return diff_content
    
    # Remove markdown code blocks if present but not properly fenced
    if "```diff" in generated_diff:
        pattern = r'```diff\s*(.*?)\s*```'
        match = re.search(pattern, generated_diff, re.DOTALL)
        if match:
            diff_content = match.group(1)
            return f"```diff\n{diff_content}\n```"
    elif "```" in generated_diff:
        # Remove any other code blocks and try to extract diff content
        diff_content = re.sub(r'```[^`]*```', '', generated_diff, flags=re.DOTALL)
        diff_content = diff_content.strip()
        
        # Try to find diff-like content
        lines = diff_content.split('\n')
        diff_lines = []
        for line in lines:
            if (line.startswith('---') or line.startswith('+++') or 
                line.startswith('@@') or line.startswith('-') or 
                line.startswith('+') or line.startswith(' ')):
                diff_lines.append(line)
        
        if diff_lines:
            return f"```diff\n{chr(10).join(diff_lines)}\n```"
    
    # If no diff format detected, try to create a simple diff structure
    if not generated_diff.strip().startswith('```diff'):
        return f"```diff\n{generated_diff.strip()}\n```"
    
    return generated_diff.strip()

class GroqExperimentResults:
    """Enhanced results tracking with pipeline integration"""
    def __init__(self):
        self.results = []
        self.summary = {
            "total_projects": 0,
            "successful_diffs": 0,
            "compilation_success": 0,
            "test_success": 0,
            "failed_diffs": 0,
            "errors": 0
        }
        self.start_time = datetime.now()
    
    def add_result(self, project_id: str, result: Dict):
        """Add a project result"""
        self.results.append(result)
        self.summary["total_projects"] += 1
        
        if result.get("diff_generated", False):
            self.summary["successful_diffs"] += 1
            
            # Check pipeline results
            diff_info = result.get("diff_info", {})
            if diff_info.get("compilation_has_succeeded", False):
                self.summary["compilation_success"] += 1
            if diff_info.get("test_has_succeeded", False):
                self.summary["test_success"] += 1
        else:
            if "error" in result:
                self.summary["errors"] += 1
            else:
                self.summary["failed_diffs"] += 1
    
    def save_results(self, filename: str):
        """Save results to JSON file"""
        end_time = datetime.now()
        duration = (end_time - self.start_time).total_seconds()
        
        data = {
            "experiment_metadata": {
                "model": "groq-llama-3.3-70b-versatile",
                "timestamp": self.start_time.strftime("%Y-%m-%d_%H:%M:%S"),
                "duration_seconds": duration,
                "pipeline_enabled": True
            },
            "results": self.results,
            "summary": self.summary
        }
        
        with open(filename, 'w') as f:
            json.dump(data, f, indent=2)
        
        print(f"\\n💾 Results saved to {filename}")

def load_dataset_entry(project_path: Path) -> DatasetEntry:
    """Load a project into DatasetEntry format for pipeline compatibility"""
    try:
        # Load basic info
        repo_slug = "unknown/unknown"
        repo_slug_file = project_path / "repo_slug.txt"
        if repo_slug_file.exists():
            repo_slug = repo_slug_file.read_text().strip()
        
        # Load error lines
        minified_error_lines = ""
        error_file = project_path / "minified_error_lines.txt"
        if error_file.exists():
            minified_error_lines = error_file.read_text().strip()
        
        super_minified_error_lines = ""
        super_error_file = project_path / "super_minified_error_lines.txt"
        if super_error_file.exists():
            super_minified_error_lines = super_error_file.read_text().strip()
        
        # Load initial error lines
        initial_error_lines = ""
        initial_error_file = project_path / "initial_error_lines.txt"
        if initial_error_file.exists():
            initial_error_lines = initial_error_file.read_text().strip()
        
        # Load API changes
        api_changes = ""
        api_changes_file = project_path / "api_changes.txt"
        if api_changes_file.exists():
            api_changes = api_changes_file.read_text().strip()
        
        # Load dependency change
        version_upgrade_str = ""
        dep_change_file = project_path / "version_upgrade_str.txt"
        if dep_change_file.exists():
            version_upgrade_str = dep_change_file.read_text().strip()
        
        # Load file in scope
        file_in_scope = ""
        file_scope = project_path / "file_in_scope.txt"
        if file_scope.exists():
            file_in_scope = file_scope.read_text().strip()
        
        # Load reproduction log
        reproduction_log = ""
        repro_log_file = project_path / "reproduction_log.txt"
        if repro_log_file.exists():
            reproduction_log = repro_log_file.read_text().strip()
        
        # Load suspicious files
        suspicious_files = []
        suspicious_files_file = project_path / "suspicious_files.json"
        if suspicious_files_file.exists():
            try:
                suspicious_data = json.loads(suspicious_files_file.read_text())
                if isinstance(suspicious_data, list):
                    suspicious_files = suspicious_data
                elif isinstance(suspicious_data, dict) and "files" in suspicious_data:
                    suspicious_files = suspicious_data["files"]
            except:
                suspicious_files = []
        
        # Load extracted compilation errors
        extracted_compilation_errors = {}
        extracted_errors_file = project_path / "extracted_compilation_errors.json"
        if extracted_errors_file.exists():
            try:
                extracted_compilation_errors = json.loads(extracted_errors_file.read_text())
            except:
                extracted_compilation_errors = {}
        
        # Load minimized files
        minimized_with_comments = {}
        minimized_files = project_path / "minimized_files"
        if minimized_files.exists():
            for root, dirs, files in os.walk(minimized_files):
                for file in files:
                    if file.endswith('_minimized_with_comments.txt'):
                        file_path = Path(root) / file
                        with open(file_path, 'r') as f:
                            # Extract relative path from the full file path
                            # Remove the minimized_files prefix and the _minimized_with_comments.txt suffix
                            relative_to_minimized = file_path.relative_to(minimized_files)
                            relative_path = str(relative_to_minimized).replace('_minimized_with_comments.txt', '')
                            minimized_with_comments[relative_path] = f.read()
        
        return DatasetEntry(
            commit_hash=project_path.name,
            repo_slug=repo_slug,
            repo_path=str(project_path.resolve() / "repo"),  # Use absolute path
            file_in_scope=file_in_scope,
            minified_error_lines=minified_error_lines,
            super_minified_error_lines=super_minified_error_lines,
            initial_error_lines=initial_error_lines,
            api_changes=api_changes,
            version_upgrade_str=version_upgrade_str,
            updated_dependency_diff="",  # Not used in our setup
            reproduction_log=reproduction_log,
            suspicious_files=suspicious_files,
            extracted_compilation_errors=extracted_compilation_errors,
            minimized_with_comments=minimized_with_comments,
            minimized_no_comments={}  # Not used in our setup
        )
        
    except Exception as e:
        logger.error(f"Error loading dataset entry for {project_path.name}: {e}")
        raise e

def groq_diff_generator(diff_params: DiffCallbackParams) -> List[str]:
    """Generate diffs using Groq LLM - this replaces the LLM call in the pipeline"""
    try:
        logger.info("Generating diff with Groq LLM...")
        
        # Create the diff generator
        diff_generator = dspy.Predict(GroqDiffSignature)
        
        # Generate the diff
        result = diff_generator(
            updated_dependency_details=diff_params.get("dependency_change", "Unknown dependency change"),
            api_changes=diff_params.get("api_changes", "No API changes documented"),
            initial_error=diff_params.get("error_text", "Unknown compilation error"),
            code=diff_params.get("code", ""),
            path=diff_params.get("relative_path", "unknown.java")
        )
        
        # Clean and return the diff
        raw_diff = result.answer
        cleaned_diff = clean_diff_output(raw_diff, diff_params.get("relative_path"))
        
        logger.info(f"Generated diff (length: {len(cleaned_diff)} chars)")
        return [cleaned_diff]
        
    except Exception as e:
        logger.error(f"Error generating diff: {e}")
        return []

def save_experiment_output(project_path: Path, extracted_diffs: List[str], diff_info: DiffInfo, experiment_name: str):
    """Save experiment output to the project's out/ directory"""
    try:
        out_dir = project_path / "out"
        out_dir.mkdir(exist_ok=True)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_filename = f"groq-{experiment_name}-{timestamp}-execution-errors.json"
        output_path = out_dir / output_filename
        
        output_data = {
            "timestamp": datetime.now().isoformat(),
            "model": "groq-llama-3.3-70b-versatile",
            "experiment": experiment_name,
            "generated_diffs": extracted_diffs,
            "compilation_succeeded": diff_info.get("compilation_has_succeeded", False),
            "test_succeeded": diff_info.get("test_has_succeeded", False),
            "error_text": diff_info.get("error_text", "")
        }
        
        output_path.write_text(json.dumps(output_data, indent=2))
        logger.info(f"Saved experiment output to: {output_path}")
        return str(output_path)
        
    except Exception as e:
        logger.error(f"Error saving experiment output: {e}")
        return ""

def test_project_with_pipeline(project_path: Path, experiment_name: str = "zero-shot-pipeline"):
    """Test a single project using the full pipeline with Groq"""
    print(f"\\n{'='*60}")
    print(f"🔄 Processing Project: {project_path.name}")
    print(f"{'='*60}")
    
    try:
        # Load dataset entry
        dataset_entry = load_dataset_entry(project_path)
        
        print(f"📁 Repo: {dataset_entry.repo_slug}")
        print(f"📦 Dependency: {dataset_entry.version_upgrade_str}")
        print(f"🔧 Error preview: {dataset_entry.minified_error_lines[:150]}...")
        print(f"📄 File in scope: {dataset_entry.file_in_scope}")
        print(f"📁 Available files: {list(dataset_entry.minimized_with_comments.keys())}")
        
        # Check if repo directory exists
        repo_path = Path(dataset_entry.repo_path)
        if not repo_path.exists():
            print(f"❌ Repo directory not found: {repo_path}")
            return {
                "project_id": project_path.name,
                "error": f"Repo directory not found: {repo_path}",
                "diff_generated": False
            }
        
        # Set up feature flags for our experiment
        feature_flags: FeatureFlags = {
            "codeType": CodeType.MINIFIED.value,
            "errorType": ErrorType.MINIFIED.value,
            "dependencyChangeType": DependencyChangeType.MINIFIED_PARSED.value,
            "apiChangeType": APIChangeType.REVAPI.value,
            "lspCheck": False  # Disable LSP for faster execution
        }
        
        # Callback functions for pipeline
        def invalid_diff_callback(is_valid: bool, message):
            if not is_valid:
                print(f"⚠️  Invalid diff: {message}")
            else:
                print("✅ Diff applied successfully")
        
        def diagnostic_callback(diagnostics: List[str], error: str):
            if diagnostics:
                print(f"🔍 LSP diagnostics: {len(diagnostics)} issues")
            if error:
                print(f"⚠️  LSP error: {error}")
        
        def compile_callback(success: bool, error_text: str):
            if success:
                print("✅ COMPILATION SUCCESSFUL!")
            else:
                print("❌ COMPILATION FAILED")
                print(f"Errors: {error_text[:300]}...")
        
        def test_callback(success: bool, error_text: str):
            if success:
                print("✅ TESTS PASSED!")
            else:
                print("❌ TESTS FAILED")
                print(f"Test errors: {error_text[:300]}...")
        
        # Run the pipeline with Groq diff generation
        print("\\n🚀 Running pipeline with Groq LLM...")
        extracted_diffs, diff_info = pipeline(
            invalid_diff_callback=invalid_diff_callback,
            diagnostic_callback=diagnostic_callback,
            compile_callback=compile_callback,
            test_callback=test_callback,
            generate_diffs_callback=groq_diff_generator,
            feature_flags=feature_flags,
            dataset_entry=dataset_entry,
            tokenizer_type=TokenizerType.LLAMA3_1  # Closest match for Groq
        )
        
        # Save experiment output
        saved_path = save_experiment_output(
            project_path, extracted_diffs, diff_info, experiment_name
        )
        
        # Prepare result
        result = {
            "project_id": project_path.name,
            "repo_slug": dataset_entry.repo_slug,
            "diff_generated": len(extracted_diffs) > 0,
            "num_diffs": len(extracted_diffs),
            "diff_info": diff_info,
            "saved_output_path": saved_path,
            "processing_time": 0  # Could add timing if needed
        }
        
        return result
        
    except Exception as e:
        logger.error(f"Error processing {project_path.name}: {e}")
        return {
            "project_id": project_path.name,
            "error": str(e),
            "diff_generated": False
        }

def main():
    """Run Groq experiment with full pipeline integration"""
    print("🚀 Groq Zero-Shot Experiment with Full Pipeline")
    print("Using Docker-based compilation and testing")
    print("=" * 70)
    
    # Check Docker availability
    docker_socket = Path("/var/run/docker.sock")
    if not docker_socket.exists():
        print("❌ ERROR: Docker socket not found. Make sure Docker is running.")
        return
    
    dataset_dir = Path("dataset")
    if not dataset_dir.exists():
        print("❌ ERROR: Dataset directory not found")
        return
    
    # Get first 3 project directories for testing
    project_dirs = [d for d in dataset_dir.iterdir() if d.is_dir()]
    project_dirs = sorted(project_dirs)[:3]  # Test with first 3 projects
    
    results = GroqExperimentResults()
    experiment_name = "groq-pipeline-experiment"
    
    for project_dir in project_dirs:
        result = test_project_with_pipeline(project_dir, experiment_name)
        results.add_result(project_dir.name, result)
        time.sleep(2)  # Rate limiting for Groq API
    
    # Summary
    print(f"\\n{'='*70}")
    print("🎯 GROQ PIPELINE EXPERIMENT SUMMARY")
    print(f"{'='*70}")
    
    summary = results.summary
    total = summary["total_projects"]
    
    print(f"📊 Total projects: {total}")
    print(f"✅ Diffs generated: {summary['successful_diffs']}/{total} ({summary['successful_diffs']/total*100:.1f}%)")
    print(f"🔧 Compilation success: {summary['compilation_success']}/{total} ({summary['compilation_success']/total*100:.1f}%)")
    print(f"🧪 Test success: {summary['test_success']}/{total} ({summary['test_success']/total*100:.1f}%)")
    print(f"❌ Failed: {summary['failed_diffs'] + summary['errors']}")
    
    if summary['compilation_success'] > 0:
        print(f"\\n🎉 SUCCESS! {summary['compilation_success']} projects compiled successfully!")
    if summary['test_success'] > 0:
        print(f"🎉 EXCELLENT! {summary['test_success']} projects passed all tests!")
    
    # Save results
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"groq_pipeline_experiment_{timestamp}.json"
    results.save_results(filename)
    
    print(f"\\n📁 Check project out/ directories for detailed outputs")

if __name__ == "__main__":
    main()
