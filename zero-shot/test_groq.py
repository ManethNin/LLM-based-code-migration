#!/usr/bin/env python3
"""
Test script to verify Groq integration with DSPy
"""

import os
from dotenv import load_dotenv
import dspy

# Load environment variables
load_dotenv(".env")

def test_groq_connection():
    """Test basic Groq connectivity"""
    
    # Check if API key is set
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key or api_key == "gsk_your_groq_api_key_here":
        print("❌ ERROR: Please set your GROQ_API_KEY in the .env file")
        print("Get your API key from: https://console.groq.com/keys")
        return False
    
    try:
        # Initialize Groq client
        groq_client = dspy.GROQ(
            model="llama-3.1-70b-versatile",
            api_key=api_key,
            max_tokens=1024,
            temperature=0
        )
        
        # Configure DSPy settings
        dspy.settings.configure(lm=groq_client)
        
        # Test simple completion
        print("🔄 Testing Groq connection...")
        
        # Create a simple signature for testing
        class SimpleQA(dspy.Signature):
            """Answer questions briefly and accurately."""
            question = dspy.InputField()
            answer = dspy.OutputField()
        
        # Create a predictor
        qa = dspy.Predict(SimpleQA)
        
        # Test the connection
        response = qa(question="What is 2+2?")
        
        print(f"✅ Success! Groq responded: {response.answer}")
        return True
        
    except Exception as e:
        print(f"❌ Error connecting to Groq: {str(e)}")
        return False

if __name__ == "__main__":
    print("Testing Groq integration for zero-shot approach...")
    print("=" * 50)
    
    success = test_groq_connection()
    
    if success:
        print("\n✅ Groq integration test passed!")
        print("You can now run the main experiment with: pdm run python upgradellm.py")
    else:
        print("\n❌ Groq integration test failed!")
        print("Please check your API key and internet connection.")
