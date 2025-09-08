#!/usr/bin/env python3
"""
Zero-Shot Experiment with Comprehensive Verification
Includes compilation and test verification like the original system
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

class VerificationResults:
    """Container for verification results"""
    def __init__(self):
        self.compilation_attempted = False
        self.compilation_success = False
        self.compilation_errors = ""
        
        self.test_attempted = False
        self.test_success = False
        self.test_errors = ""
        
        self.processing_time = 0
        self.fix_applied = False

class JavaCompilerVerifier:
    """Handles Java compilation verification"""
    
    def __init__(self, project_dir: Path):
        self.project_dir = project_dir
        self.temp_dir = None
    
    def setup_temp_project(self, fixed_code: str, java_file_path: str) -> Path:
        """Set up a temporary project with the fixed code"""
        self.temp_dir = Path(tempfile.mkdtemp(prefix="java_verify_"))
        
        # Copy project structure
        temp_project = self.temp_dir / "project"
        temp_project.mkdir(parents=True)
        
        # Create the fixed Java file
        fixed_file = temp_project / java_file_path
        fixed_file.parent.mkdir(parents=True, exist_ok=True)
        fixed_file.write_text(fixed_code)
        
        # Copy pom.xml if it exists
        pom_file = self.project_dir / "pom.xml"
        if pom_file.exists():
            (temp_project / "pom.xml").write_text(pom_file.read_text())
        
        return temp_project
    
    def verify_compilation(self, fixed_code: str, java_file_path: str) -> Tuple[bool, str]:
        """Verify if the fixed code compiles"""
        try:
            temp_project = self.setup_temp_project(fixed_code, java_file_path)
            
            # Try Maven compilation
            result = subprocess.run(
                ["mvn", "compile", "-q"],
                cwd=temp_project,
                capture_output=True,
                text=True,
                timeout=120  # 2 minute timeout
            )
            
            success = result.returncode == 0
            error_output = result.stderr + result.stdout
            
            return success, error_output
            
        except subprocess.TimeoutExpired:
            return False, "Compilation timeout (>2 minutes)"
        except FileNotFoundError:
            # Maven not available, try javac
            return self._verify_with_javac(fixed_code, java_file_path)
        except Exception as e:
            return False, f"Compilation verification error: {str(e)}"
        finally:
            self.cleanup()
    
    def _verify_with_javac(self, fixed_code: str, java_file_path: str) -> Tuple[bool, str]:
        """Fallback verification with javac"""
        try:
            temp_project = self.setup_temp_project(fixed_code, java_file_path)
            java_file = temp_project / java_file_path
            
            result = subprocess.run(
                ["javac", str(java_file)],
                capture_output=True,
                text=True,
                timeout=30
            )
            
            success = result.returncode == 0
            error_output = result.stderr + result.stdout
            
            return success, error_output
            
        except subprocess.TimeoutExpired:
            return False, "javac timeout"
        except FileNotFoundError:
            return False, "Neither Maven nor javac available for compilation verification"
        except Exception as e:
            return False, f"javac verification error: {str(e)}"
    
    def verify_tests(self, fixed_code: str, java_file_path: str) -> Tuple[bool, str]:
        """Verify if tests pass with the fixed code"""
        try:
            temp_project = self.setup_temp_project(fixed_code, java_file_path)
            
            # Run Maven tests
            result = subprocess.run(
                ["mvn", "test", "-q"],
                cwd=temp_project,
                capture_output=True,
                text=True,
                timeout=300  # 5 minute timeout
            )
            
            success = result.returncode == 0
            error_output = result.stderr + result.stdout
            
            return success, error_output
            
        except subprocess.TimeoutExpired:
            return False, "Test timeout (>5 minutes)"
        except FileNotFoundError:
            return False, "Maven not available for test verification"
        except Exception as e:
            return False, f"Test verification error: {str(e)}"
    
    def cleanup(self):
        """Clean up temporary files"""
        if self.temp_dir and self.temp_dir.exists():
            import shutil
            shutil.rmtree(self.temp_dir, ignore_errors=True)

class ExperimentResults:
    """Tracks experiment results with verification"""
    def __init__(self):
        self.results = []
        self.summary = {
            "total_projects": 0,
            "successful_fixes": 0,
            "compilation_success": 0,
            "test_success": 0,
            "failed_fixes": 0,
            "errors": 0
        }
    
    def add_result(self, project_id: str, result: Dict):
        """Add a project result"""
        self.results.append(result)
        self.summary["total_projects"] += 1
        
        if result["success"]:
            self.summary["successful_fixes"] += 1
            
            verification = result.get("verification", {})
            if verification.get("compilation_success"):
                self.summary["compilation_success"] += 1
            if verification.get("test_success"):
                self.summary["test_success"] += 1
        else:
            if "error" in result:
                self.summary["errors"] += 1
            else:
                self.summary["failed_fixes"] += 1
    
    def save_results(self, filename: str):
        """Save results to JSON file"""
        data = {
            "experiment_metadata": {
                "model": "llama-3.1-8b-instant",
                "timestamp": datetime.now().strftime("%Y-%m-%d_%H:%M:%S"),
                "verification_enabled": True
            },
            "results": self.results,
            "summary": self.summary
        }
        
        with open(filename, 'w') as f:
            json.dump(data, f, indent=2)
        
        print(f"\\n💾 Results saved to {filename}")

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

def attempt_fix_with_verification(project_data: Dict) -> Tuple[bool, str, str, VerificationResults]:
    """Attempt to fix the code and verify the result"""
    verification = VerificationResults()
    start_time = time.time()
    
    try:
        if not all(key in project_data for key in ["source_code", "error_lines", "java_file_path"]):
            return False, "Missing required project data", "", verification
        
        # Create the code fixer
        code_fixer = dspy.ChainOfThought(CodeFixSignature)
        
        # Generate the fix
        logger.info(f"Generating fix for {project_data.get('project_id', 'unknown')}")
        
        result = code_fixer(
            repo_slug=project_data.get("repo_slug", "unknown/unknown"),
            dependency_change=project_data.get("dependency_change", "unknown"),
            error_lines=project_data["error_lines"],
            api_changes=json.dumps(project_data.get("api_changes", {})),
            source_code=project_data["source_code"],
            file_path=project_data["java_file_path"]
        )
        
        fixed_code = result.fixed_code
        verification.fix_applied = True
        
        # Verify the fix if we have the original project structure
        dataset_dir = Path("dataset") / project_data["project_id"]
        if dataset_dir.exists():
            verifier = JavaCompilerVerifier(dataset_dir)
            
            # Test compilation
            verification.compilation_attempted = True
            compilation_success, compilation_errors = verifier.verify_compilation(
                fixed_code, project_data["java_file_path"]
            )
            verification.compilation_success = compilation_success
            verification.compilation_errors = compilation_errors
            
            # Test execution (only if compilation succeeds)
            if compilation_success:
                verification.test_attempted = True
                test_success, test_errors = verifier.verify_tests(
                    fixed_code, project_data["java_file_path"]
                )
                verification.test_success = test_success
                verification.test_errors = test_errors
            
            verifier.cleanup()
        
        verification.processing_time = time.time() - start_time
        return True, "Fix generated successfully", fixed_code, verification
        
    except Exception as e:
        verification.processing_time = time.time() - start_time
        logger.error(f"Error in attempt_fix_with_verification: {e}")
        return False, str(e), "", verification

def run_experiment_with_verification():
    """Run the full experiment with verification"""
    print("🚀 Starting Zero-Shot Experiment with Verification")
    print("=" * 70)
    print(f"🤖 Model: llama-3.1-8b-instant")
    print(f"🔬 Verification: Compilation + Testing")
    print(f"📅 Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 70)
    
    # Find all project directories
    dataset_dir = Path("dataset")
    if not dataset_dir.exists():
        print("❌ ERROR: Dataset directory not found")
        return
    
    project_dirs = [d for d in dataset_dir.iterdir() if d.is_dir()]
    project_dirs.sort()
    
    print(f"📊 Found {len(project_dirs)} projects to process")
    
    results = ExperimentResults()
    
    for idx, project_dir in enumerate(project_dirs, 1):
        print(f"\\n🔄 [{idx}/{len(project_dirs)}] Processing: {project_dir.name}")
        
        try:
            # Load project data
            project_data = load_project_data(project_dir)
            
            if "repo_slug" in project_data:
                print(f"   📁 Repo: {project_data['repo_slug']}")
            
            # Attempt fix with verification
            success, message, fix_generated, verification = attempt_fix_with_verification(project_data)
            
            # Prepare result
            result = {
                "project_id": project_dir.name,
                "repo_slug": project_data.get("repo_slug", "unknown"),
                "success": success,
                "message": message,
                "fix_generated": fix_generated,
                "processing_time": verification.processing_time,
                "verification": {
                    "compilation_attempted": verification.compilation_attempted,
                    "compilation_success": verification.compilation_success,
                    "compilation_errors": verification.compilation_errors,
                    "test_attempted": verification.test_attempted,
                    "test_success": verification.test_success,
                    "test_errors": verification.test_errors,
                }
            }
            
            if not success:
                result["error_message"] = message
            
            results.add_result(project_dir.name, result)
            
            # Print status
            if success:
                status_msg = f"✅ SUCCESS: Fix generated"
                if verification.compilation_attempted:
                    if verification.compilation_success:
                        status_msg += " + ✅ COMPILES"
                        if verification.test_attempted:
                            if verification.test_success:
                                status_msg += " + ✅ TESTS PASS"
                            else:
                                status_msg += " + ❌ TESTS FAIL"
                    else:
                        status_msg += " + ❌ COMPILATION FAILS"
                print(status_msg)
            else:
                print(f"❌ FAILED: {message}")
            
        except Exception as e:
            logger.error(f"Error processing {project_dir.name}: {e}")
            result = {
                "project_id": project_dir.name,
                "success": False,
                "error_message": str(e),
                "processing_time": 0
            }
            results.add_result(project_dir.name, result)
            print(f"❌ ERROR: {str(e)}")
        
        # Show progress summary every 10 projects
        if idx % 10 == 0:
            summary = results.summary
            print(f"\\n📊 Progress Summary ({idx} projects):")
            print(f"   ✅ Successful fixes: {summary['successful_fixes']}")
            print(f"   🔧 Compilation success: {summary['compilation_success']}")
            print(f"   🧪 Test success: {summary['test_success']}")
            print(f"   ❌ Failed fixes: {summary['failed_fixes']}")
            print(f"   💥 Errors: {summary['errors']}")
    
    # Final summary
    summary = results.summary
    print(f"\\n🎯 FINAL RESULTS")
    print("=" * 50)
    print(f"📊 Total projects: {summary['total_projects']}")
    print(f"✅ Successful fixes: {summary['successful_fixes']} ({summary['successful_fixes']/summary['total_projects']*100:.1f}%)")
    print(f"🔧 Compilation success: {summary['compilation_success']} ({summary['compilation_success']/summary['total_projects']*100:.1f}%)")
    print(f"🧪 Test success: {summary['test_success']} ({summary['test_success']/summary['total_projects']*100:.1f}%)")
    print(f"❌ Failed fixes: {summary['failed_fixes']} ({summary['failed_fixes']/summary['total_projects']*100:.1f}%)")
    print(f"💥 Errors: {summary['errors']} ({summary['errors']/summary['total_projects']*100:.1f}%)")
    
    # Save results
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"groq_experiment_with_verification_{timestamp}.json"
    results.save_results(filename)

if __name__ == "__main__":
    run_experiment_with_verification()
