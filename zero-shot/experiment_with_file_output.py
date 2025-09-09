#!/usr/bin/env python3
"""
Enhanced Zero-Shot Experiment with File Output
Saves generated fixes as actual Java files in the out/ directory
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
import re

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

# Improved signature for code fixing
class ImprovedCodeFixSignature(dspy.Signature):
    """Fix Java compilation errors caused by dependency upgrades.
    
    IMPORTANT: Return ONLY the complete, corrected Java file content. 
    Do NOT include markdown formatting, explanations, or backticks.
    Do NOT include any text before or after the Java code.
    The output should be valid Java source code that can be compiled directly.
    """
    
    error_description: str = dspy.InputField(desc="The compilation error message")
    dependency_change: str = dspy.InputField(desc="What dependency was upgraded (e.g., 'mysql:mysql-connector-java 5.1.49 -> 8.0.28')")
    api_changes: str = dspy.InputField(desc="Description of API changes in the new dependency version")
    source_code: str = dspy.InputField(desc="The Java source code that has compilation errors")
    
    fixed_code: str = dspy.OutputField(desc="Complete corrected Java file content (NO markdown, NO explanations, ONLY Java code)")

def clean_generated_code(generated_code: str) -> str:
    """Clean the generated code to remove markdown formatting and explanations"""
    # Remove markdown code blocks
    if "```java" in generated_code:
        # Extract content between ```java and ```
        pattern = r'```java\s*(.*?)\s*```'
        match = re.search(pattern, generated_code, re.DOTALL)
        if match:
            generated_code = match.group(1)
    
    # Remove any remaining backticks
    generated_code = generated_code.replace('```', '')
    
    # Remove common prefixes/explanations
    lines = generated_code.split('\n')
    java_started = False
    cleaned_lines = []
    
    for line in lines:
        line = line.strip()
        # Look for the start of actual Java code
        if not java_started:
            if line.startswith('package ') or line.startswith('import ') or line.startswith('public class') or line.startswith('/**'):
                java_started = True
                cleaned_lines.append(line)
            # Skip explanation lines
            elif any(prefix in line.lower() for prefix in ['repo slug:', 'dependency change:', 'error lines:', 'api changes:']):
                continue
        else:
            cleaned_lines.append(line)
    
    return '\n'.join(cleaned_lines).strip()

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
                            data["java_file_path"] = relative_path
                        break
            
        return data
        
    except Exception as e:
        logger.error(f"Error loading project data for {project_path.name}: {e}")
        return data

def simple_javac_check(fixed_code: str, java_file_name: str) -> Tuple[bool, str]:
    """Simple check using javac"""
    try:
        with tempfile.TemporaryDirectory() as temp_dir:
            # Clean the filename - remove duplicate .java extensions
            if java_file_name.endswith('.java.java'):
                java_file_name = java_file_name[:-5]  # Remove one .java
            elif not java_file_name.endswith('.java'):
                java_file_name += '.java'
                
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

def save_generated_fix(project_path: Path, fixed_code: str, java_file_path: str, experiment_name: str) -> str:
    """Save the generated fix to the project's out/ directory"""
    try:
        # Create out directory if it doesn't exist
        out_dir = project_path / "out"
        out_dir.mkdir(exist_ok=True)
        
        # Clean the java file name
        java_filename = Path(java_file_path).name
        if java_filename.endswith('.java.java'):
            java_filename = java_filename[:-5]  # Remove one .java
        elif not java_filename.endswith('.java'):
            java_filename += '.java'
        
        # Create a unique filename with experiment name
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_filename = f"groq-{experiment_name}-{timestamp}-{java_filename}"
        output_path = out_dir / output_filename
        
        # Save the fixed code
        output_path.write_text(fixed_code)
        
        logger.info(f"Saved generated fix to: {output_path}")
        return str(output_path)
        
    except Exception as e:
        logger.error(f"Error saving fix for {project_path.name}: {e}")
        return ""

