from typing import Dict, Any, List, Optional, Union
from deepeval.metrics import GEval
from deepeval.test_case import LLMTestCase, LLMTestCaseParams
import logging

class DeepEvalHandler:
    """
    Handler for DeepEval metrics and evaluations.
    """
    
    def __init__(self):
        """Initialize the DeepEvalHandler."""
        pass
        
    def create_correctness_metric(self, threshold: float = 0.5) -> GEval:
        """
        Create a GEval correctness metric.
        
        Args:
            threshold: The threshold score for the metric to pass (default: 0.5)
            
        Returns:
            GEval metric configured for correctness evaluation
        """
        return GEval(
            name="Correctness",
            criteria="Determine if the 'actual output' is correct based on the 'expected output'.",
            evaluation_params=[LLMTestCaseParams.ACTUAL_OUTPUT, LLMTestCaseParams.EXPECTED_OUTPUT],
            threshold=threshold
        )
    
    def create_factual_accuracy_metric(self, threshold: float = 0.5) -> GEval:
        """
        Create a GEval factual accuracy metric.
        
        Args:
            threshold: The threshold score for the metric to pass (default: 0.5)
            
        Returns:
            GEval metric configured for factual accuracy evaluation
        """
        return GEval(
            name="Factual Accuracy",
            criteria="Determine if the LLM response contains factually accurate information based on the provided context.",
            evaluation_params=[LLMTestCaseParams.ACTUAL_OUTPUT, LLMTestCaseParams.CONTEXT],
            threshold=threshold
        )
    
    def evaluate_response(self, 
                         input_query: str, 
                         actual_output: str,
                         expected_output: Optional[str] = None,
                         context: Optional[Union[str, List[str]]] = None,
                         metrics: Optional[List[str]] = None) -> Dict[str, Any]:
        """
        Evaluate an LLM response using specified metrics.
        
        Args:
            input_query: The input query that generated the LLM response
            actual_output: The actual response from the LLM
            expected_output: The expected response for comparison (required for GEval)
            context: Context information for factual consistency checking
            metrics: List of metrics to use (e.g., ["correctness", "factual_accuracy"])
            
        Returns:
            Dict containing evaluation results
        """
        if metrics is None:
            metrics = ["correctness"]
        
        test_case = LLMTestCase(
            input=input_query,
            actual_output=actual_output,
            expected_output=expected_output,
            context=context
        )
        
        from deepeval import assert_test
        
        all_results = []
        
        if "correctness" in metrics and expected_output:
            correctness_metric = self.create_correctness_metric()
            try:
                assert_test(test_case, [correctness_metric])
                all_results.append(correctness_metric)
            except Exception as e:
                logging.error(f"Error in correctness evaluation: {str(e)}")
            
        if "factual_accuracy" in metrics and context:
            factual_metric = self.create_factual_accuracy_metric()
            try:
                assert_test(test_case, [factual_metric])
                all_results.append(factual_metric)
            except Exception as e:
                logging.error(f"Error in factual accuracy evaluation: {str(e)}")
        
        return {
            "input": input_query,
            "actual_output": actual_output,
            "expected_output": expected_output,
            "context": context,
            "evaluation_results": all_results
        }
    
    def evaluate_batch(self, 
                      test_cases: List[Dict[str, Any]],
                      metrics: Optional[List[str]] = None) -> List[Dict[str, Any]]:
        """
        Evaluate multiple LLM responses using specified metrics.
        
        Args:
            test_cases: List of test case dictionaries, each containing:
                - input_query: The input query that generated the LLM response
                - actual_output: The actual response from the LLM
                - expected_output: (Optional) The expected response for comparison
                - context: (Optional) Context information for factual accuracy checking
            metrics: List of metrics to use (e.g., ["correctness", "factual_accuracy"])
            
        Returns:
            List of dictionaries containing evaluation results for each test case
        """
        if metrics is None:
            metrics = ["correctness"]
        
        results = []
        for i, test_case in enumerate(test_cases):
            try:
                input_query = test_case.get("input_query")
                actual_output = test_case.get("actual_output")
                expected_output = test_case.get("expected_output")
                context = test_case.get("context")
                
                # Skip cases that don't have the minimum required fields
                if not input_query or not actual_output:
                    logging.warning(f"Skipping test case {i}: missing required fields")
                    continue
                
                # Evaluate the response
                result = self.evaluate_response(
                    input_query=input_query,
                    actual_output=actual_output,
                    expected_output=expected_output,
                    context=context,
                    metrics=metrics
                )
                
                results.append(result)
            except Exception as e:
                logging.error(f"Error evaluating test case {i}: {str(e)}")
                results.append({
                    "input": test_case.get("input_query", "Unknown"),
                    "error": str(e)
                })
        
        return results