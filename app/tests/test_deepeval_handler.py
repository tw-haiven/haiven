# from deepeval import assert_test
# from deepeval.test_case import LLMTestCase, LLMTestCaseParams
# from deepeval.metrics import GEval
# import pytest
# from deepeval_handler import DeepEvalHandler
# import json
# import os

# # Centralized test data - Environmentally friendly living domain
# TEST_INPUT = "What are some simple ways to reduce my carbon footprint at home?"

# TEST_ACTUAL_OUTPUT_CORRECTNESS = (
#     "Reducing your carbon footprint at home can be achieved through several simple practices. "
#     "You can start by reducing energy consumption through LED bulbs, unplugging unused electronics, "
#     "and using energy-efficient appliances. Water conservation is also important - fix leaky faucets "
#     "and take shorter showers. Additionally, reducing waste by composting food scraps and recycling "
#     "properly makes a significant difference."
# )

# TEST_EXPECTED_OUTPUT = (
#     "Reducing your carbon footprint at home can be achieved through several simple practices. "
#     "You can start by reducing energy consumption through LED bulbs, unplugging unused electronics, "
#     "and using energy-efficient appliances. Water conservation is also important - fix leaky faucets "
#     "and take shorter showers. Additionally, reducing waste by composting food scraps, recycling "
#     "properly, and using reusable shopping bags instead of plastic ones makes a significant difference."
# )

# TEST_ACTUAL_OUTPUT_FACTUAL = (
#     "To reduce your carbon footprint at home, switch to LED lighting, use energy-efficient appliances, "
#     "and improve insulation. Conserve water by installing low-flow fixtures and collecting rainwater "
#     "for plants. Reduce waste through composting and recycling, and consider walking or biking for short trips."
# )

# TEST_CONTEXT = [
#     "LED bulbs use 75% less energy than traditional incandescent bulbs.",
#     "Proper insulation can reduce home energy usage by up to 20%.",
#     "Composting food waste reduces methane emissions from landfills.",
#     "Energy-efficient appliances use 10-50% less energy than standard models."
# ]

