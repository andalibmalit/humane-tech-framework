"""
Configuration for the data generation pipeline.
"""

# Model configuration (with fallback support)
# OpenRouter model IDs
OPENROUTER_GENERATION_MODEL = "anthropic/claude-sonnet-4"
OPENROUTER_VALIDATION_MODEL = "x-ai/grok-4-fast:free"

# Cerebras direct API model names (fallback)
CEREBRAS_GENERATION_MODEL = "qwen-3-235b-a22b-thinking-2507"
CEREBRAS_VALIDATION_MODEL = "llama-4-maverick-17b-128e-instruct"

# Default to OpenRouter models (will fallback to Cerebras if needed)
GENERATION_MODEL = OPENROUTER_GENERATION_MODEL
VALIDATION_MODEL = OPENROUTER_VALIDATION_MODEL

# Pipeline settings
DEFAULT_BATCH_SIZE = 75
MAX_RETRIES = 3
TEMPERATURE = 0.8  # Higher for creativity in generation
VALIDATION_TEMPERATURE = 0.3  # Lower for consistent evaluation

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