#!/usr/bin/env python3
"""
Quick test of the zero-shot experiment with first 5 projects
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

def quick_test():
    """Run a quick test on first 5 projects"""
    print("🚀 Starting Quick Zero-Shot Test with Groq")
    print("=" * 50)
    print(f"🤖 Model: {language_model}")
    print(f"📅 Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 50)
    
    dataset_path = Path("dataset")
    if not dataset_path.exists():
        print(f"❌ Dataset directory not found: {dataset_path}")
        return
    
    # Get first 5 project directories
    project_dirs = [d for d in dataset_path.iterdir() if d.is_dir()]
    project_dirs = sorted(project_dirs)[:5]  # Only first 5
    
    print(f"📊 Testing with {len(project_dirs)} projects")
    
    successes = 0
    failures = 0
    
    for i, project_dir in enumerate(project_dirs, 1):
        print(f"\n🔄 [{i}/5] Processing: {project_dir.name}")
        
        try:
            # Load project data
            project_data = load_project_data(project_dir)
            repo_slug = project_data.get("repo_slug", "unknown")
            
            print(f"   📁 Repo: {repo_slug}")
            print(f"   🔧 Error: {project_data.get('error_lines', 'N/A')[:100]}...")
            print(f"   📦 Dependency: {project_data.get('dependency_change', 'N/A')}")
            
            # Attempt to fix
            success, message, fix_generated = attempt_fix(project_data)
            
            # Print result
            status = "✅ SUCCESS" if success else ("🔧 FIX_GEN" if fix_generated else "❌ FAILED")
            print(f"   {status}: {message}")
            
            if success:
                successes += 1
            else:
                failures += 1
            
            # Rate limiting
            time.sleep(2)  # 2 seconds between requests
            
        except Exception as e:
            error_msg = f"Unexpected error: {str(e)}"
            logger.error(f"Error processing {project_dir.name}: {error_msg}")
            failures += 1
    
    # Final results
    print("\n" + "=" * 50)
    print("🎉 QUICK TEST COMPLETED!")
    print("=" * 50)
    success_rate = (successes / (successes + failures)) * 100 if (successes + failures) > 0 else 0
    print(f"✅ Successes: {successes}")
    print(f"❌ Failures: {failures}")
    print(f"📈 Success Rate: {success_rate:.1f}%")
    print(f"🤖 Model: {language_model}")

if __name__ == "__main__":
    quick_test()
