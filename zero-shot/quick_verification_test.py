#!/usr/bin/env python3
"""
Quick Verification Test - Test first 3 projects with detailed debugging
"""

import os
import json
import logging
import time
import tempfile
import subprocess
from pathlib import Path
from typing import Dict, List, Optional, Tuple
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
    model="llama-3.1-8b-instant",
    api_key=api_key,
    max_tokens=4096,
    temperature=0
)

dspy.configure(lm=groq_lm)

# Enhanced signature for code fixing
class CodeFixSignature(dspy.Signature):
    """You are a Java expert. Fix the compilation error caused by a dependency upgrade.
    
    Provide a complete, corrected version of the Java file that compiles successfully.
    """
    
    repo_slug: str = dspy.InputField(desc="GitHub repository (e.g., 'user/repo')")
    dependency_change: str = dspy.InputField(desc="Dependency version change (e.g., 'lib:1.0->2.0')")
    error_lines: str = dspy.InputField(desc="Compilation error messages")
    api_changes: str = dspy.InputField(desc="API changes in the dependency")
    source_code: str = dspy.InputField(desc="The broken Java source code to fix")
    file_path: str = dspy.InputField(desc="Relative path to the Java file")
    
    fixed_code: str = dspy.OutputField(desc="Complete fixed Java file content")

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
        
        # Load the actual Java file content
        minimized_files = project_path / "minimized_files"
        if minimized_files.exists():
            # Find minimized Java files (stored as .txt files)
            for root, dirs, files in os.walk(minimized_files):
                for file in files:
                    if file.endswith('_minimized_with_comments.txt'):
                        file_path = os.path.join(root, file)
                        with open(file_path, 'r') as f:
                            data["source_code"] = f.read()
                            # Extract the relative path from the filename
                            relative_path = file.replace('_minimized_with_comments.txt', '.java')
                            relative_path = relative_path.replace(str(minimized_files) + '/', '')
                            data["java_file_path"] = relative_path
                        break
            
        return data
        
    except Exception as e:
        logger.error(f"Error loading project data for {project_path.name}: {e}")
        return data

def simple_javac_check(fixed_code: str, java_file_name: str) -> Tuple[bool, str]:
    """Simple check using javac - just see if the Java syntax is valid"""
    try:
        with tempfile.TemporaryDirectory() as temp_dir:
            java_file = Path(temp_dir) / java_file_name
            java_file.write_text(fixed_code)
            
            # Try to compile with javac
            result = subprocess.run(
                ["javac", str(java_file)],
                capture_output=True,
                text=True,
                timeout=30,
                cwd=temp_dir
            )
            
            success = result.returncode == 0
            error_output = result.stderr + result.stdout
            
            return success, error_output
            
    except subprocess.TimeoutExpired:
        return False, "javac timeout"
    except FileNotFoundError:
        return False, "javac not available"
    except Exception as e:
        return False, f"javac error: {str(e)}"

def test_project(project_path: Path):
    """Test a single project"""
    print(f"\n{'='*60}")
    print(f"🔄 Testing Project: {project_path.name}")
    print(f"{'='*60}")
    
    # Load project data
    project_data = load_project_data(project_path)
    
    print(f"📁 Repo: {project_data.get('repo_slug', 'unknown')}")
    print(f"📦 Dependency: {project_data.get('dependency_change', 'unknown')}")
    print(f"🔧 Error preview: {project_data.get('error_lines', 'N/A')[:200]}...")
    
    if "source_code" not in project_data:
        print("❌ No source code found")
        return
    
    print(f"📄 Java file: {project_data.get('java_file_path', 'unknown')}")
    print(f"📏 Source code length: {len(project_data['source_code'])} chars")
    
    try:
        # Generate fix
        print("\n🤖 Generating fix...")
        code_fixer = dspy.ChainOfThought(CodeFixSignature)
        
        result = code_fixer(
            repo_slug=project_data.get("repo_slug", "unknown/unknown"),
            dependency_change=project_data.get("dependency_change", "unknown"),
            error_lines=project_data["error_lines"],
            api_changes=json.dumps(project_data.get("api_changes", {})),
            source_code=project_data["source_code"],
            file_path=project_data["java_file_path"]
        )
        
        fixed_code = result.fixed_code
        print(f"✅ Fix generated ({len(fixed_code)} chars)")
        
        # Show a preview of the fix
        print(f"\n📋 Fix preview (first 500 chars):")
        print(f"```java")
        print(fixed_code[:500])
        if len(fixed_code) > 500:
            print("... (truncated)")
        print(f"```")
        
        # Test compilation
        print(f"\n🔧 Testing compilation...")
        java_file_name = project_data.get('java_file_path', 'Test.java').split('/')[-1]
        
        compile_success, compile_errors = simple_javac_check(fixed_code, java_file_name)
        
        if compile_success:
            print("✅ COMPILATION SUCCESSFUL!")
        else:
            print("❌ COMPILATION FAILED:")
            print(f"Errors: {compile_errors[:500]}...")
        
        return {
            "project_id": project_path.name,
            "fix_generated": True,
            "fix_length": len(fixed_code),
            "compilation_success": compile_success,
            "compilation_errors": compile_errors if not compile_success else None
        }
        
    except Exception as e:
        print(f"❌ ERROR: {str(e)}")
        return {
            "project_id": project_path.name,
            "fix_generated": False,
            "error": str(e)
        }

def main():
    """Test first 3 projects with detailed verification"""
    print("🚀 Quick Verification Test")
    print("Testing first 3 projects with detailed debugging")
    print("=" * 70)
    
    dataset_dir = Path("dataset")
    if not dataset_dir.exists():
        print("❌ ERROR: Dataset directory not found")
        return
    
    # Get first 3 project directories
    project_dirs = [d for d in dataset_dir.iterdir() if d.is_dir()]
    project_dirs = sorted(project_dirs)[:3]
    
    results = []
    
    for project_dir in project_dirs:
        result = test_project(project_dir)
        results.append(result)
        time.sleep(2)  # Rate limiting
    
    # Summary
    print(f"\n{'='*70}")
    print("🎯 SUMMARY")
    print(f"{'='*70}")
    
    total = len(results)
    successful_fixes = sum(1 for r in results if r.get('fix_generated', False))
    successful_compilations = sum(1 for r in results if r.get('compilation_success', False))
    
    print(f"📊 Total projects tested: {total}")
    print(f"✅ Fixes generated: {successful_fixes}/{total} ({successful_fixes/total*100:.1f}%)")
    print(f"🔧 Successful compilations: {successful_compilations}/{total} ({successful_compilations/total*100:.1f}%)")
    
    # Save results
    with open("quick_verification_results.json", "w") as f:
        json.dump({
            "timestamp": datetime.now().isoformat(),
            "results": results,
            "summary": {
                "total": total,
                "fixes_generated": successful_fixes,
                "successful_compilations": successful_compilations
            }
        }, f, indent=2)
    
    print(f"\n💾 Detailed results saved to quick_verification_results.json")

if __name__ == "__main__":
    main()
