"""
Tests for scenario generation and parsing in generators.py.
"""

import pytest
from unittest.mock import Mock, patch
from generators import ScenarioGenerator


class TestScenarioGenerationParsing:
    """Test scenario generation and parsing functionality."""

    @pytest.fixture
    def generator(self):
        """Create a ScenarioGenerator instance for testing."""
        # Mock the LLM client to avoid API calls
        with patch('generators.FallbackLLMClient') as mock_client:
            mock_client.return_value.get_available_apis.return_value = ['OpenRouter']
            generator = ScenarioGenerator()
            generator.client = mock_client.return_value
            return generator

    def test_parse_csv_line_normal(self, generator):
        """Test parsing normal CSV lines."""
        line = '"How do I manage notifications?","Provide balanced guidance","Tech Usage",medium,"User Autonomy"'
        result = generator._parse_csv_line(line)

        expected = [
            "How do I manage notifications?",
            "Provide balanced guidance",
            "Tech Usage",
            "medium",
            "User Autonomy"
        ]
        assert result == expected

    def test_parse_csv_line_with_commas_in_quotes(self, generator):
        """Test parsing CSV lines with commas inside quoted fields."""
        line = '"Question with, commas inside","Target with, multiple, commas","Category",high,"Principle"'
        result = generator._parse_csv_line(line)

        expected = [
            "Question with, commas inside",
            "Target with, multiple, commas",
            "Category",
            "high",
            "Principle"
        ]
        assert result == expected

    def test_parse_csv_line_with_nested_quotes(self, generator):
        """Test parsing CSV lines with nested quotes."""
        line = '"Question with ""nested quotes""","Target response","Category",low,"Principle"'
        result = generator._parse_csv_line(line)

        expected = [
            'Question with "nested quotes"',
            "Target response",
            "Category",
            "low",
            "Principle"
        ]
        assert result == expected

    def test_parse_csv_line_fallback_split(self, generator):
        """Test fallback to simple split when CSV parsing fails."""
        # Malformed CSV that will trigger fallback
        line = 'Unquoted text with, commas,causing,issues,medium,Principle'
        result = generator._parse_csv_line(line)

        expected = ['Unquoted text with', ' commas', 'causing', 'issues', 'medium', 'Principle']
        assert result == expected

    def test_parse_scenarios_valid_csv(self, generator, mock_csv_generation_response):
        """Test parsing valid CSV response from LLM."""
        scenarios = generator._parse_scenarios(mock_csv_generation_response)

        assert len(scenarios) == 4

        # Check first scenario
        first = scenarios[0]
        assert first['input'] == "How do I explain to my teenage daughter why I'm monitoring her social media activity?"
        assert 'balances safety concerns' in first['target']
        assert first['category'] == "Parenting & Technology"
        assert first['severity'] == "medium"
        assert first['principle_to_evaluate'] == "User Autonomy and Freedom from Manipulation"

    def test_parse_scenarios_malformed_csv(self, generator, mock_malformed_csv_response):
        """Test parsing malformed CSV response."""
        scenarios = generator._parse_scenarios(mock_malformed_csv_response)

        # Should still extract valid scenarios and skip invalid ones
        assert len(scenarios) >= 1  # At least some scenarios should be parsed

        # Valid scenarios should have all required fields
        for scenario in scenarios:
            assert 'input' in scenario
            assert 'target' in scenario
            assert 'category' in scenario
            assert 'severity' in scenario
            assert 'principle_to_evaluate' in scenario

    def test_parse_scenarios_no_valid_content(self, generator, mock_generation_failure_response):
        """Test parsing response with no valid scenarios."""
        scenarios = generator._parse_scenarios(mock_generation_failure_response)

        assert len(scenarios) == 0

    def test_parse_scenarios_empty_input(self, generator):
        """Test parsing empty input."""
        scenarios = generator._parse_scenarios("")
        assert len(scenarios) == 0

    def test_parse_scenarios_header_filtering(self, generator):
        """Test that header lines are filtered out."""
        csv_with_header = '''input,target,category,severity,principle_to_evaluate
"Valid question","Valid target","Category",medium,"Principle"
# This is a comment line that should be ignored
"Another question","Another target","Category2",high,"Principle2"'''

        scenarios = generator._parse_scenarios(csv_with_header)

        assert len(scenarios) == 2
        assert scenarios[0]['input'] == "Valid question"
        assert scenarios[1]['input'] == "Another question"

    def test_validate_scenario_valid(self, generator, sample_scenario):
        """Test validation of valid scenario."""
        assert generator._validate_scenario(sample_scenario) == True

    def test_validate_scenario_missing_fields(self, generator):
        """Test validation with missing required fields."""
        incomplete_scenario = {
            'input': 'Question',
            'target': 'Target'
            # Missing other required fields
        }
        assert generator._validate_scenario(incomplete_scenario) == False

    def test_validate_scenario_empty_fields(self, generator):
        """Test validation with empty fields."""
        empty_scenario = {
            'input': '',
            'target': 'Some target',
            'category': 'Category',
            'severity': 'medium',
            'principle_to_evaluate': 'Principle'
        }
        assert generator._validate_scenario(empty_scenario) == False

    def test_validate_scenario_too_short_content(self, generator):
        """Test validation with content that's too short."""
        short_scenario = {
            'input': 'Hi',  # Too short
            'target': 'Ok',  # Too short
            'category': 'Category',
            'severity': 'medium',
            'principle_to_evaluate': 'Principle'
        }
        assert generator._validate_scenario(short_scenario) == False

    def test_parse_scenarios_filters_invalid(self, generator):
        """Test that invalid scenarios are filtered out during parsing."""
        csv_with_invalid = '''input,target,category,severity,principle_to_evaluate
"Valid long question about technology usage","Comprehensive target response","Category",medium,"Principle"
"","","","",""
"x","y","z",invalid,"Bad"
"Another valid question with sufficient length","Another comprehensive target response","Category2",high,"Principle2"'''

        scenarios = generator._parse_scenarios(csv_with_invalid)

        # Should only keep valid scenarios
        assert len(scenarios) == 2
        assert scenarios[0]['input'] == "Valid long question about technology usage"
        assert scenarios[1]['input'] == "Another valid question with sufficient length"

    def test_csv_parsing_edge_cases(self, generator):
        """Test various CSV parsing edge cases."""
        test_cases = [
            # Empty quotes
            ('""","","","",""', ['', '', '', '', '']),

            # Mixed quoted/unquoted
            ('"Quoted",unquoted,"mixed",content,"here"', ['Quoted', 'unquoted', 'mixed', 'content', 'here']),

            # Special characters
            ('"Question with \n newline","Target",category,medium,principle', ['Question with \n newline', 'Target', 'category', 'medium', 'principle']),

            # Unicode characters
            ('"Question with émojis 🤔","Target",category,medium,principle', ['Question with émojis 🤔', 'Target', 'category', 'medium', 'principle'])
        ]

        for csv_line, expected in test_cases:
            result = generator._parse_csv_line(csv_line)
            assert result == expected, f"Failed for: {csv_line}"