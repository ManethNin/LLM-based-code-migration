#!/usr/bin/env python3
"""
Minimal Zero-Shot Approach with Groq
"""

import os
import json
import logging
from pathlib import Path
from typing import Dict

# Configure logging
logging.basicConfig(level=logging.INFO)
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

print(f"✅ Configured Groq with model: {language_model}")

# Simple signature for code fixing
class CodeFixSignature(dspy.Signature):
    """Generate a fix for Java compilation errors caused by dependency updates."""
    error_description = dspy.InputField()
    api_changes = dspy.InputField()
    source_code = dspy.InputField()
    fixed_code = dspy.OutputField()

def test_code_fix():
    """Test the code fixing functionality"""
    
    # Create predictor
    code_fixer = dspy.Predict(CodeFixSignature)
    
    # Test with simple example
    test_error = "error: package org.example.old does not exist"
    test_api_changes = "org.example.old -> org.example.new"
    test_code = """
import org.example.old.SomeClass;

public class TestClass {
    public void method() {
        SomeClass obj = new SomeClass();
    }
}
"""
    
    print("🔄 Testing code fix generation...")
    
    try:
        result = code_fixer(
            error_description=test_error,
            api_changes=test_api_changes,
            source_code=test_code
        )
        
        print("✅ Generated fix:")
        print(result.fixed_code)
        return True
        
    except Exception as e:
        print(f"❌ Error generating fix: {e}")
        return False

def load_sample_dataset():
    """Load a few samples from the dataset for testing"""
    dataset_path = Path("dataset")
    
    if not dataset_path.exists():
        print(f"❌ Dataset directory not found: {dataset_path}")
        return []
    
    # Get first few directories as samples
    samples = []
    for dir_path in sorted(dataset_path.iterdir())[:3]:  # Just first 3 for testing
        if dir_path.is_dir():
            try:
                # Load basic info
                repo_slug_file = dir_path / "repo_slug.txt"
                if repo_slug_file.exists():
                    repo_slug = repo_slug_file.read_text().strip()
                    samples.append({
                        "commit_hash": dir_path.name,
                        "repo_slug": repo_slug,
                        "path": dir_path
                    })
            except Exception as e:
                print(f"⚠️  Error loading sample {dir_path.name}: {e}")
    
    return samples

def main():
    """Main execution"""
    print("🚀 Starting Zero-Shot Approach with Groq")
    print("=" * 50)
    
    # Test basic functionality
    if not test_code_fix():
        print("❌ Basic test failed")
        return
    
    # Load sample dataset
    samples = load_sample_dataset()
    if not samples:
        print("⚠️  No dataset samples found, running basic test only")
        return
    
    print(f"✅ Loaded {len(samples)} sample(s) from dataset")
    
    for sample in samples:
        print(f"\n📁 Processing: {sample['repo_slug']} ({sample['commit_hash'][:8]})")
        # Here you would add the actual processing logic
        # For now, just report what we found
        
    print("\n🎉 Minimal zero-shot approach completed successfully!")
    print("To run the full experiment, use the complete upgradellm.py script")

if __name__ == "__main__":
    main()
