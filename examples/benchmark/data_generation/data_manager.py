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


