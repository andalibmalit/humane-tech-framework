"""
Tests for validation response parsing in validators.py.
"""

import pytest
from unittest.mock import Mock, patch
from validators import ScenarioValidator


class TestValidationResponseParsing:
    """Test validation response parsing functionality."""

    @pytest.fixture
    def validator(self):
        """Create a ScenarioValidator instance for testing."""
        with patch('validators.FallbackLLMClient') as mock_client:
            mock_client.return_value.get_available_apis.return_value = ['OpenRouter']
            validator = ScenarioValidator()
            validator.client = mock_client.return_value
            return validator

    def test_parse_validation_result_approved(self, validator, sample_scenario, sample_web_context, mock_validation_response_approved):
        """Test parsing of approved validation response."""
        is_approved, report = validator._parse_validation_result(
            mock_validation_response_approved, sample_scenario, sample_web_context
        )

        assert is_approved == True
        assert report['approved'] == True
        assert report['score'] == 85
        assert len(report['reason']) > 100  # Should capture multi-line reasoning
        assert 'demonstrates strong alignment' in report['reason']
        assert 'REALISM & RELEVANCE' in report['reason']
        assert 'EVALUATION UTILITY' in report['reason']
        assert len(report['suggestions']) > 50  # Should capture suggestions
        assert 'demographic context' in report['suggestions']

    def test_parse_validation_result_rejected(self, validator, sample_scenario, sample_web_context, mock_validation_response_rejected):
        """Test parsing of rejected validation response."""
        is_approved, report = validator._parse_validation_result(
            mock_validation_response_rejected, sample_scenario, sample_web_context
        )

        assert is_approved == False
        assert report['approved'] == False
        assert report['score'] == 35
        assert len(report['reason']) > 200  # Should capture multi-line reasoning/suggestions
        assert 'fails multiple critical' in report['reason']
        assert 'CRITICAL ISSUES' in report['reason']
        assert len(report['suggestions']) > 100  # Should capture detailed suggestions
        assert 'Rewrite with specific situation' in report['suggestions']

    def test_parse_validation_minimal_response(self, validator, sample_scenario, sample_web_context):
        """Test parsing minimal validation response."""
        minimal_response = """APPROVED: NO
SCORE: 40/100
REASONING: Below threshold
SUGGESTIONS: Improve quality"""

        is_approved, report = validator._parse_validation_result(
            minimal_response, sample_scenario, sample_web_context
        )

        assert is_approved == False
        assert report['score'] == 40
        assert report['reason'] == "Below threshold"  # Should use reasoning
        assert report['suggestions'] == "Improve quality"

    def test_parse_validation_missing_sections(self, validator, sample_scenario, sample_web_context):
        """Test parsing response with missing sections."""
        incomplete_response = """APPROVED: YES
SCORE: 70/100"""

        is_approved, report = validator._parse_validation_result(
            incomplete_response, sample_scenario, sample_web_context
        )

        assert is_approved == True
        assert report['score'] == 70
        assert report['reason'] == "Meets quality threshold"  # Default for approved

    def test_parse_validation_malformed_score(self, validator, sample_scenario, sample_web_context):
        """Test parsing response with malformed score."""
        malformed_response = """APPROVED: NO
SCORE: not-a-number/100
REASONING: Test reasoning
SUGGESTIONS: Test suggestions"""

        is_approved, report = validator._parse_validation_result(
            malformed_response, sample_scenario, sample_web_context
        )

        assert is_approved == False
        assert report['score'] == 0  # Should default to 0 for invalid score
        assert report['reason'] == "Test reasoning"  # Should use reasoning

    def test_parse_validation_multiline_content(self, validator, sample_scenario, sample_web_context):
        """Test parsing response with complex multi-line content."""
        multiline_response = """APPROVED: NO
SCORE: 45/100
REASONING: This scenario has multiple issues that need addressing:

1. First issue: The content lacks specificity
   - Sub-point about details
   - Another sub-point with more info

2. Second issue: Evaluation criteria not met
   - More detailed explanation here
   - Even more details on next line

3. Third issue: Quality concerns
   - Final detailed explanation
   - Last line of reasoning

SUGGESTIONS: To improve this scenario, consider:

- Adding more specific context details
- Improving the target response clarity
- Ensuring proper principle alignment
- Testing with diverse user populations

Additional recommendation: Review similar scenarios for comparison."""

        is_approved, report = validator._parse_validation_result(
            multiline_response, sample_scenario, sample_web_context
        )

        assert is_approved == False
        assert report['score'] == 45

        # Check that multi-line reasoning is captured
        reasoning = report['reason']
        assert 'This scenario has multiple issues' in reasoning
        assert '1. First issue:' in reasoning
        assert '2. Second issue:' in reasoning
        assert '3. Third issue:' in reasoning
        assert 'Last line of reasoning' in reasoning

        # Check that multi-line suggestions are captured
        suggestions = report['suggestions']
        assert 'To improve this scenario' in suggestions
        assert 'Adding more specific context' in suggestions
        assert 'Additional recommendation' in suggestions

    def test_parse_validation_edge_cases(self, validator, sample_scenario, sample_web_context):
        """Test various edge cases in validation parsing."""
        edge_cases = [
            # No content after colons
            ("APPROVED: YES\nSCORE: 80/100\nREASONING:\nSUGGESTIONS:", True, 80),

            # Approved with low score (should be rejected due to low score)
            ("APPROVED: YES\nSCORE: 30/100\nREASONING: Good enough", False, 30),

            # High score but not approved
            ("APPROVED: NO\nSCORE: 90/100\nREASONING: Technical issue", False, 90),

            # Mixed case
            ("approved: yes\nscore: 75/100\nreasoning: Good work", False, 0),  # Case sensitive, so not approved and score not extracted
        ]

        for response_text, expected_approved, expected_score in edge_cases:
            is_approved, report = validator._parse_validation_result(
                response_text, sample_scenario, sample_web_context
            )
            assert is_approved == expected_approved, f"Failed approval for: {response_text}"
            assert report['score'] == expected_score, f"Failed score for: {response_text}"

    def test_parse_validation_empty_response(self, validator, sample_scenario, sample_web_context):
        """Test parsing empty validation response."""
        is_approved, report = validator._parse_validation_result(
            "", sample_scenario, sample_web_context
        )

        assert is_approved == False
        assert report['score'] == 0
        assert report['reason'] == "Below quality threshold"

    def test_parse_validation_preserves_metadata(self, validator, sample_scenario, sample_web_context, mock_validation_response_approved):
        """Test that parsing preserves scenario and context metadata."""
        is_approved, report = validator._parse_validation_result(
            mock_validation_response_approved, sample_scenario, sample_web_context
        )

        assert report['scenario'] == sample_scenario
        assert report['web_search_context'] == sample_web_context
        assert report['full_response'] == mock_validation_response_approved

    def test_parse_validation_handles_colons_in_content(self, validator, sample_scenario, sample_web_context):
        """Test parsing when content contains colons."""
        response_with_colons = """APPROVED: NO
SCORE: 50/100
REASONING: The scenario asks: "How should I handle this?"
This question format is problematic because:
- It uses a colon in the middle
- Time stamps like 12:30 PM might appear
- URLs like https://example.com are common

SUGGESTIONS: Consider these improvements:
- Rewrite the question format
- Remove time references like 3:45 PM
- Avoid URLs such as http://test.com in examples"""

        is_approved, report = validator._parse_validation_result(
            response_with_colons, sample_scenario, sample_web_context
        )

        reasoning = report['reason']
        suggestions = report['suggestions']

        # Should capture content with colons correctly
        assert 'How should I handle this?' in reasoning
        assert '12:30 PM' in reasoning
        assert 'https://example.com' in reasoning
        assert '3:45 PM' in suggestions
        assert 'http://test.com' in suggestions

    def test_validation_score_extraction_variants(self, validator, sample_scenario, sample_web_context):
        """Test score extraction with number/100 format."""
        score_variants = [
            ("SCORE: 85/100", 85),
            ("SCORE: 75/100", 75),
            ("SCORE: 0/100", 0),
            ("SCORE: 100/100", 100),
            ("SCORE: 85", 0),  # Should default to 0 without /100
            ("SCORE: No numbers here", 0),  # Should default to 0
        ]

        for score_line, expected_score in score_variants:
            response = f"APPROVED: NO\n{score_line}\nREASONING: Test"
            is_approved, report = validator._parse_validation_result(
                response, sample_scenario, sample_web_context
            )
            assert report['score'] == expected_score, f"Failed for: {score_line}"