# %%
import logging
import os
import re

logger = logging.getLogger()
logger.setLevel(logging.DEBUG)

# %%
import json
from pathlib import Path

log_regex = r"(WARNING|ERROR)\] (.+\.java):\["

def get_files_with_errors(element_lines):
    files = []
    for line in element_lines:
        match = re.search(log_regex, line)
        if match:
            path = match.group(2)
            # split off the first folder of the path
            path = path.split("/")[2:]
            files.append("/".join(path))
    return files

import dspy
from dotenv import load_dotenv
from groq import Groq

# %%
from dspy import InputField, OutputField, settings
from masterthesis.llm.types import DiffCallbackParams, DiffInfo, TokenizerType

load_dotenv(".env")

# Using Groq with current available models
language_model = "llama-3.1-8b-instant"  # Current working Groq model
# Alternative models (check Groq console for current availability):
# language_model = "mixtral-8x7b-32768"
# language_model = "gemma2-9b-it"

tokenizer_type = TokenizerType.LLAMA3_1

study_type = "dspy-baseline" 
# study_type = "full"
# study_type = "full-supplement"

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

# Setup Groq LLM
groq_client = GroqLM(
    model=language_model,
    api_key=os.getenv("GROQ_API_KEY"),
    max_tokens=4096,
    temperature=0
)

settings.configure(lm=groq_client)

language_model = language_model.replace("/", "_")

# Check if Docker is available (optional for basic functionality)
docker_available = Path("/var/run/docker.sock").exists()
if not docker_available:
    print("WARNING: Docker socket not found. Some functionality may be limited.")
    print("Please install Docker Desktop or Colima for full functionality.")

# Continue with the rest of the original script...