# # Multiple test cases for batch evaluation with specific contexts for each
# BATCH_TEST_CASES = [
#     {
#         "input_query": "What are some simple ways to reduce my carbon footprint at home?",
#         "actual_output": "Reducing your carbon footprint at home can be achieved through several simple practices like using LED bulbs, unplugging unused electronics, and using energy-efficient appliances.",
#         "expected_output": "Reducing your carbon footprint at home can be achieved through several simple practices like using LED bulbs, unplugging unused electronics, and using energy-efficient appliances. You can also conserve water and reduce waste.",
#         "context": [
#             "LED bulbs use 75% less energy than traditional incandescent bulbs.",
#             "Vampire power (standby power from electronics) accounts for 5-10% of residential electricity use.",
#             "Energy-efficient appliances use 10-50% less energy than standard models.",
#             "Low-flow showerheads can reduce water usage by up to 60%."
#         ]
#     },
#     {
#         "input_query": "How does composting help the environment?",
#         "actual_output": "Composting helps the environment by reducing the amount of waste that goes to landfills, which decreases methane emissions. It also creates nutrient-rich soil for plants.",
#         "expected_output": "Composting helps the environment by reducing the amount of waste that goes to landfills, which decreases methane emissions. It also creates nutrient-rich soil for plants and reduces the need for chemical fertilizers.",
#         "context": [
#             "Food and yard waste make up about 30% of what we throw away.",
#             "Composting food waste reduces methane emissions from landfills.",
#             "Methane is a greenhouse gas 25 times more potent than carbon dioxide.",
#             "Compost improves soil health and reduces the need for chemical fertilizers."
#         ]
#     },
#     {
#         "input_query": "What are the benefits of using renewable energy?",
#         "actual_output": "Renewable energy sources like solar and wind power reduce greenhouse gas emissions, decrease dependence on fossil fuels, and often lead to lower energy costs in the long run.",
#         "expected_output": "Renewable energy sources like solar and wind power reduce greenhouse gas emissions, decrease dependence on fossil fuels, and often lead to lower energy costs in the long run. They also create jobs and improve energy security.",
#         "context": [
#             "Renewable energy generates 28% of global electricity.",
#             "Solar panel costs have fallen by about 90% since 2009.",
#             "Wind power is one of the lowest-priced renewable energy technologies available.",
#             "Renewable energy sources created over three times as many jobs as fossil fuel production."
#         ]
#     },
#     {
#         "input_query": "How can I reduce plastic waste?",
#         "actual_output": "To reduce plastic waste, use reusable bags, bottles, and containers. Avoid single-use plastics and buy products with minimal packaging.",
#         "expected_output": "To reduce plastic waste, use reusable bags, bottles, and containers. Avoid single-use plastics, buy products with minimal packaging, and recycle plastics properly when you do use them.",
#         "context": [
#             "Approximately 8 million metric tons of plastic enter the oceans each year.",
#             "The average American uses 156 plastic bottles annually.",
#             "Only about 9% of all plastic waste ever produced has been recycled.",
#             "Single-use plastic bags have an average usage time of 12 minutes."
#         ]
#     },
#     {
#         "input_query": "What is sustainable transportation?",
#         "actual_output": "Sustainable transportation includes walking, biking, public transit, carpooling, and electric vehicles that minimize environmental impact.",
#         "expected_output": "Sustainable transportation includes walking, biking, public transit, carpooling, and electric vehicles that minimize environmental impact by reducing emissions and conserving resources.",
#         "context": [
#             "Transportation accounts for approximately 29% of greenhouse gas emissions in the US.",
#             "An average passenger vehicle emits about 4.6 metric tons of CO2 per year.",
#             "Electric vehicles produce fewer emissions overall than conventional vehicles.",
#             "Public transportation produces 76% less greenhouse gas emissions per passenger mile than private vehicles."
#         ]
#     },
#     {
#         "input_query": "How does eating less meat help the environment?",
#         "actual_output": "Eating less meat helps the environment by reducing greenhouse gas emissions from livestock farming, which is a major contributor to climate change.",
#         "expected_output": "Eating less meat helps the environment by reducing greenhouse gas emissions from livestock farming, which is a major contributor to climate change. It also reduces water usage and land required for animal agriculture.",
#         "context": [
#             "Livestock accounts for 14.5% of global greenhouse gas emissions.",
#             "Producing one pound of beef requires approximately 1,800 gallons of water.",
#             "Plant-based diets require less land, water, and energy than meat-based diets.",
#             "If cattle were their own nation, they would be the world's third-largest emitter of greenhouse gases."
#         ]
#     },
#     {
#         "input_query": "What are the benefits of planting trees?",
#         "actual_output": "Trees absorb carbon dioxide, provide oxygen, prevent soil erosion, and create habitats for wildlife.",
#         "expected_output": "Trees absorb carbon dioxide, provide oxygen, prevent soil erosion, create habitats for wildlife, and can help reduce energy costs by providing shade.",
#         "context": [
#             "A single mature tree can absorb up to 48 pounds of carbon dioxide per year.",
#             "A single large tree can release enough oxygen for four people daily.",
#             "Trees can reduce erosion by holding soil in place with their root systems.",
#             "Strategically placed trees can reduce home cooling costs by up to 35%."
#         ]
#     },
#     {
#         "input_query": "How can I save water at home?",
#         "actual_output": "You can save water by fixing leaks, taking shorter showers, using water-efficient appliances, and collecting rainwater for plants.",
#         "expected_output": "You can save water by fixing leaks, taking shorter showers, using water-efficient appliances, collecting rainwater for plants, and only running full loads in washing machines and dishwashers.",
#         "context": [
#             "The average American uses 82 gallons of water per day at home.",
#             "A leaky faucet that drips at the rate of one drip per second can waste more than 3,000 gallons per year.",
#             "A full bathtub requires about 70 gallons of water, while a 5-minute shower uses just 10-25 gallons.",
#             "ENERGY STAR certified washing machines use about 33% less water than regular washers."
#         ]
#     },
#     {
#         "input_query": "What is a zero-waste lifestyle?",
#         "actual_output": "A zero-waste lifestyle aims to minimize trash sent to landfills by reducing consumption, reusing items, recycling, and composting.",
#         "expected_output": "A zero-waste lifestyle aims to minimize trash sent to landfills by reducing consumption, reusing items, recycling, composting, and refusing single-use items and unnecessary packaging.",
#         "context": [
#             "The average American produces about 4.5 pounds of waste per day.",
#             "Landfills are the third-largest source of human-related methane emissions in the US.",
#             "The 5 Rs of zero waste are: Refuse, Reduce, Reuse, Recycle, and Rot (compost).",
#             "Only about 35% of municipal solid waste is recycled or composted in the US."
#         ]
#     },
#     {
#         "input_query": "How do energy-efficient appliances help the environment?",
#         "actual_output": "Energy-efficient appliances use less electricity, which reduces greenhouse gas emissions from power plants and lowers utility bills.",
#         "expected_output": "Energy-efficient appliances use less electricity, which reduces greenhouse gas emissions from power plants, lowers utility bills, and decreases overall resource consumption in energy production.",
#         "context": [
#             "Energy-efficient appliances use 10-50% less energy than standard models.",
#             "ENERGY STAR certified products helped Americans save 430 billion kilowatt-hours of electricity in 2019.",
#             "An ENERGY STAR certified refrigerator uses about 9% less energy than models that meet the federal minimum standard.",
#             "If every appliance purchased in the US was ENERGY STAR certified, we would save over $700 million in annual energy costs."
#         ]
#     }
# ]

