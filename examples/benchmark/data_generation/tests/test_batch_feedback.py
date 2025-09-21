"""
Tests for batch feedback generation in validators.py.
"""

import pytest
from unittest.mock import Mock, patch
from validators import ScenarioValidator


class TestBatchFeedbackGeneration:
    """Test batch feedback generation functionality."""

    @pytest.fixture
    def validator(self):
        """Create a ScenarioValidator instance for testing."""
        with patch('validators.FallbackLLMClient') as mock_client:
            mock_client.return_value.get_available_apis.return_value = ['OpenRouter']
            validator = ScenarioValidator()
            validator.client = mock_client.return_value
            return validator

    @pytest.fixture
    def failure_reports_realism(self):
        """Sample failure reports focused on realism issues."""
        return [
            {
                'reason': 'scenario lacks realism and believable context',
                'score': 25,
                'scenario': {'input': 'test1'}
            },
            {
                'reason': 'unrealistic user interaction, not believable',
                'score': 30,
                'scenario': {'input': 'test2'}
            },
            {
                'reason': 'this scenario is not realistic enough for evaluation',
                'score': 35,
                'scenario': {'input': 'test3'}
            }
        ]

    @pytest.fixture
    def failure_reports_principle_alignment(self):
        """Sample failure reports focused on principle alignment issues."""
        return [
            {
                'reason': 'weak principle alignment with stated evaluation criteria',
                'score': 40,
                'scenario': {'input': 'test1'}
            },
            {
                'reason': 'principle selection seems arbitrary and misaligned',
                'score': 45,
                'scenario': {'input': 'test2'}
            },
            {
                'reason': 'no clear alignment between scenario and principle',
                'score': 35,
                'scenario': {'input': 'test3'}
            }
        ]

    @pytest.fixture
    def failure_reports_diversity(self):
        """Sample failure reports focused on diversity issues."""
        return [
            {
                'reason': 'lacks diversity in context and population representation',
                'score': 30,
                'scenario': {'input': 'test1'}
            },
            {
                'reason': 'not unique enough, similar to existing scenarios',
                'score': 25,
                'scenario': {'input': 'test2'}
            },
            {
                'reason': 'diversity coverage is insufficient for evaluation',
                'score': 35,
                'scenario': {'input': 'test3'}
            }
        ]

    @pytest.fixture
    def failure_reports_evaluation_utility(self):
        """Sample failure reports focused on evaluation utility issues."""
        return [
            {
                'reason': 'limited evaluation utility for benchmarking purposes',
                'score': 40,
                'scenario': {'input': 'test1'}
            },
            {
                'reason': 'utility for assessment is questionable and unclear',
                'score': 30,
                'scenario': {'input': 'test2'}
            },
            {
                'reason': 'evaluation criteria cannot be properly measured',
                'score': 35,
                'scenario': {'input': 'test3'}
            }
        ]

    @pytest.fixture
    def mixed_failure_reports(self):
        """Mixed failure reports with various issues."""
        return [
            {
                'reason': 'realism issues and weak principle alignment',
                'score': 20,
                'scenario': {'input': 'test1'}
            },
            {
                'reason': 'evaluation utility is poor, lacks diversity',
                'score': 25,
                'scenario': {'input': 'test2'}
            },
            {
                'reason': 'multiple problems: not realistic, no clear evaluation path',
                'score': 15,
                'scenario': {'input': 'test3'}
            },
            {
                'reason': 'good principle alignment but lacks realism',
                'score': 55,
                'scenario': {'input': 'test4'}
            }
        ]

    def test_generate_batch_feedback_no_failures(self, validator):
        """Test feedback generation with no failures."""
        feedback = validator._generate_batch_feedback([], [])
        assert feedback is None

    def test_generate_batch_feedback_realism_issues(self, validator, failure_reports_realism):
        """Test feedback generation for realism-focused failures."""
        scenarios = [{'input': f'test{i}'} for i in range(1, 4)]
        feedback = validator._generate_batch_feedback(failure_reports_realism, scenarios)

        assert feedback is not None
        assert 'realism' in feedback.lower()
        assert 'believable' in feedback.lower() or 'realistic' in feedback.lower()
        assert 'specific details' in feedback.lower() or 'context' in feedback.lower()

    def test_generate_batch_feedback_principle_alignment_issues(self, validator, failure_reports_principle_alignment):
        """Test feedback generation for principle alignment failures."""
        scenarios = [{'input': f'test{i}'} for i in range(1, 4)]
        feedback = validator._generate_batch_feedback(failure_reports_principle_alignment, scenarios)

        assert feedback is not None
        assert 'principle' in feedback.lower()
        assert 'alignment' in feedback.lower()
        assert 'clear connection' in feedback.lower() or 'appropriate principle' in feedback.lower()

    def test_generate_batch_feedback_diversity_issues(self, validator, failure_reports_diversity):
        """Test feedback generation for diversity failures."""
        scenarios = [{'input': f'test{i}'} for i in range(1, 4)]
        feedback = validator._generate_batch_feedback(failure_reports_diversity, scenarios)

        assert feedback is not None
        assert 'diversity' in feedback.lower() or 'unique' in feedback.lower()
        assert 'different' in feedback.lower() or 'varied' in feedback.lower()

    def test_generate_batch_feedback_evaluation_utility_issues(self, validator, failure_reports_evaluation_utility):
        """Test feedback generation for evaluation utility failures."""
        scenarios = [{'input': f'test{i}'} for i in range(1, 4)]
        feedback = validator._generate_batch_feedback(failure_reports_evaluation_utility, scenarios)

        assert feedback is not None
        assert 'evaluation' in feedback.lower() or 'utility' in feedback.lower()
        assert 'measurable' in feedback.lower() or 'assessment' in feedback.lower()

    def test_generate_batch_feedback_mixed_issues(self, validator, mixed_failure_reports):
        """Test feedback generation for mixed failure types."""
        scenarios = [{'input': f'test{i}'} for i in range(1, 5)]
        feedback = validator._generate_batch_feedback(mixed_failure_reports, scenarios)

        assert feedback is not None
        # Should address the most common issues
        feedback_lower = feedback.lower()
        issue_keywords = ['realism', 'principle', 'evaluation', 'diversity']
        found_keywords = [kw for kw in issue_keywords if kw in feedback_lower]
        assert len(found_keywords) >= 2  # Should address multiple issue types

    def test_generate_batch_feedback_low_scores(self, validator):
        """Test feedback generation emphasizes low scores."""
        low_score_failures = [
            {'reason': 'various issues', 'score': 10, 'scenario': {'input': 'test1'}},
            {'reason': 'more issues', 'score': 15, 'scenario': {'input': 'test2'}},
            {'reason': 'serious problems', 'score': 20, 'scenario': {'input': 'test3'}},
        ]
        scenarios = [{'input': f'test{i}'} for i in range(1, 4)]
        feedback = validator._generate_batch_feedback(low_score_failures, scenarios)

        assert feedback is not None
        feedback_lower = feedback.lower()
        assert 'low' in feedback_lower or 'poor' in feedback_lower or 'quality' in feedback_lower

    def test_generate_batch_feedback_pattern_analysis(self, validator):
        """Test that feedback analyzes patterns correctly."""
        # Create failures with clear patterns
        pattern_failures = [
            {'reason': 'realism and believability issues here', 'score': 30, 'scenario': {'input': 'test1'}},
            {'reason': 'realism problems in this scenario too', 'score': 25, 'scenario': {'input': 'test2'}},
            {'reason': 'realistic context is missing entirely', 'score': 20, 'scenario': {'input': 'test3'}},
            {'reason': 'unrelated issue about formatting', 'score': 45, 'scenario': {'input': 'test4'}},
        ]
        scenarios = [{'input': f'test{i}'} for i in range(1, 5)]
        feedback = validator._generate_batch_feedback(pattern_failures, scenarios)

        assert feedback is not None
        # Should identify realism as the primary pattern (3 out of 4 failures)
        assert 'realism' in feedback.lower()

    def test_generate_batch_feedback_comprehensive_structure(self, validator, mixed_failure_reports):
        """Test that feedback has comprehensive structure."""
        scenarios = [{'input': f'test{i}'} for i in range(1, 5)]
        feedback = validator._generate_batch_feedback(mixed_failure_reports, scenarios)

        assert feedback is not None
        assert len(feedback) > 50  # Should be substantial feedback

        # Should contain actionable guidance
        feedback_lower = feedback.lower()
        actionable_keywords = ['ensure', 'add', 'improve', 'focus', 'include', 'create', 'make']
        found_actionable = [kw for kw in actionable_keywords if kw in feedback_lower]
        assert len(found_actionable) >= 1  # Should have actionable suggestions

    def test_generate_batch_feedback_edge_cases(self, validator):
        """Test feedback generation edge cases."""
        # Empty reason strings
        empty_failures = [
            {'reason': '', 'score': 30, 'scenario': {'input': 'test1'}},
            {'reason': None, 'score': 25, 'scenario': {'input': 'test2'}},
        ]
        scenarios = [{'input': 'test1'}, {'input': 'test2'}]
        feedback = validator._generate_batch_feedback(empty_failures, scenarios)

        # Should handle gracefully and still provide some feedback
        assert feedback is None or len(feedback) > 10

    def test_generate_batch_feedback_score_categorization(self, validator):
        """Test that feedback correctly categorizes scores."""
        score_range_failures = [
            {'reason': 'test issue 1', 'score': 10, 'scenario': {'input': 'test1'}},   # Very low
            {'reason': 'test issue 2', 'score': 35, 'scenario': {'input': 'test2'}},   # Low
            {'reason': 'test issue 3', 'score': 55, 'scenario': {'input': 'test3'}},   # Medium-low
            {'reason': 'test issue 4', 'score': 45, 'scenario': {'input': 'test4'}},   # Below threshold
        ]
        scenarios = [{'input': f'test{i}'} for i in range(1, 5)]
        feedback = validator._generate_batch_feedback(score_range_failures, scenarios)

        assert feedback is not None
        # All scores are below 65 threshold, so should mention quality improvements needed
        feedback_lower = feedback.lower()
        quality_keywords = ['quality', 'improve', 'better', 'enhance', 'strengthen']
        found_quality = [kw for kw in quality_keywords if kw in feedback_lower]
        assert len(found_quality) >= 1

    def test_generate_batch_feedback_keyword_extraction(self, validator):
        """Test that keyword extraction works correctly."""
        keyword_test_failures = [
            {'reason': 'The REALISM of this scenario is questionable', 'score': 30, 'scenario': {'input': 'test1'}},
            {'reason': 'PRINCIPLE alignment needs significant work', 'score': 35, 'scenario': {'input': 'test2'}},
            {'reason': 'DIVERSITY and coverage are lacking', 'score': 25, 'scenario': {'input': 'test3'}},
            {'reason': 'EVALUATION utility is minimal', 'score': 40, 'scenario': {'input': 'test4'}},
        ]
        scenarios = [{'input': f'test{i}'} for i in range(1, 5)]
        feedback = validator._generate_batch_feedback(keyword_test_failures, scenarios)

        assert feedback is not None
        feedback_lower = feedback.lower()

        # Should identify multiple issue categories
        categories = ['realism', 'principle', 'diversity', 'evaluation']
        found_categories = [cat for cat in categories if cat in feedback_lower]
        assert len(found_categories) >= 3  # Should catch most categories