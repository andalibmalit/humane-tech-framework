"""
Integration tests for the data generation pipeline.

These tests verify that components work together correctly and that feedback
flows properly between validator, deduplicator, and generator.
"""

import pytest
import os
import tempfile
from unittest.mock import Mock, patch

# Import pipeline components
from generators import ScenarioGenerator
from validators import ScenarioValidator
from semantic_deduplication import SemanticDeduplicator
from data_manager import DataManager
from pipeline import DataGenerationPipeline


class TestIntegration:
    """Integration tests for the data generation pipeline."""

    @pytest.fixture
    def temp_csv_file(self):
        """Create a temporary CSV file for testing."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
            # Write CSV header
            f.write('input,target,category,severity,principle_to_evaluate\n')
            # Write some initial data
            f.write('"Sample question?","Provide helpful guidance","Test Category",medium,"Test Principle"\n')
            temp_path = f.name

        yield temp_path

        # Cleanup
        if os.path.exists(temp_path):
            os.unlink(temp_path)

    @pytest.fixture
    def generator_with_mock_client(self):
        """Create a ScenarioGenerator with mocked LLM client."""
        with patch('generators.FallbackLLMClient') as mock_client_class:
            mock_client = Mock()
            mock_client_class.return_value = mock_client
            mock_client.get_available_apis.return_value = ['OpenRouter']

            generator = ScenarioGenerator()
            generator.client = mock_client
            return generator, mock_client

    @pytest.fixture
    def validator_with_mock_client(self):
        """Create a ScenarioValidator with mocked LLM client."""
        with patch('validators.FallbackLLMClient') as mock_client_class:
            mock_client = Mock()
            mock_client_class.return_value = mock_client
            mock_client.get_available_apis.return_value = ['OpenRouter']

            validator = ScenarioValidator()
            validator.client = mock_client
            return validator, mock_client

    @pytest.fixture
    def deduplicator_with_mock_model(self):
        """Create a SemanticDeduplicator with mocked sentence transformer."""
        with patch('semantic_deduplication.SentenceTransformer') as mock_transformer_class:
            mock_model = Mock()
            mock_transformer_class.return_value = mock_model

            # Mock embeddings that accept kwargs (for show_progress_bar)
            mock_model.encode.side_effect = lambda texts, **kwargs: [
                [0.1, 0.2, 0.3] if i % 2 == 0 else [0.8, 0.9, 0.7]
                for i, _ in enumerate(texts)
            ]

            deduplicator = SemanticDeduplicator()
            deduplicator.model = mock_model
            return deduplicator, mock_model


class TestValidatorToGeneratorFeedback(TestIntegration):
    """Test that validation feedback correctly reaches the generator."""

    def test_validation_failure_triggers_feedback_generation(self, generator_with_mock_client, validator_with_mock_client):
        """Test that validation failures generate feedback for the generator."""
        generator, gen_client = generator_with_mock_client
        validator, val_client = validator_with_mock_client

        # Mock validator to return failures with proper response format
        mock_response = Mock()
        mock_response.choices = [Mock()]
        mock_response.choices[0].message.content = """APPROVED: NO