def test_project_with_file_output(project_path: Path, experiment_name: str = "zero-shot"):
    """Test a single project and save the generated fix to file"""
    print(f"\n{'='*60}")
    print(f"🔄 Testing Project: {project_path.name}")
    print(f"{'='*60}")
    
    # Load project data
    project_data = load_project_data(project_path)
    
    print(f"📁 Repo: {project_data.get('repo_slug', 'unknown')}")
    print(f"📦 Dependency: {project_data.get('dependency_change', 'unknown')}")
    print(f"🔧 Error preview: {project_data.get('error_lines', 'N/A')[:150]}...")
    
    if "source_code" not in project_data:
        print("❌ No source code found")
        return {"project_id": project_path.name, "error": "No source code"}
    
    print(f"📄 Java file: {project_data.get('java_file_path', 'unknown')}")
    print(f"📏 Source code length: {len(project_data['source_code'])} chars")
    
    try:
        # Generate fix with improved prompt
        print("\n🤖 Generating fix...")
        code_fixer = dspy.Predict(ImprovedCodeFixSignature)
        
        result = code_fixer(
            error_description=project_data.get("error_lines", "Unknown error"),
            dependency_change=project_data.get("dependency_change", "Unknown dependency change"),
            api_changes=str(project_data.get("api_changes", "No API changes documented")),
            source_code=project_data["source_code"]
        )
        
        # Clean the generated code
        raw_fix = result.fixed_code
        cleaned_fix = clean_generated_code(raw_fix)
        
        print(f"✅ Fix generated")
        print(f"   📏 Raw length: {len(raw_fix)} chars")
        print(f"   📏 Cleaned length: {len(cleaned_fix)} chars")
        
        # Save the generated fix to file
        saved_path = save_generated_fix(
            project_path, 
            cleaned_fix, 
            project_data.get("java_file_path", "Unknown.java"),
            experiment_name
        )
        
        # Test compilation
        print(f"\n🔧 Testing compilation...")
        java_file_name = project_data.get('java_file_path', 'Test.java')
        
        compile_success, compile_errors = simple_javac_check(cleaned_fix, java_file_name)
        
        if compile_success:
            print("✅ COMPILATION SUCCESSFUL!")
        else:
            print("❌ COMPILATION FAILED:")
            print(f"Errors: {compile_errors[:300]}...")
        
        print(f"💾 Generated fix saved to: {saved_path}")
        
        return {
            "project_id": project_path.name,
            "repo_slug": project_data.get("repo_slug", "unknown"),
            "fix_generated": True,
            "raw_fix_length": len(raw_fix),
            "cleaned_fix_length": len(cleaned_fix),
            "compilation_success": compile_success,
            "compilation_errors": compile_errors if not compile_success else None,
            "saved_file_path": saved_path,
            "java_file_path": project_data.get("java_file_path", "unknown")
        }
        
    except Exception as e:
        print(f"❌ ERROR: {str(e)}")
        return {
            "project_id": project_path.name,
            "fix_generated": False,
            "error": str(e)
        }

def main():
    """Test projects with file output to out/ directories"""
    print("🚀 Zero-Shot Experiment with File Output")
    print("Generating fixes and saving to project out/ directories")
    print("=" * 70)
    
    dataset_dir = Path("dataset")
    if not dataset_dir.exists():
        print("❌ ERROR: Dataset directory not found")
        return
    
    # Get first 3 project directories for testing
    project_dirs = [d for d in dataset_dir.iterdir() if d.is_dir()]
    project_dirs = sorted(project_dirs)[:3]  # Test with first 3 projects
    
    results = []
    experiment_name = "zero-shot-with-files"
    
    for project_dir in project_dirs:
        result = test_project_with_file_output(project_dir, experiment_name)
        results.append(result)
        time.sleep(3)  # Rate limiting for Groq API
    
    # Summary
    print(f"\n{'='*70}")
    print("🎯 EXPERIMENT SUMMARY WITH FILE OUTPUT")
    print(f"{'='*70}")
    
    total = len(results)
    successful_fixes = sum(1 for r in results if r.get('fix_generated', False))
    successful_saves = sum(1 for r in results if r.get('saved_file_path', ''))
    successful_compilations = sum(1 for r in results if r.get('compilation_success', False))
    
    print(f"📊 Total projects tested: {total}")
    print(f"✅ Fixes generated: {successful_fixes}/{total} ({successful_fixes/total*100:.1f}%)")
    print(f"💾 Files saved: {successful_saves}/{total} ({successful_saves/total*100:.1f}%)")
    print(f"🔧 Successful compilations: {successful_compilations}/{total} ({successful_compilations/total*100:.1f}%)")
    
    if successful_saves > 0:
        print(f"\n📁 Generated files saved to:")
        for result in results:
            if result.get('saved_file_path'):
                print(f"  💾 {result['project_id']}: {result['saved_file_path']}")
    
    # Save results
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"groq_experiment_with_files_{timestamp}.json"
    with open(filename, "w") as f:
        json.dump({
            "timestamp": datetime.now().isoformat(),
            "experiment_type": "zero_shot_with_file_output",
            "model": "llama-3.1-8b-instant",
            "results": results,
            "summary": {
                "total": total,
                "fixes_generated": successful_fixes,
                "files_saved": successful_saves,
                "successful_compilations": successful_compilations,
                "success_rate": successful_compilations/total*100 if total > 0 else 0
            }
        }, f, indent=2)
    
    print(f"\n💾 Detailed results saved to {filename}")

if __name__ == "__main__":
    main()