# def test_correctness():
#     correctness_metric = GEval(
#         name="Correctness",
#         criteria="Determine if the 'actual output' is correct based on the 'expected output'.",
#         evaluation_params=[LLMTestCaseParams.ACTUAL_OUTPUT, LLMTestCaseParams.EXPECTED_OUTPUT],
#         threshold=0.5
#     )
#     test_case = LLMTestCase(
#         input=TEST_INPUT,
#         actual_output=TEST_ACTUAL_OUTPUT_CORRECTNESS,
#         expected_output=TEST_EXPECTED_OUTPUT
#     )
#     assert_test(test_case, [correctness_metric])

# def test_factual_accuracy():
#     """
#     Test factual accuracy using GEval
#     """
#     # Create a GEval metric for factual accuracy with a threshold of 0.5
#     factual_accuracy_metric = GEval(
#         name="Factual Accuracy",
#         criteria="Determine if the LLM response contains factually accurate information based on the provided context.",
#         evaluation_params=[LLMTestCaseParams.ACTUAL_OUTPUT, LLMTestCaseParams.CONTEXT],
#         threshold=0.5
#     )
    
#     # Create the test case
#     test_case = LLMTestCase(
#         input=TEST_INPUT,
#         actual_output=TEST_ACTUAL_OUTPUT_FACTUAL,
#         context=TEST_CONTEXT
#     )
    
#     # Run the assertion
#     assert_test(test_case, [factual_accuracy_metric])

# def test_batch_evaluation():
#     """
#     Test batch evaluation of multiple inputs using DeepEvalHandler with input-specific contexts
#     """
#     handler = DeepEvalHandler()
    
#     # Run batch evaluation with input-specific contexts
#     results = handler.evaluate_batch(
#         test_cases=BATCH_TEST_CASES,
#         metrics=["correctness", "factual_accuracy"]
#     )
    
#     # Check if we have results for all test cases
#     assert len(results) == len(BATCH_TEST_CASES), f"Expected {len(BATCH_TEST_CASES)} results, but got {len(results)}"
    
#     # Check if each result contains evaluation_results
#     for i, result in enumerate(results):
#         assert "evaluation_results" in result, f"Test case {i} missing evaluation_results"
        
#         # Print evaluation scores for each test case
#         print(f"\nTest case {i+1}: {result['input']}")
#         for metric_result in result["evaluation_results"]:
#             print(f"  {metric_result.name}: {metric_result.score}")
    
#     # Save detailed results to a file for further analysis
#     output_path = os.path.join(os.path.dirname(__file__), "batch_evaluation_results.json")
#     with open(output_path, "w") as f:
#         # Convert results to a serializable format
#         serializable_results = []
#         for result in results:
#             serializable_result = {
#                 "input": result["input"],
#                 "actual_output": result["actual_output"],
#                 "expected_output": result["expected_output"],
#                 "metrics": []
#             }
            
#             for metric_result in result["evaluation_results"]:
#                 # Check if score attribute exists and has a value
#                 score = metric_result.score if hasattr(metric_result, "score") else None
                
#                 # Add metric details without relying on the 'passed' attribute
#                 serializable_result["metrics"].append({
#                     "name": metric_result.name,
#                     "score": score,
#                     # Determine passed status based on threshold if possible
#                     "passed": (score is not None and hasattr(metric_result, "threshold") and 
#                               score >= metric_result.threshold) if score is not None else None
#                 })
                
#             serializable_results.append(serializable_result)
            
#         json.dump(serializable_results, f, indent=2)
    
#     print(f"\nSaved detailed results to {output_path}")
#     return True  # Explicitly return True to pass the test