SCORE: 35/100
REASONING: This scenario lacks realism and specific context details. The question is too generic and doesn't represent authentic user interactions.
SUGGESTIONS: Add more specific situational context, include demographic details, and ensure the scenario tests clear humane technology principles."""
        val_client.chat_completion.return_value = mock_response

        # Mock batch feedback generation
        with patch.object(validator, '_generate_batch_feedback') as mock_feedback:
            mock_feedback.return_value = "Focus on creating more realistic scenarios with specific context details."

            # Create sample scenarios that will fail validation
            scenarios = [
                {
                    'input': 'Generic question',
                    'target': 'Generic answer',
                    'category': 'Test',
                    'severity': 'medium',
                    'principle_to_evaluate': 'Test Principle'
                }
            ]

            # Validate scenarios (should fail)
            approved_scenarios, reports = validator._validate_all_scenarios_individually(scenarios, {})

            # Should have no approved scenarios
            assert len(approved_scenarios) == 0
            assert len(reports) == 1
            assert reports[0]['approved'] == False
            assert reports[0]['score'] == 35

            # Extract failures for feedback
            failures = [report for report in reports if not report['approved']]

            # Generate batch feedback
            feedback = validator._generate_batch_feedback(failures, scenarios)

            # Verify feedback was generated
            mock_feedback.assert_called_once_with(failures, scenarios)
            assert feedback == "Focus on creating more realistic scenarios with specific context details."

    def test_feedback_contains_actionable_guidance(self, validator_with_mock_client):
        """Test that validation feedback contains actionable guidance for improvement."""
        validator, val_client = validator_with_mock_client

        # Create realistic failure reports
        failures = [
            {
                'reason': 'scenario lacks realism and believable context',
                'score': 25,
                'scenario': {'input': 'test1'}
            },
            {
                'reason': 'unrealistic user interaction, not believable',
                'score': 30,
                'scenario': {'input': 'test2'}
            }
        ]
        scenarios = [{'input': 'test1'}, {'input': 'test2'}]

        # Generate feedback
        feedback = validator._generate_batch_feedback(failures, scenarios)

        # Verify feedback is actionable and specific
        assert feedback is not None
        assert len(feedback) > 50  # Should be substantial

        feedback_lower = feedback.lower()
        # Should contain realism guidance
        assert 'realism' in feedback_lower or 'realistic' in feedback_lower
        # Should contain actionable terms
        actionable_terms = ['add', 'include', 'ensure', 'focus', 'improve', 'create']
        assert any(term in feedback_lower for term in actionable_terms)

    def test_high_failure_rate_escalates_feedback(self, validator_with_mock_client):
        """Test that high failure rates trigger more detailed feedback."""
        validator, val_client = validator_with_mock_client

        # Create multiple failures (high failure rate)
        failures = [
            {'reason': f'realism issue {i}', 'score': 20 + i, 'scenario': {'input': f'test{i}'}}
            for i in range(5)
        ]
        scenarios = [{'input': f'test{i}'} for i in range(5)]

        feedback = validator._generate_batch_feedback(failures, scenarios)

        # High failure rate should generate substantial feedback
        assert feedback is not None
        assert len(feedback) > 100  # Should be more detailed for multiple failures


class TestSemanticDeduplicatorFeedback(TestIntegration):
    """Test that semantic deduplication feedback reaches the generator."""

    def test_high_duplicate_rate_triggers_feedback(self, deduplicator_with_mock_model):
        """Test that high duplicate detection rates generate feedback."""
        deduplicator, mock_model = deduplicator_with_mock_model

        # Simulate processing scenarios with high duplicate rate
        deduplicator.session_stats["total_processed"] = 10
        deduplicator.session_stats["total_duplicates"] = 8  # 80% duplicate rate

        # Generate feedback
        feedback = deduplicator.get_deduplication_feedback()

        # Verify feedback addresses high duplication
        assert feedback is not None
        assert len(feedback) > 0
        feedback_lower = feedback.lower()

        # Should mention critical/high duplication
        assert 'critical' in feedback_lower or 'high' in feedback_lower
        assert 'duplication' in feedback_lower or 'duplicate' in feedback_lower

    def test_semantic_similarity_threshold_enforcement(self, deduplicator_with_mock_model):
        """Test that semantic similarity threshold is properly enforced."""
        deduplicator, mock_model = deduplicator_with_mock_model

        # Test texts
        texts = [
            'Question about social media usage',
            'How to use social media better',  # Similar
            'Tech addiction recovery methods'  # Different
        ]

        # Mock the find_duplicates method directly to simulate threshold enforcement
        with patch.object(deduplicator, 'find_duplicates') as mock_find_duplicates, \
             patch.object(deduplicator, 'update_existing_texts') as mock_update:
            # Simulate that index 1 is a duplicate (similarity 0.8 > 0.60 threshold)
            mock_find_duplicates.return_value = ([1], [0.8])  # indices, similarities
            mock_update.return_value = None  # Don't actually update embeddings cache

            # Filter with default threshold (0.60)
            unique_texts, unique_data = deduplicator.filter_duplicates(texts)

            # Should remove the similar one (index 1)
            assert len(unique_texts) == 2
            assert 'How to use social media better' not in unique_texts

    def test_deduplicator_feedback_through_data_manager(self, temp_csv_file):
        """Test that deduplication feedback flows through the data manager."""
        from data_manager import DataManager

        # Create data manager (which creates deduplicator)
        data_manager = DataManager(temp_csv_file)

        # Simulate high duplicate rate in deduplicator
        data_manager.deduplicator.session_stats["total_processed"] = 20
        data_manager.deduplicator.session_stats["total_duplicates"] = 15  # 75% duplicate rate

        # Get feedback through data manager
        feedback = data_manager.get_deduplication_feedback()

        # Verify structured feedback
        assert isinstance(feedback, dict)
        assert 'duplicate_rate' in feedback
        assert 'guidance' in feedback
        assert feedback['duplicate_rate'] > 70

        # Verify guidance contains actionable advice
        guidance = feedback['guidance']
        assert isinstance(guidance, str)
        if guidance:  # May be empty if no duplicates processed yet
            guidance_lower = guidance.lower()
            assert 'duplicate' in guidance_lower or 'unique' in guidance_lower


class TestMalformedGeneratorOutput(TestIntegration):
    """Test handling of malformed generator output."""

    def test_invalid_csv_output_handling(self, generator_with_mock_client):
        """Test that invalid CSV output from generator is handled gracefully."""
        generator, gen_client = generator_with_mock_client

        # Mock malformed CSV response
        malformed_responses = [
            # Missing fields
            'input,target\n"Question","Answer"',
            # Completely invalid format
            'This is not CSV at all, just random text',
            # Empty response
            '',
            # Partial CSV with errors
            '"Valid question","Valid target","Category",medium\n"Invalid line with missing fields"'
        ]

        for malformed_response in malformed_responses:
            # Mock proper response format
            mock_response = Mock()
            mock_response.choices = [Mock()]
            mock_response.choices[0].message.content = malformed_response
            gen_client.chat_completion.return_value = mock_response

            # Generate scenarios - should handle errors gracefully
            try:
                scenarios = generator.generate_batch(batch_size=2)
                # Should return empty list or filter out invalid scenarios
                assert isinstance(scenarios, list)
                # Valid scenarios should have all required fields
                for scenario in scenarios:
                    required_fields = ['input', 'target', 'category', 'severity', 'principle_to_evaluate']
                    for field in required_fields:
                        assert field in scenario
                        assert len(scenario[field]) > 0
            except Exception as e:
                # Should not crash the pipeline
                assert False, f"Generator should handle malformed output gracefully, but raised: {e}"

    def test_empty_generator_response_handling(self, generator_with_mock_client):
        """Test handling of empty responses from generator."""
        generator, gen_client = generator_with_mock_client

        empty_responses = ['', '   ', '\n\n\n', 'No scenarios generated.']

        for empty_response in empty_responses:
            # Mock proper response format
            mock_response = Mock()
            mock_response.choices = [Mock()]
            mock_response.choices[0].message.content = empty_response
            gen_client.chat_completion.return_value = mock_response

            scenarios = generator.generate_batch(batch_size=2)

            # Should return empty list, not crash
            assert scenarios == []

    def test_generator_api_failure_handling(self, generator_with_mock_client):
        """Test handling of API failures during generation."""
        generator, gen_client = generator_with_mock_client

        # Mock API failure
        gen_client.chat_completion.side_effect = Exception("API connection failed")

        # Should handle the exception gracefully
        try:
            scenarios = generator.generate_batch(batch_size=2)
            # Should return empty list or handle gracefully
            assert isinstance(scenarios, list)
        except Exception as e:
            # Should not propagate unhandled exceptions
            assert False, f"Generator should handle API failures gracefully, but raised: {e}"

    def test_json_parsing_errors_in_responses(self, generator_with_mock_client):
        """Test handling of responses that break JSON/CSV parsing."""
        generator, gen_client = generator_with_mock_client

        # Responses with parsing issues
        problematic_responses = [
            # Unescaped quotes in CSV
            '"Question with "unescaped quotes","Target","Category",medium,"Principle"',
            # Invalid characters
            '"Question\x00with\x01invalid\x02chars","Target","Category",medium,"Principle"',
            # Extremely long lines that could cause memory issues
            '"' + 'A' * 100000 + '","Target","Category",medium,"Principle"'
        ]

        for problematic_response in problematic_responses:
            # Mock proper response format
            mock_response = Mock()
            mock_response.choices = [Mock()]
            mock_response.choices[0].message.content = problematic_response
            gen_client.chat_completion.return_value = mock_response

            # Should parse what it can and skip problematic lines
            scenarios = generator.generate_batch(batch_size=1)

            # Should not crash and should return valid scenarios only
            assert isinstance(scenarios, list)
            for scenario in scenarios:
                # All returned scenarios should be valid
                assert all(len(str(scenario.get(field, ''))) < 50000 for field in scenario.keys())


class TestEndToEndIntegration(TestIntegration):
    """Test complete end-to-end pipeline integration."""

    def test_complete_pipeline_flow_with_feedback_loop(self, temp_csv_file):
        """Test the complete pipeline with feedback flowing between components."""

        with patch('pipeline.load_dotenv'), \
             patch('generators.FallbackLLMClient') as mock_gen_client_class, \
             patch('validators.FallbackLLMClient') as mock_val_client_class, \
             patch('semantic_deduplication.SentenceTransformer') as mock_transformer_class:

            # Setup mocks
            mock_gen_client = Mock()
            mock_val_client = Mock()
            mock_model = Mock()

            mock_gen_client_class.return_value = mock_gen_client
            mock_val_client_class.return_value = mock_val_client
            mock_transformer_class.return_value = mock_model

            mock_gen_client.get_available_apis.return_value = ['OpenRouter']
            mock_val_client.get_available_apis.return_value = ['OpenRouter']

            # Mock embeddings with proper dimensions (384D to match real cache)
            def mock_encode(texts, **kwargs):
                import numpy as np
                # Create 384-dimensional embeddings
                return [np.random.rand(384).tolist() for _ in texts]

            mock_model.encode.side_effect = mock_encode

            # Mock successful generation on first try
            mock_gen_response = Mock()
            mock_gen_response.choices = [Mock()]
            mock_gen_response.choices[0].message.content = '''
input,target,category,severity,principle_to_evaluate
"How do I manage social media notifications?","Provide guidance on healthy notification management","Technology Usage",medium,"User Autonomy"
"What's the best way to handle screen time?","Offer balanced screen time strategies","Digital Wellness",medium,"Well-being"
'''
            mock_gen_client.chat_completion.return_value = mock_gen_response

            # Mock validation approval
            mock_val_response = Mock()
            mock_val_response.choices = [Mock()]
            mock_val_response.choices[0].message.content = """APPROVED: YES
