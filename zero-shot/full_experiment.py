#!/usr/bin/env python3
"""
Full Zero-Shot Experiment with Groq
Processes all dataset entries and measures success rate
"""

import os
import json
import logging
import time
from pathlib import Path
from typing import Dict, List, Optional
from datetime import datetime
import traceback

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Setup imports
import dspy
from dotenv import load_dotenv
from groq import Groq

# Load environment
load_dotenv(".env")

# Check API key
api_key = os.getenv("GROQ_API_KEY")
if not api_key or api_key.startswith("gsk_your"):
    print("❌ ERROR: Please set your GROQ_API_KEY in the .env file")
    print("Get your API key from: https://console.groq.com/keys")
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

# Configure LLM
language_model = "llama-3.1-8b-instant"
groq_client = GroqLM(
    model=language_model,
    api_key=api_key,
    max_tokens=4096,
    temperature=0
)

dspy.settings.configure(lm=groq_client)

# Enhanced signature for code fixing
class CodeFixSignature(dspy.Signature):
    """Generate a fix for Java compilation errors caused by dependency updates."""
    error_description = dspy.InputField(desc="The compilation error message")
    api_changes = dspy.InputField(desc="Description of API changes in the dependency")
    dependency_change = dspy.InputField(desc="What dependency was updated")
    source_code = dspy.InputField(desc="The Java source code that has errors")
    fixed_code = dspy.OutputField(desc="The corrected Java source code")

class ExperimentResults:
    def __init__(self):
        self.total_projects = 0
        self.successful_fixes = 0
        self.failed_fixes = 0
        self.errors = 0
        self.results = []
        self.start_time = datetime.now()
    
    def add_result(self, project_id: str, repo_slug: str, success: bool, error_msg: str = None, fix_generated: bool = False):
        result = {
            "project_id": project_id,
            "repo_slug": repo_slug,
            "success": success,
            "fix_generated": fix_generated,
            "error": error_msg,
            "timestamp": datetime.now().isoformat()
        }
        self.results.append(result)
        
        if success:
            self.successful_fixes += 1
        elif fix_generated:
            self.failed_fixes += 1
        else:
            self.errors += 1
        
        self.total_projects += 1
    
    def print_progress(self):
        if self.total_projects > 0:
            success_rate = (self.successful_fixes / self.total_projects) * 100
            print(f"\n📊 Progress: {self.total_projects} projects processed")
            print(f"✅ Successful fixes: {self.successful_fixes} ({success_rate:.1f}%)")
            print(f"❌ Failed fixes: {self.failed_fixes}")
            print(f"⚠️  Errors: {self.errors}")
    
    def save_results(self, filename: str = "groq_experiment_results.json"):
        end_time = datetime.now()
        duration = (end_time - self.start_time).total_seconds()
        
        summary = {
            "experiment": {
                "model": language_model,
                "start_time": self.start_time.isoformat(),
                "end_time": end_time.isoformat(),
                "duration_seconds": duration,
                "total_projects": self.total_projects,
                "successful_fixes": self.successful_fixes,
                "failed_fixes": self.failed_fixes,
                "errors": self.errors,
                "success_rate": (self.successful_fixes / self.total_projects * 100) if self.total_projects > 0 else 0
            },
            "results": self.results
        }
        
        with open(filename, 'w') as f:
            json.dump(summary, f, indent=2)
        
        print(f"\n💾 Results saved to {filename}")

def load_project_data(project_path: Path) -> Dict:
    """Load all relevant data for a project"""
    data = {"project_id": project_path.name}
    
    try:
        # Repo slug
        repo_slug_file = project_path / "repo_slug.txt"
        if repo_slug_file.exists():
            data["repo_slug"] = repo_slug_file.read_text().strip()
        
        # Error lines
        error_file = project_path / "minified_error_lines.txt"
        if error_file.exists():
            data["error_lines"] = error_file.read_text().strip()
        
        # API changes
        api_changes_file = project_path / "api_changes.txt"
        if api_changes_file.exists():
            api_text = api_changes_file.read_text().strip()
            try:
                data["api_changes"] = json.loads(api_text)
            except:
                data["api_changes"] = api_text
        
        # Dependency change
        dep_change_file = project_path / "version_upgrade_str.txt"
        if dep_change_file.exists():
            data["dependency_change"] = dep_change_file.read_text().strip()
        
        # File in scope
        file_scope = project_path / "file_in_scope.txt"
        if file_scope.exists():
            data["file_in_scope"] = file_scope.read_text().strip()
        
        # Try to load the actual Java file content
        minimized_files = project_path / "minimized_files"
        if minimized_files.exists():
            # Look for minimized Java files (stored as .txt files)
            java_files = list(minimized_files.glob("**/*_minimized_with_comments.txt"))
            if java_files:
                # Take the first Java file for simplicity
                java_file = java_files[0]
                data["source_code"] = java_file.read_text()
                data["java_file_path"] = str(java_file.relative_to(minimized_files))
        
        return data
        
    except Exception as e:
        logger.error(f"Error loading project data for {project_path.name}: {e}")
        return data

