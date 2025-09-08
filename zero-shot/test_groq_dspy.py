#!/usr/bin/env python3
# Working Groq + DSPy Integration Test
import os
from dotenv import load_dotenv
import dspy
from groq import Groq

load_dotenv(".env")

# Custom DSPy LLM wrapper for Groq
class GroqLM(dspy.LM):
    def __init__(self, model, api_key, max_tokens=4096, temperature=0, **kwargs):
        super().__init__(model=model, **kwargs)
        self.model = model  # Explicitly set the model attribute
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

def test_groq_dspy_integration():
    """Test the Groq DSPy integration"""
    
    # Check API key
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key or api_key.startswith("gsk_your"):
        print("❌ Please set your GROQ_API_KEY in .env file")
        return False
    
    try:
        # Initialize Groq LLM with current available model
        groq_lm = GroqLM(
            model="llama-3.1-8b-instant",  # Current Groq model
            api_key=api_key,
            max_tokens=1024,
            temperature=0
        )
        
        # Configure DSPy
        dspy.settings.configure(lm=groq_lm)
        
        # Create a simple signature
        class MathQA(dspy.Signature):
            """Answer math questions accurately."""
            question = dspy.InputField()
            answer = dspy.OutputField()
        
        # Test prediction
        qa = dspy.Predict(MathQA)
        result = qa(question="What is 5 + 3?")
        
        print(f"✅ Success! Groq answered: {result.answer}")
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("Testing Groq + DSPy Integration...")
    test_groq_dspy_integration()
