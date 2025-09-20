"""
Main pipeline controller for data generation.
"""

import os
import sys
from pathlib import Path
from typing import List, Dict, Optional
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Add the current directory to Python path for imports
sys.path.append(str(Path(__file__).parent))

from generators import ScenarioGenerator
from validators import ScenarioValidator
from data_manager import DataManager
from config import DEFAULT_BATCH_SIZE


class DataGenerationPipeline:
    def __init__(self, api_key: Optional[str] = None, similarity_threshold: float = 0.87):
        """Initialize the data generation pipeline."""
        self.generator = ScenarioGenerator(api_key)
        self.validator = ScenarioValidator(api_key)
        self.data_manager = DataManager(similarity_threshold)

        print("🚀 Data Generation Pipeline Initialized")
        print(f"📊 Current dataset: {self.data_manager.get_dataset_stats()['total_rows']} rows")

    def run_interactive(self):
        """Run the pipeline in interactive mode."""
        print("\n" + "="*60)
        print("🎯 HUMANE TECH BENCHMARK DATA GENERATION PIPELINE")
        print("="*60)

        # Show current dataset statistics
        self._show_dataset_stats()

        batch_size = DEFAULT_BATCH_SIZE
        user_context = ""

        while True:
            print(f"\n📝 Ready to generate {batch_size} scenarios")
            print("💡 Current context:", user_context if user_context else "None")

            # Check for stop command
            user_input = input("\nPress Enter to continue, or provide context/commands: ").strip()

            if "STOP GENERATION" in user_input.upper():
                print("\n🛑 Generation stopped by user")
                break

            # Update context if provided
            if user_input and "STOP GENERATION" not in user_input.upper():
                user_context = user_input
                print(f"📝 Context updated: {user_context}")

            # Generate scenarios
            print(f"\n🔄 Generating {batch_size} scenarios...")
            scenarios = self.generator.generate_batch(
                batch_size=batch_size,
                context=user_context
            )

            if not scenarios:
                print("❌ No scenarios generated. Check your API key and model availability.")
                continue

            # Validate scenarios
            print(f"\n🔍 Validating {len(scenarios)} scenarios...")
            approved_scenarios, validation_reports = self.validator.validate_batch(scenarios)

            # Show validation summary
            validation_summary = self.validator.get_validation_summary(validation_reports)
            self._show_validation_summary(validation_summary)

            if not approved_scenarios:
                print("❌ No scenarios passed validation. Continuing to next batch...")
                continue

            # Add to dataset (with semantic deduplication)
            print(f"\n💾 Adding {len(approved_scenarios)} approved scenarios to dataset...")
            added_count = self.data_manager.append_rows(approved_scenarios)

            # Show results
            print(f"\n✅ Added {added_count} unique scenarios to dataset")

            # Show sample of what was added
            if added_count > 0:
                self._show_sample_scenarios(approved_scenarios[:3])

            # Show updated dataset stats
            self._show_dataset_stats()

            print("\n" + "-"*60)

        print("\n🎉 Pipeline completed!")
        self._show_final_summary()

    def run_batch(self,
                  total_scenarios: int,
                  batch_size: int = None,
                  context: str = "",
                  auto_approve: bool = False) -> Dict:
        """
        Run the pipeline in batch mode for a specific number of scenarios.

        Args:
            total_scenarios: Total number of scenarios to generate
            batch_size: Size of each batch (default from config)
            context: Generation context
            auto_approve: If True, skip validation (use with caution)

        Returns:
            Summary statistics
        """
        if batch_size is None:
            batch_size = DEFAULT_BATCH_SIZE

        print(f"🚀 Running batch mode: {total_scenarios} scenarios in batches of {batch_size}")

        total_generated = 0
        total_added = 0
        all_validation_reports = []

        batches = (total_scenarios + batch_size - 1) // batch_size  # Ceiling division

        for batch_num in range(batches):
            current_batch_size = min(batch_size, total_scenarios - total_generated)

            print(f"\n📦 Batch {batch_num + 1}/{batches}: Generating {current_batch_size} scenarios")

            # Generate
            scenarios = self.generator.generate_batch(
                batch_size=current_batch_size,
                context=context
            )

            if not scenarios:
                print(f"❌ Batch {batch_num + 1} failed to generate scenarios")
                continue

            total_generated += len(scenarios)

            # Validate (unless auto-approve is enabled)
            if auto_approve:
                approved_scenarios = scenarios
                validation_reports = []
            else:
                approved_scenarios, validation_reports = self.validator.validate_batch(scenarios)
                all_validation_reports.extend(validation_reports)

            # Add to dataset
            if approved_scenarios:
                added_count = self.data_manager.append_rows(approved_scenarios)
                total_added += added_count
                print(f"✅ Batch {batch_num + 1}: Added {added_count} scenarios")

        # Final summary
        final_stats = {
            "total_generated": total_generated,
            "total_added": total_added,
            "validation_summary": self.validator.get_validation_summary(all_validation_reports) if all_validation_reports else {},
            "final_dataset_stats": self.data_manager.get_dataset_stats()
        }

        print(f"\n🎉 Batch mode completed!")
        print(f"📊 Generated: {total_generated}, Added: {total_added}")

        return final_stats

    def _show_dataset_stats(self):
        """Display current dataset statistics."""
        stats = self.data_manager.get_dataset_stats()
        print(f"\n📊 CURRENT DATASET STATS:")
        print(f"   Total rows: {stats['total_rows']}")

        if stats['principle_distribution']:
            print(f"   Principle distribution:")
            for principle, count in stats['principle_distribution'].items():
                percentage = (count / stats['total_rows']) * 100 if stats['total_rows'] > 0 else 0
                print(f"     • {principle}: {count} ({percentage:.1f}%)")

    def _show_validation_summary(self, summary: Dict):
        """Display validation summary."""
        if not summary:
            return

        print(f"\n🔍 VALIDATION SUMMARY:")
        print(f"   Approved: {summary['approved_count']}/{summary['total_scenarios']} ({summary['approval_rate']:.1%})")
        print(f"   Average score: {summary['average_score']:.1f}/100")

        if summary['rejection_reasons']:
            print(f"   Top rejection reasons:")
            for reason, count in list(summary['rejection_reasons'].items())[:3]:
                print(f"     • {reason}: {count}")

    def _show_sample_scenarios(self, scenarios: List[Dict]):
        """Display sample scenarios."""
        print(f"\n📝 SAMPLE SCENARIOS ADDED:")
        for i, scenario in enumerate(scenarios, 1):
            print(f"   {i}. Input: {scenario['input'][:80]}...")
            print(f"      Category: {scenario['category']}")
            print(f"      Principle: {scenario['principle_to_evaluate']}")

    def _show_final_summary(self):
        """Display final pipeline summary."""
        stats = self.data_manager.get_dataset_stats()
        dedup_stats = stats.get('deduplication_stats', {})

        print(f"\n📈 FINAL SUMMARY:")
        print(f"   Final dataset size: {stats['total_rows']} rows")
        print(f"   Semantic similarity threshold: {dedup_stats.get('similarity_threshold', 'N/A')}")
        print(f"   Cached embeddings: {dedup_stats.get('total_cached_texts', 'N/A')}")


def main():
    """Main entry point for the pipeline."""
    # Check for environment variables
    if not os.getenv("OPENROUTER_API_KEY"):
        print("❌ Error: OPENROUTER_API_KEY environment variable not set")
        print("   Please set your OpenRouter API key:")
        print("   export OPENROUTER_API_KEY='your-api-key-here'")
        return

    try:
        pipeline = DataGenerationPipeline()
        pipeline.run_interactive()

    except KeyboardInterrupt:
        print("\n\n🛑 Pipeline interrupted by user")
    except Exception as e:
        print(f"\n❌ Pipeline error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()