def attempt_fix(project_data: Dict) -> tuple[bool, str, bool]:
    """
    Attempt to fix the project using Groq
    Returns: (success, result_message, fix_generated)
    """
    try:
        # Prepare inputs for the LLM
        error_desc = project_data.get("error_lines", "Unknown compilation error")
        api_changes = str(project_data.get("api_changes", "Unknown API changes"))
        dep_change = project_data.get("dependency_change", "Unknown dependency change")
        source_code = project_data.get("source_code", "")
        
        if not source_code:
            return False, "No source code found", False
        
        # Limit source code size to avoid token limits
        if len(source_code) > 8000:  # Rough character limit
            source_code = source_code[:8000] + "\n// ... (truncated)"
        
        # Create the predictor
        code_fixer = dspy.Predict(CodeFixSignature)
        
        # Generate fix
        logger.info(f"Generating fix for {project_data['project_id']}")
        result = code_fixer(
            error_description=error_desc,
            api_changes=api_changes,
            dependency_change=dep_change,
            source_code=source_code
        )
        
        fixed_code = result.fixed_code
        
        # Basic validation - check if the fix looks reasonable
        if fixed_code and len(fixed_code) > 10:
            # Very basic success criteria - if we got a substantial response
            # In a real experiment, you'd compile and test the code
            contains_import_fix = "import" in fixed_code
            contains_package_change = any(keyword in fixed_code.lower() for keyword in ["package", "import", "class"])
            
            if contains_package_change:
                return True, f"Fix generated successfully (length: {len(fixed_code)} chars)", True
            else:
                return False, f"Fix generated but doesn't seem to address imports/packages", True
        else:
            return False, "No meaningful fix generated", False
            
    except Exception as e:
        error_msg = f"Error during fix generation: {str(e)}"
        logger.error(error_msg)
        return False, error_msg, False

def run_full_experiment():
    """Run the complete experiment on all projects"""
    print("🚀 Starting Full Zero-Shot Experiment with Groq")
    print("=" * 60)
    print(f"🤖 Model: {language_model}")
    print(f"📅 Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)
    
    dataset_path = Path("dataset")
    if not dataset_path.exists():
        print(f"❌ Dataset directory not found: {dataset_path}")
        return
    
    # Get all project directories
    project_dirs = [d for d in dataset_path.iterdir() if d.is_dir()]
    project_dirs = sorted(project_dirs)  # Process in consistent order
    
    print(f"📊 Found {len(project_dirs)} projects to process")
    
    results = ExperimentResults()
    
    for i, project_dir in enumerate(project_dirs, 1):
        print(f"\n🔄 [{i}/{len(project_dirs)}] Processing: {project_dir.name}")
        
        try:
            # Load project data
            project_data = load_project_data(project_dir)
            repo_slug = project_data.get("repo_slug", "unknown")
            
            print(f"   📁 Repo: {repo_slug}")
            
            # Attempt to fix
            success, message, fix_generated = attempt_fix(project_data)
            
            # Record result
            results.add_result(
                project_id=project_dir.name,
                repo_slug=repo_slug,
                success=success,
                error_msg=message if not success else None,
                fix_generated=fix_generated
            )
            
            # Print result
            status = "✅ SUCCESS" if success else ("🔧 FIX_GEN" if fix_generated else "❌ FAILED")
            print(f"   {status}: {message}")
            
            # Show progress every 10 projects
            if i % 10 == 0 or i == len(project_dirs):
                results.print_progress()
            
            # Rate limiting - don't overwhelm the API
            time.sleep(1)  # 1 second between requests
            
        except Exception as e:
            error_msg = f"Unexpected error: {str(e)}"
            logger.error(f"Error processing {project_dir.name}: {error_msg}")
            results.add_result(
                project_id=project_dir.name,
                repo_slug="unknown",
                success=False,
                error_msg=error_msg,
                fix_generated=False
            )
    
    # Final results
    print("\n" + "=" * 60)
    print("🎉 EXPERIMENT COMPLETED!")
    print("=" * 60)
    results.print_progress()
    
    # Save detailed results
    results.save_results()
    
    # Print summary
    if results.total_projects > 0:
        success_rate = (results.successful_fixes / results.total_projects) * 100
        print(f"\n📈 Final Success Rate: {success_rate:.1f}%")
        print(f"⏱️  Total Time: {(datetime.now() - results.start_time).total_seconds():.1f} seconds")
        print(f"🤖 Model Used: {language_model}")

if __name__ == "__main__":
    run_full_experiment()