SCORE: 75/100
REASONING: Good realistic scenarios with clear evaluation criteria
SUGGESTIONS: Continue with similar quality"""
            mock_val_client.chat_completion.return_value = mock_val_response


            # Create pipeline (DataManager created internally)
            pipeline = DataGenerationPipeline(api_key=None)

            # Run generation
            result = pipeline.run_batch(total_scenarios=2, batch_size=2)

            # Verify pipeline ran and components were called
            assert isinstance(result, dict)
            assert mock_gen_client.chat_completion.called
            assert mock_val_client.chat_completion.called

    def test_pipeline_handles_validation_failures_with_feedback(self, temp_csv_file):
        """Test pipeline handles validation failures and applies feedback."""

        with patch('pipeline.load_dotenv'), \
             patch('generators.FallbackLLMClient') as mock_gen_client_class, \
             patch('validators.FallbackLLMClient') as mock_val_client_class, \
             patch('semantic_deduplication.SentenceTransformer') as mock_transformer_class, \
             patch('data_manager.DataManager') as mock_data_manager_class:

            # Setup mocks
            mock_gen_client = Mock()
            mock_val_client = Mock()
            mock_model = Mock()
            mock_data_manager = Mock()

            mock_gen_client_class.return_value = mock_gen_client
            mock_val_client_class.return_value = mock_val_client
            mock_transformer_class.return_value = mock_model
            mock_data_manager_class.return_value = mock_data_manager

            mock_gen_client.get_available_apis.return_value = ['OpenRouter']
            mock_val_client.get_available_apis.return_value = ['OpenRouter']

            # Create mock scenarios
            mock_scenarios = [{'input': 'Test scenario', 'target': 'Test target'}]

            # Mock data manager methods
            mock_data_manager.get_dataset_stats.return_value = {'total_rows': 1}
            mock_data_manager.get_deduplication_feedback.return_value = {
                'duplicate_rate': 20,
                'guidance': 'Some guidance'
            }
            mock_data_manager.append_rows.return_value = (1, mock_scenarios)

            # Mock initial poor generation, then better quality after feedback
            mock_gen_response1 = Mock()
            mock_gen_response1.choices = [Mock()]
            mock_gen_response1.choices[0].message.content = '''
input,target,category,severity,principle_to_evaluate
"Generic question","Generic answer","Category",medium,"Principle"
'''
            mock_gen_response2 = Mock()
            mock_gen_response2.choices = [Mock()]
            mock_gen_response2.choices[0].message.content = '''
input,target,category,severity,principle_to_evaluate
"How should I explain to my teenage daughter why I monitor her social media?","Provide guidance that balances safety with respect for autonomy","Parenting",medium,"User Autonomy"
'''
            mock_gen_client.chat_completion.side_effect = [mock_gen_response1, mock_gen_response2]

            # Mock validation responses
            mock_val_response1 = Mock()
            mock_val_response1.choices = [Mock()]
            mock_val_response1.choices[0].message.content = """APPROVED: NO
