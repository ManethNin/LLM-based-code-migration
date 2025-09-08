#!/usr/bin/env python3
import os
from dotenv import load_dotenv
import dspy

load_dotenv(".env")

try:
    # Test basic Groq client creation
    groq_client = dspy.GROQ(
        model="llama-3.1-70b-versatile",
        api_key=os.getenv("GROQ_API_KEY"),
        max_tokens=100,
        temperature=0
    )
    
    print("✅ Groq client created successfully")
    
    # Configure DSPy
    dspy.settings.configure(lm=groq_client)
    print("✅ DSPy configured with Groq")
    
    # Test basic signature
    class BasicQA(dspy.Signature):
        question = dspy.InputField()
        answer = dspy.OutputField()
    
    # Test prediction
    qa = dspy.Predict(BasicQA)
    result = qa(question="What is 2+2?")
    
    print(f"✅ Test successful! Answer: {result.answer}")
    
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()
