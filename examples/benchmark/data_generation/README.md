# Humane Tech Benchmark Data Generation Pipeline

This pipeline generates high-quality evaluation scenarios for testing AI assistants' adherence to humane technology principles.

## Features

- **LLM-Assisted Generation**: Uses Claude Sonnet 4 for creative scenario generation
- **Intelligent Validation**: Uses Grok 4 Fast (free) with web search for quality assessment
- **API Fallback**: OpenRouter first, falls back to Cerebras direct API for free tier usage
- **Semantic Deduplication**: Prevents duplicate scenarios using sentence transformers (87% similarity threshold)
- **Interactive Mode**: Generate in batches with user feedback between iterations
- **Principle-Aware**: Prioritizes existing evaluation categories while maintaining diversity

⚠️ **Important**: Web search for validation is only available through OpenRouter. Cerebras fallback provides a generous free tier but without web research capabilities.

## Setup

1. **Install Dependencies**
   ```bash
   cd examples/benchmark
   pip install -r requirements.txt
   ```

2. **Set API Key**
   ```bash
   # Copy template and add your OpenRouter API key
   cp data_generation/.env.template data_generation/.env
   # Edit .env file with your API key
   ```

3. **Get OpenRouter API Key**
   - Sign up at [OpenRouter](https://openrouter.ai/)
   - Generate an API key
   - Add it to your `.env` file

## Usage

### Interactive Mode (Recommended)
```bash
cd data_generation
python pipeline.py
```

This will:
- Generate 75 scenarios per batch (default)
- Validate each scenario for quality
- Filter semantic duplicates
- Append unique scenarios to your CSV
- Wait for your input between batches

### Programmatic Usage
```python
from pipeline import DataGenerationPipeline

# Initialize pipeline
pipeline = DataGenerationPipeline()

# Generate 200 scenarios in batch mode
results = pipeline.run_batch(
    total_scenarios=200,
    context="Focus on scenarios involving elderly users"
)

# Or run specific batch
scenarios = pipeline.generator.generate_batch(
    batch_size=50,
    context="Generate scenarios about social media and mental health"
)
```

## Pipeline Flow

```
User Input → Generation (Claude) → Validation (Grok+Web) → Deduplication → CSV Append
     ↑                                                                             ↓
     └──────────────── User feedback/context injection ←─────────────────────────┘
```

## Evaluation Categories

The pipeline prioritizes these existing evaluation categories:

- **Fostering Meaningful Connection**
- **Psychological Safety and Emotional Well-Being**
- **User Autonomy and Freedom from Manipulation**
- **Transparency and Explainability**
- **Trustworthiness and Reliability**
- **Fairness and Inclusivity**
- **Privacy and Data Rights**
- **Accountability and Human Oversight**
- **Ethical Alignment and Moral Integrity**
- **Human Well-Being and Flourishing**
- **Crisis Response and Emergency Situations**

## Configuration

Key settings in `config.py`:
- `GENERATION_MODEL`: Default Claude Sonnet 4
- `VALIDATION_MODEL`: Default Grok 4 Fast (free)
- `DEFAULT_BATCH_SIZE`: 75 scenarios per batch
- `TEMPERATURE`: 0.8 for generation, 0.3 for validation
- Similarity threshold: 0.87 for deduplication

## Output Format

Each scenario includes:
- `input`: Human's question/situation
- `target`: Ideal humane response approach
- `category`: Situation type (e.g., "Mental Health & Crisis")
- `severity`: Impact level (low/medium/high/critical)
- `principle_to_evaluate`: Evaluation category from list above

## Quality Assurance

The validation engine evaluates scenarios on:
1. **Realism & Relevance** (0-25 points)
2. **Evaluation Utility** (0-25 points)
3. **Principle Alignment** (0-25 points)
4. **Diversity & Coverage** (0-25 points)

Scenarios scoring 65+ are approved for inclusion.

## Commands During Interactive Mode

- **Press Enter**: Continue with current settings
- **Type context**: Provide guidance for next batch (e.g., "more scenarios for teenagers")
- **Type "STOP GENERATION"**: End the session

## Troubleshooting

- **API Errors**: Check your OpenRouter API key and credit balance
- **Import Errors**: Ensure all requirements are installed
- **Validation Failures**: The validator uses web search; network issues may cause failures
- **Memory Issues**: Large batches may require more RAM for embeddings

## Files

- `pipeline.py`: Main controller script
- `generators.py`: Scenario generation engine
- `validators.py`: Quality validation engine
- `data_manager.py`: CSV handling and statistics
- `semantic_deduplication.py`: Similarity-based duplicate detection
- `config.py`: Configuration settings