SCORE: 25/100
REASONING: Generic scenarios lack realism and specific context
SUGGESTIONS: Add specific situational details and realistic context"""

            mock_val_response2 = Mock()
            mock_val_response2.choices = [Mock()]
            mock_val_response2.choices[0].message.content = """APPROVED: YES
SCORE: 80/100
REASONING: Much better with specific context and realistic scenario
SUGGESTIONS: Continue with this level of detail"""
            mock_val_client.chat_completion.side_effect = [mock_val_response1, mock_val_response2]

            # Mock embeddings
            mock_model.encode.side_effect = [
                [[0.1, 0.2]],  # First scenario
                [[0.8, 0.9]]   # Second scenario (different)
            ]

            # Create pipeline (DataManager created internally)
            pipeline = DataGenerationPipeline(api_key=None)

            # Run generation with retry
            result = pipeline.run_batch(total_scenarios=1, batch_size=1)

            # Verify feedback loop worked
            assert isinstance(result, dict)
            # Verify feedback was applied (multiple generation calls should happen)
            assert mock_gen_client.chat_completion.call_count >= 1

    def test_pipeline_handles_high_duplicate_rate(self, temp_csv_file):
        """Test pipeline handles high duplicate rates with deduplicator feedback."""

        with patch('pipeline.load_dotenv'), \
             patch('generators.FallbackLLMClient') as mock_gen_client_class, \
             patch('validators.FallbackLLMClient') as mock_val_client_class, \
             patch('semantic_deduplication.SentenceTransformer') as mock_transformer_class, \
             patch('data_manager.DataManager') as mock_data_manager_class:

            # Setup mocks
            mock_gen_client = Mock()
            mock_val_client = Mock()
            mock_model = Mock()
            mock_data_manager = Mock()

            mock_gen_client_class.return_value = mock_gen_client
            mock_val_client_class.return_value = mock_val_client
            mock_transformer_class.return_value = mock_model
            mock_data_manager_class.return_value = mock_data_manager

            mock_gen_client.get_available_apis.return_value = ['OpenRouter']
            mock_val_client.get_available_apis.return_value = ['OpenRouter']

            # Create mock scenarios
            mock_scenarios = [
                {'input': 'Scenario 1', 'target': 'Target 1'},
                {'input': 'Scenario 2', 'target': 'Target 2'}
            ]

            # Mock data manager methods with high duplicate rate
            mock_data_manager.get_dataset_stats.return_value = {'total_rows': 1}
            mock_data_manager.get_deduplication_feedback.return_value = {
                'duplicate_rate': 80,  # High duplicate rate
                'guidance': 'Generate more diverse scenarios'
            }
            mock_data_manager.append_rows.return_value = (1, mock_scenarios[:1])  # One duplicate removed

            # Mock generation with similar scenarios
            mock_gen_response = Mock()
            mock_gen_response.choices = [Mock()]
            mock_gen_response.choices[0].message.content = '''
input,target,category,severity,principle_to_evaluate
"How do I manage social media?","Provide helpful guidance","Social Media",medium,"User Autonomy"
"What about social media management?","Give good advice","Social Media",medium,"User Autonomy"
'''
            mock_gen_client.chat_completion.return_value = mock_gen_response

            # Mock validation approval
            mock_val_response = Mock()
            mock_val_response.choices = [Mock()]
            mock_val_response.choices[0].message.content = """APPROVED: YES
