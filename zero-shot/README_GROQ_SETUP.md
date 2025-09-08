# Zero-Shot Approach Setup with Groq

This guide will help you set up and run the zero-shot approach using Groq API.

## Prerequisites

1. **Groq API Key**: Get your free API key from [https://console.groq.com/keys](https://console.groq.com/keys)
2. **Python 3.12+**: Required for this project
3. **Docker**: Required for running Java compilation tests (optional for basic testing)

## Setup Steps

### 1. Install Dependencies

```bash
cd /Users/manethninduwara/Downloads/thesis-submission/zero-shot
/Users/manethninduwara/Downloads/thesis-submission/zero-shot/.venv/bin/python -m pdm install
```

### 2. Configure API Key

Edit the `.env` file and replace the placeholder with your actual Groq API key:

```bash
# .env file
GROQ_API_KEY=gsk_your_actual_groq_api_key_here
```

### 3. Test the Setup

Run the test script to verify everything works:

```bash
/Users/manethninduwara/Downloads/thesis-submission/zero-shot/.venv/bin/python test_groq.py
```

### 4. Run the Zero-Shot Experiment

Once the test passes, run the main experiment:

```bash
/Users/manethninduwara/Downloads/thesis-submission/zero-shot/.venv/bin/python upgradellm.py
```

## Configuration

The current setup uses:
- **Model**: `llama-3.1-70b-versatile` (Groq's fastest large model)
- **Study Type**: `dspy-baseline` (basic zero-shot prompting)
- **Temperature**: 0 (deterministic outputs)

### Alternative Groq Models

You can modify `upgradellm.py` to use different Groq models:

```python
# Fast inference, good quality
language_model = "llama-3.1-70b-versatile"

# Fastest inference, smaller model  
language_model = "llama-3.1-8b-instant"

# Good for reasoning tasks
language_model = "mixtral-8x7b-32768"

# Google's Gemma model
language_model = "gemma2-9b-it"
```

## What the Experiment Does

1. **Loads Dataset**: Processes Java projects with dependency breaking changes
2. **LLM Processing**: Uses Groq to generate fixes for compilation errors
3. **Evaluation**: Tests the generated fixes against actual compilation
4. **Results Storage**: Saves results in SQLite database for analysis

## Output

Results are stored in:
- `pipeline_llama-3.1-70b-versatile.db` - SQLite database with experiment results
- Console output showing progress and statistics

## Troubleshooting

### Common Issues

1. **API Key Error**: Make sure your Groq API key is correctly set in `.env`
2. **Import Errors**: Run `pdm install` to ensure all dependencies are installed
3. **Docker Warning**: Install Docker Desktop or Colima for full functionality
4. **Memory Issues**: Use smaller models like `llama-3.1-8b-instant` for resource-constrained systems

### Docker Setup (Optional)

For full functionality, install Docker:

**macOS**:
```bash
# Using Homebrew
brew install --cask docker

# Or install Colima (lightweight alternative)
brew install colima
colima start
```

## Results Analysis

After running the experiment, use the Jupyter notebooks to analyze results:

```bash
/Users/manethninduwara/Downloads/thesis-submission/zero-shot/.venv/bin/python -m jupyter notebook
```

Open `dspy-trace-analysis.ipynb` for detailed analysis.
