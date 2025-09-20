"""
Semantic similarity-based deduplication using sentence transformers.
"""

import numpy as np
import pickle
from pathlib import Path
from typing import List, Set, Tuple
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity


class SemanticDeduplicator:
    def __init__(self,
                 model_name: str = "sentence-transformers/all-MiniLM-L6-v2",
                 similarity_threshold: float = 0.87,
                 cache_dir: str = None):
        """
        Initialize semantic deduplicator.

        Args:
            model_name: Sentence transformer model to use
            similarity_threshold: Cosine similarity threshold for duplicates (0-1)
            cache_dir: Directory to cache embeddings
        """
        self.model = SentenceTransformer(model_name)
        self.similarity_threshold = similarity_threshold

        # Setup cache directory
        if cache_dir is None:
            cache_dir = Path(__file__).parent / "embeddings_cache"
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(exist_ok=True)

        # Cache file paths
        self.embeddings_cache_file = self.cache_dir / "existing_embeddings.pkl"
        self.texts_cache_file = self.cache_dir / "existing_texts.pkl"

        # Load existing embeddings and texts
        self.existing_embeddings, self.existing_texts = self._load_cache()

    def _load_cache(self) -> Tuple[np.ndarray, List[str]]:
        """Load cached embeddings and texts."""
        try:
            if self.embeddings_cache_file.exists() and self.texts_cache_file.exists():
                with open(self.embeddings_cache_file, 'rb') as f:
                    embeddings = pickle.load(f)
                with open(self.texts_cache_file, 'rb') as f:
                    texts = pickle.load(f)
                print(f"Loaded {len(texts)} cached embeddings")
                return embeddings, texts
        except Exception as e:
            print(f"Warning: Could not load cached embeddings: {e}")

        return np.array([]), []

    def _save_cache(self):
        """Save embeddings and texts to cache."""
        try:
            with open(self.embeddings_cache_file, 'wb') as f:
                pickle.dump(self.existing_embeddings, f)
            with open(self.texts_cache_file, 'wb') as f:
                pickle.dump(self.existing_texts, f)
        except Exception as e:
            print(f"Warning: Could not save cache: {e}")

    def update_existing_texts(self, texts: List[str]):
        """Update the cache with new existing texts."""
        if not texts:
            return

        print(f"Computing embeddings for {len(texts)} existing texts...")
        new_embeddings = self.model.encode(texts, show_progress_bar=True)

        if len(self.existing_embeddings) == 0:
            self.existing_embeddings = new_embeddings
            self.existing_texts = texts
        else:
            # Append new embeddings
            self.existing_embeddings = np.vstack([self.existing_embeddings, new_embeddings])
            self.existing_texts.extend(texts)

        # Save to cache
        self._save_cache()
        print(f"Cache updated with {len(self.existing_texts)} total texts")

    def find_duplicates(self, new_texts: List[str]) -> Tuple[List[int], List[float]]:
        """
        Find duplicates among new texts compared to existing texts.

        Args:
            new_texts: List of new text scenarios to check

        Returns:
            Tuple of (duplicate_indices, similarity_scores)
        """
        if not new_texts or len(self.existing_embeddings) == 0:
            return [], []

        print(f"Computing embeddings for {len(new_texts)} new texts...")
        new_embeddings = self.model.encode(new_texts, show_progress_bar=True)

        print("Computing semantic similarities...")
        duplicate_indices = []
        similarity_scores = []

        for i, new_embedding in enumerate(new_embeddings):
            # Compute cosine similarity with all existing embeddings
            similarities = cosine_similarity([new_embedding], self.existing_embeddings)[0]
            max_similarity = np.max(similarities)

            if max_similarity >= self.similarity_threshold:
                duplicate_indices.append(i)
                similarity_scores.append(max_similarity)

                # Find the most similar existing text for logging
                most_similar_idx = np.argmax(similarities)
                most_similar_text = self.existing_texts[most_similar_idx]
                print(f"  Duplicate found (similarity: {max_similarity:.3f}):")
                print(f"    New: {new_texts[i][:100]}...")
                print(f"    Existing: {most_similar_text[:100]}...")

        return duplicate_indices, similarity_scores

    def filter_duplicates(self, new_texts: List[str],
                         new_data: List[dict] = None) -> Tuple[List[str], List[dict]]:
        """
        Filter out duplicate texts and optionally associated data.

        Args:
            new_texts: List of new text scenarios
            new_data: Optional list of data dictionaries corresponding to texts

        Returns:
            Tuple of (unique_texts, unique_data)
        """
        duplicate_indices, similarities = self.find_duplicates(new_texts)

        if not duplicate_indices:
            print("No semantic duplicates found!")
            return new_texts, new_data if new_data else []

        print(f"Found {len(duplicate_indices)} semantic duplicates")

        # Create set of duplicate indices for efficient lookup
        duplicate_set = set(duplicate_indices)

        # Filter texts
        unique_texts = [text for i, text in enumerate(new_texts)
                       if i not in duplicate_set]

        # Filter data if provided
        unique_data = []
        if new_data:
            unique_data = [data for i, data in enumerate(new_data)
                          if i not in duplicate_set]

        # Update cache with unique texts
        if unique_texts:
            self.update_existing_texts(unique_texts)

        print(f"Kept {len(unique_texts)} unique texts out of {len(new_texts)} total")
        return unique_texts, unique_data

    def get_statistics(self) -> dict:
        """Get statistics about the deduplication cache."""
        return {
            "total_cached_texts": len(self.existing_texts),
            "similarity_threshold": self.similarity_threshold,
            "model_name": self.model.get_sentence_embedding_dimension(),
            "cache_files_exist": {
                "embeddings": self.embeddings_cache_file.exists(),
                "texts": self.texts_cache_file.exists()
            }
        }

    def clear_cache(self):
        """Clear the embeddings cache."""
        if self.embeddings_cache_file.exists():
            self.embeddings_cache_file.unlink()
        if self.texts_cache_file.exists():
            self.texts_cache_file.unlink()

        self.existing_embeddings = np.array([])
        self.existing_texts = []
        print("Cache cleared")

    def adjust_threshold(self, new_threshold: float):
        """Adjust the similarity threshold."""
        self.similarity_threshold = new_threshold
        print(f"Similarity threshold updated to {new_threshold}")