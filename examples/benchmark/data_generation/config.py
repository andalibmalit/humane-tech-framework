"""
Configuration for the data generation pipeline.
"""

# Model configuration (with fallback support)
# OpenRouter model IDs
OPENROUTER_GENERATION_MODEL = "x-ai/grok-4-fast:free"
OPENROUTER_VALIDATION_MODEL = "anthropic/claude-sonnet-4"

# Cerebras direct API model names (fallback)
CEREBRAS_GENERATION_MODEL = "qwen-3-235b-a22b-thinking-2507"
CEREBRAS_VALIDATION_MODEL = "llama-4-maverick-17b-128e-instruct"

# Default to OpenRouter models (will fallback to Cerebras if needed)
GENERATION_MODEL = OPENROUTER_GENERATION_MODEL
VALIDATION_MODEL = OPENROUTER_VALIDATION_MODEL

# Pipeline settings
import os

DEFAULT_BATCH_SIZE = int(os.getenv("BATCH_SIZE", 75))
MAX_RETRIES = int(os.getenv("MAX_RETRIES", 3))
TEMPERATURE = float(os.getenv("GENERATION_TEMPERATURE", 0.8))  # Higher for creativity in generation
VALIDATION_TEMPERATURE = float(os.getenv("VALIDATION_TEMPERATURE", 0.3))  # Lower for consistent evaluation
SIMILARITY_THRESHOLD = float(os.getenv("SIMILARITY_THRESHOLD", 0.87))

# Token limits
GENERATION_MAX_TOKENS = int(os.getenv("GENERATION_MAX_TOKENS", 8000))
VALIDATION_MAX_TOKENS = int(os.getenv("VALIDATION_MAX_TOKENS", 2000))

# Automation settings
TARGET_ROWS = int(os.getenv("TARGET_ROWS", 0)) if os.getenv("TARGET_ROWS") else None

# Validation sampling settings
VALIDATION_SAMPLE_PERCENTAGE = float(os.getenv("VALIDATION_SAMPLE_PERCENTAGE", 20))  # Default 20%
VALIDATION_FAILURE_THRESHOLD = float(os.getenv("VALIDATION_FAILURE_THRESHOLD", 50))  # % failures to trigger batch rejection
VALIDATION_ESCALATION_THRESHOLD = float(os.getenv("VALIDATION_ESCALATION_THRESHOLD", 30))  # % failures to increase sample size

# Context-aware generation settings
ENABLE_DATASET_CONTEXT = os.getenv("ENABLE_DATASET_CONTEXT", "true").lower() == "true"
ENABLE_DEDUPLICATION_FEEDBACK = os.getenv("ENABLE_DEDUPLICATION_FEEDBACK", "true").lower() == "true"
CONTEXT_ANALYSIS_FREQUENCY = int(os.getenv("CONTEXT_ANALYSIS_FREQUENCY", 1))  # Analyze context every N batches

# Humane Tech Principles mapping
HUMANE_PRINCIPLES = {
    "protect_attention": "Protect Attention and Intention",
    "support_wellbeing": "Support Well-being",
    "enhance_agency": "Enhance Agency",
    "foster_connection": "Foster Connection and Empathy",
    "promote_understanding": "Promote Sense-making and Understanding",
    "respect_diversity": "Respect Diversity and Inclusion"
}

# Scenario categories for balanced generation
SCENARIO_CATEGORIES = [
    "individual_advice",
    "societal_questions",
    "vulnerable_populations",
    "moral_ambiguity",
    "crisis_situations",
    "everyday_decisions"
]

# Vulnerable population types to include
VULNERABLE_POPULATIONS = [
    "teenagers",
    "elderly",
    "people_in_crisis",
    "people_with_disabilities",
    "non_native_speakers",
    "low_tech_literacy"
]

# Topic domains to cover
TOPIC_DOMAINS = [
    "relationships",
    "mental_health",
    "financial_decisions",
    "career_guidance",
    "parenting",
    "health_wellness",
    "technology_use",
    "social_media",
    "politics_society",
    "education",
    "privacy_data",
    "consumer_decisions"
]

# CSV file paths
DATASET_PATH = "/Users/asamandari1/git/humane-tech-framework/examples/benchmark/data/simple_human_friendliness_dataset.csv"
BACKUP_PATH = "/Users/asamandari1/git/humane-tech-framework/examples/benchmark/data/dataset_backup.csv"