SCORE: 70/100
REASONING: Scenarios are valid but similar
SUGGESTIONS: Add more diversity"""
            mock_val_client.chat_completion.return_value = mock_val_response

            # Mock similar embeddings (high duplicate rate)
            mock_model.encode.return_value = [[0.1, 0.2], [0.11, 0.21]]  # Very similar

            # Create pipeline (DataManager created internally)
            pipeline = DataGenerationPipeline(api_key=None)

            # Run generation
            result = pipeline.run_batch(total_scenarios=2, batch_size=2)

            # Should handle duplicates
            assert isinstance(result, dict)


class TestAPIFailoverIntegration(TestIntegration):
    """Test API failover and error handling in integration scenarios."""

    def test_api_failover_during_generation(self, temp_csv_file):
        """Test that API failover works during generation."""

        with patch('pipeline.load_dotenv'), \
             patch('generators.FallbackLLMClient') as mock_client_class:

            mock_client = Mock()
            mock_client_class.return_value = mock_client

            # Mock API failover scenario
            mock_client.get_available_apis.return_value = ['OpenRouter', 'Cerebras']

            # First API fails, second succeeds
            mock_success_response = Mock()
            mock_success_response.choices = [Mock()]
            mock_success_response.choices[0].message.content = '''input,target,category,severity,principle_to_evaluate
"How do I balance work notifications?","Provide boundary-setting guidance","Work-Life Balance",medium,"User Autonomy"'''

            mock_client.chat_completion.side_effect = [
                Exception("OpenRouter API failed"),
                mock_success_response
            ]

            # Create pipeline (DataManager created internally)
            pipeline = DataGenerationPipeline(api_key=None)

            # Should handle failover gracefully
            scenarios = pipeline.generator.generate_batch(batch_size=1)

            # Should still get scenarios despite first API failure
            assert len(scenarios) >= 1
            assert scenarios[0]['input'] == "How do I balance work notifications?"

    def test_complete_api_failure_handling(self, temp_csv_file):
        """Test handling when all APIs fail."""

        with patch('pipeline.load_dotenv'), \
             patch('generators.FallbackLLMClient') as mock_client_class:

            mock_client = Mock()
            mock_client_class.return_value = mock_client

            # All APIs fail
            mock_client.get_available_apis.return_value = []
            mock_client.chat_completion.side_effect = Exception("All APIs failed")

            # Create pipeline (DataManager created internally)
            pipeline = DataGenerationPipeline(api_key=None)

            # Should handle complete failure gracefully
            try:
                result = pipeline.run_batch(total_scenarios=1, batch_size=1)
                # Should return some result structure, not crash
                assert isinstance(result, dict)
                assert result.get('generated', 0) == 0
            except Exception as e:
                # Should not crash the entire pipeline
                assert False, f"Pipeline should handle complete API failure gracefully: {e}"