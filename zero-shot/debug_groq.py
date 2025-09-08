#!/usr/bin/env python3
"""Debug the DSPy Groq integration"""

import os
from dotenv import load_dotenv
import dspy

load_dotenv(".env")

# Test with verbose output
try:
    groq_client = dspy.GROQ(
        model="llama-3.1-70b-versatile", 
        api_key=os.getenv("GROQ_API_KEY")
    )
    
    print("Groq client attributes:")
    print(f"Model: {getattr(groq_client, 'model', 'NOT SET')}")
    print(f"API Key present: {bool(getattr(groq_client, 'api_key', None))}")
    
    # Look at the underlying client
    if hasattr(groq_client, 'client'):
        print(f"Has underlying client: {groq_client.client}")
    
    # Test a simple call
    print("\nTesting direct call...")
    response = groq_client("What is 2+2?", max_tokens=10)
    print(f"Response: {response}")
    
except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()
