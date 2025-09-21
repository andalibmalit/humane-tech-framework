"""
Data management utilities for the pipeline with semantic deduplication.
"""

import csv
import pandas as pd
import shutil
from pathlib import Path
from typing import List, Dict
from config import DATASET_PATH, BACKUP_PATH, HUMANE_PRINCIPLES
from semantic_deduplication import SemanticDeduplicator


class DataManager:
    def __init__(self, similarity_threshold: float = 0.87):
        self.dataset_path = Path(DATASET_PATH)
        self.backup_path = Path(BACKUP_PATH)
        self.deduplicator = SemanticDeduplicator(similarity_threshold=similarity_threshold)

        # Initialize deduplicator with existing scenarios
        self._initialize_deduplicator()

    def _initialize_deduplicator(self):
        """Initialize the deduplicator with existing dataset scenarios."""
        if self.dataset_path.exists():
            try:
                df = pd.read_csv(self.dataset_path)
                existing_inputs = df['input'].tolist()
                if existing_inputs:
                    print(f"Initializing deduplicator with {len(existing_inputs)} existing scenarios...")
                    self.deduplicator.update_existing_texts(existing_inputs)
                else:
                    print("No existing scenarios found in dataset")
            except Exception as e:
                print(f"Warning: Could not load existing scenarios for deduplication: {e}")

    def create_backup(self):
        """Create a backup of the current dataset."""
        if self.dataset_path.exists():
            shutil.copy2(self.dataset_path, self.backup_path)
            print(f"Backup created at {self.backup_path}")

    def append_rows(self, new_rows: List[Dict[str, str]]) -> int:
        """Append new rows to the dataset, filtering semantic duplicates."""
        if not new_rows:
            return 0

        # Extract input texts for deduplication
        new_inputs = [row['input'] for row in new_rows]

        # Filter out semantic duplicates
        unique_inputs, unique_rows = self.deduplicator.filter_duplicates(new_inputs, new_rows)

        if not unique_rows:
            print("No unique rows to add (all were semantic duplicates)")
            return 0

        # Append to CSV
        file_exists = self.dataset_path.exists()
        with open(self.dataset_path, 'a', newline='', encoding='utf-8') as csvfile:
            fieldnames = ['input', 'target', 'category', 'severity', 'principle_to_evaluate']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

            # Write header if file doesn't exist
            if not file_exists:
                writer.writeheader()

            # Write rows
            writer.writerows(unique_rows)

        print(f"Added {len(unique_rows)} unique rows to dataset")
        if len(unique_rows) < len(new_rows):
            print(f"Filtered out {len(new_rows) - len(unique_rows)} semantic duplicates")

        return len(unique_rows)

    def get_dataset_stats(self) -> Dict:
        """Get statistics about the current dataset."""
        if not self.dataset_path.exists():
            return {
                "total_rows": 0,
                "principle_distribution": {},
                "category_distribution": {},
                "deduplication_stats": self.deduplicator.get_statistics()
            }

        try:
            df = pd.read_csv(self.dataset_path)

            # Count by principle
            principle_dist = df['principle_to_evaluate'].value_counts().to_dict()

            # Count by category
            category_dist = df['category'].value_counts().to_dict()

            # Count by severity
            severity_dist = df['severity'].value_counts().to_dict()

            return {
                "total_rows": len(df),
                "principle_distribution": principle_dist,
                "category_distribution": category_dist,
                "severity_distribution": severity_dist,
                "deduplication_stats": self.deduplicator.get_statistics()
            }
        except Exception as e:
            print(f"Error getting dataset stats: {e}")
            return {
                "total_rows": 0,
                "principle_distribution": {},
                "category_distribution": {},
                "deduplication_stats": self.deduplicator.get_statistics()
            }

    def get_sample_rows(self, n: int = 3) -> List[Dict]:
        """Get a sample of recent rows for display."""
        if not self.dataset_path.exists():
            return []

        try:
            df = pd.read_csv(self.dataset_path)
            if len(df) == 0:
                return []

            # Get last n rows
            sample_df = df.tail(n)
            return sample_df.to_dict('records')
        except Exception as e:
            print(f"Error getting sample rows: {e}")
            return []

    def adjust_similarity_threshold(self, new_threshold: float):
        """Adjust the semantic similarity threshold."""
        self.deduplicator.adjust_threshold(new_threshold)
        print(f"Semantic similarity threshold adjusted to {new_threshold}")

    def clear_deduplication_cache(self):
        """Clear the semantic deduplication cache."""
        self.deduplicator.clear_cache()
        print("Semantic deduplication cache cleared")

    def get_principle_balance(self) -> Dict[str, float]:
        """Get the balance of principles in the dataset."""
        stats = self.get_dataset_stats()
        total = stats['total_rows']

        if total == 0:
            return {}

        principle_dist = stats['principle_distribution']
        return {principle: count/total for principle, count in principle_dist.items()}

    def suggest_needed_principles(self, target_balance: float = 0.167) -> List[str]:
        """Suggest which principles need more scenarios (target is ~1/6 each)."""
        balance = self.get_principle_balance()

        if not balance:
            return list(HUMANE_PRINCIPLES.keys())  # All principles needed if no data

        underrepresented = []
        for principle_key, principle_name in HUMANE_PRINCIPLES.items():
            # Check both possible naming conventions
            current_ratio = balance.get(principle_name, balance.get(principle_key, 0))
            if current_ratio < target_balance:
                underrepresented.append(principle_name)

        return underrepresented

    def get_diversity_analysis(self) -> Dict:
        """Analyze diversity patterns in existing dataset to guide generation."""
        if not self.dataset_path.exists():
            return {
                "total_scenarios": 0,
                "guidance": "No existing dataset found. Generate diverse scenarios across all categories and principles.",
                "coverage_gaps": [],
                "common_patterns": []
            }

        try:
            df = pd.read_csv(self.dataset_path)

            if len(df) == 0:
                return {
                    "total_scenarios": 0,
                    "guidance": "Empty dataset. Generate diverse scenarios across all categories and principles.",
                    "coverage_gaps": [],
                    "common_patterns": []
                }

            # Analyze input patterns for uniqueness guidance
            inputs = df['input'].tolist()

            # Extract key patterns
            common_starters = {}
            common_topics = {}

            for inp in inputs:
                # Common question starters
                starter = inp.split()[:3] if inp.split() else []
                starter_key = " ".join(starter).lower()
                common_starters[starter_key] = common_starters.get(starter_key, 0) + 1

                # Common topic keywords
                words = inp.lower().split()
                for word in words:
                    if len(word) > 4:  # Focus on meaningful words
                        common_topics[word] = common_topics.get(word, 0) + 1

            # Identify overrepresented patterns (top 20%)
            sorted_starters = sorted(common_starters.items(), key=lambda x: x[1], reverse=True)
            sorted_topics = sorted(common_topics.items(), key=lambda x: x[1], reverse=True)

            overused_starters = [starter for starter, count in sorted_starters[:max(1, len(sorted_starters)//5)] if count > 2]
            overused_topics = [topic for topic, count in sorted_topics[:max(1, len(sorted_topics)//10)] if count > 3]

            # Analyze distribution gaps
            stats = self.get_dataset_stats()

            # Find underrepresented categories
            total_rows = stats['total_rows']
            category_gaps = []
            for category, count in stats['category_distribution'].items():
                if count / total_rows < 0.12:  # Less than ~12% representation
                    category_gaps.append(category)

            # Find underrepresented principles
            principle_gaps = []
            for principle, count in stats['principle_distribution'].items():
                if count / total_rows < 0.12:  # Less than ~12% representation
                    principle_gaps.append(principle)

            # Generate guidance
            guidance_parts = []
            guidance_parts.append(f"Existing dataset has {total_rows} scenarios.")

            if overused_starters:
                guidance_parts.append(f"AVOID these overused question starters: {', '.join(overused_starters[:5])}")

            if overused_topics:
                guidance_parts.append(f"AVOID these overused topics: {', '.join(overused_topics[:8])}")

            if category_gaps:
                guidance_parts.append(f"FOCUS on underrepresented categories: {', '.join(category_gaps)}")

            if principle_gaps:
                guidance_parts.append(f"FOCUS on underrepresented principles: {', '.join(principle_gaps[:3])}")

            return {
                "total_scenarios": total_rows,
                "guidance": " ".join(guidance_parts),
                "coverage_gaps": {
                    "categories": category_gaps,
                    "principles": principle_gaps
                },
                "common_patterns": {
                    "overused_starters": overused_starters[:5],
                    "overused_topics": overused_topics[:8]
                },
                "distribution": {
                    "categories": stats['category_distribution'],
                    "principles": stats['principle_distribution']
                }
            }

        except Exception as e:
            print(f"Error analyzing diversity: {e}")
            return {
                "total_scenarios": 0,
                "guidance": "Error analyzing existing dataset. Generate diverse scenarios.",
                "coverage_gaps": [],
                "common_patterns": []
            }

    def get_deduplication_feedback(self) -> Dict:
        """Get feedback about recent deduplication patterns."""
        dedupe_stats = self.deduplicator.get_statistics()
        session_stats = dedupe_stats.get('session_stats', {})

        # Get detailed deduplication feedback
        detailed_feedback = self.deduplicator.get_deduplication_feedback()

        feedback = {
            "total_cached_scenarios": dedupe_stats.get('total_cached_texts', 0),
            "similarity_threshold": dedupe_stats.get('similarity_threshold', 0.87),
            "session_processed": session_stats.get('total_processed', 0),
            "session_duplicates": session_stats.get('total_duplicates', 0),
            "duplicate_rate": 0,
            "guidance": ""
        }

        # Calculate duplicate rate
        if feedback["session_processed"] > 0:
            feedback["duplicate_rate"] = (feedback["session_duplicates"] / feedback["session_processed"]) * 100

        # Generate comprehensive guidance
        guidance_parts = []

        # Base guidance
        if feedback["total_cached_scenarios"] > 100:
            guidance_parts.append(f"Large dataset ({feedback['total_cached_scenarios']} scenarios) requires highly unique generation.")
        elif feedback["total_cached_scenarios"] > 0:
            guidance_parts.append(f"Growing dataset ({feedback['total_cached_scenarios']} scenarios) needs diverse scenarios.")

        # Add detailed deduplication feedback
        if detailed_feedback:
            guidance_parts.append(detailed_feedback)

        # General uniqueness guidance
        if feedback["duplicate_rate"] > 60:
            guidance_parts.append("URGENT: Drastically vary vocabulary, contexts, and question structures.")
        elif feedback["duplicate_rate"] > 30:
            guidance_parts.append("Focus on novel scenarios with different angles and phrasings.")

        feedback["guidance"] = " ".join(guidance_parts) if guidance_parts else "Generate diverse scenarios."

        return feedback


