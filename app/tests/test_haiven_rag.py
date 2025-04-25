# © 2024 Thoughtworks, Inc. | Licensed under the Apache License, Version 2.0  | See LICENSE.md file for permissions.
from langchain_aws import ChatBedrockConverse
from langchain_openai import AzureOpenAIEmbeddings
import numpy as np
from ragas.llms import LangchainLLMWrapper
from ragas.embeddings import LangchainEmbeddingsWrapper
from ragas.dataset_schema import SingleTurnSample
from ragas import evaluate
from ragas.metrics import LLMContextRecall, Faithfulness, FactualCorrectness, ContextRelevance, ContextPrecision, ResponseRelevancy
from ragas import EvaluationDataset
import csv
import json
import os
import pandas as pd
import ast

# AWS Bedrock Claude Sonnet 3.7
bedrock_llm = ChatBedrockConverse(
    region_name="us-east-1",
    model="us.anthropic.claude-3-7-sonnet-20250219-v1:0",
    temperature=0.5,
)
evaluator_llm = LangchainLLMWrapper(bedrock_llm)

# text-embedding-ada-002 Open AI embedding
evaluator_embeddings = LangchainEmbeddingsWrapper(AzureOpenAIEmbeddings(
    openai_api_version="2023-05-15",
    azure_endpoint="https://genai-pod-teamai-ai-aiservices197713008.openai.azure.com",
    azure_deployment="text-embedding-ada-002",
    model="text-embedding-ada-002",
))

def load_sample_from_csv():
    """Load sample data from CSV file"""
    csv_file_path = os.path.join(os.path.dirname(__file__), 'test_data', 'RAG test scenarios - RAGAS Dataset.csv')
    
    with open(csv_file_path, 'r', newline='') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            return SingleTurnSample(
                user_input=row['question'],
                response=row['llm_response'],
                reference=row["ground_truth"],
                retrieved_contexts=ast.literal_eval(row["contexts"])
            )
    
    # If no sample found, raise an error
    raise ValueError("No sample data found in CSV file")

sample = load_sample_from_csv()

def evaluate_custom(metric):
    metric_instance = metric(llm=evaluator_llm)
    score = metric_instance.single_turn_score(sample)
    if isinstance(score, np.floating):
        score = float(score)
    return score

def create_dataset():
    try:
        df = pd.read_csv(os.path.join(os.path.dirname(__file__), 'test_data', 'RAG test scenarios - RAGAS Dataset.csv'))    

        dataset = []
        for index, row in df.iterrows():
            dataset.append({
                "user_input": row["question"],
                "response": row["llm_response"],
                "retrieved_contexts": ast.literal_eval(row["contexts"]),
                "reference": row["ground_truth"]
            })  

    except FileNotFoundError:
        print("Error: CSV not found. Please upload and save the file first.")
    except KeyError as e:
        print(f"Error: Column header '{e}' not found in the file.")
    except Exception as e:
        print(f"An error occurred: {e}")  
    return dataset

def test_retrieval_metrics_from_dataset():
    dataset = create_dataset()  
    evaluation_dataset = EvaluationDataset.from_list(dataset)

    result = evaluate(dataset=evaluation_dataset,
                      metrics=[ContextPrecision(), LLMContextRecall(), ContextRelevance()],
                      llm=evaluator_llm,
                      embeddings=evaluator_embeddings)
    
    # Initialize lists to collect values for each metric
    precision_scores = []
    recall_scores = []
    relevance_scores = []
    
    # Collect scores across all results
    for score in result.scores:
        precision_scores.append(score["context_precision"])
        recall_scores.append(score["context_recall"])
        relevance_scores.append(score["nv_context_relevance"])
    
    # Calculate averages
    avg_precision = sum(precision_scores) / len(precision_scores) if precision_scores else 0
    avg_recall = sum(recall_scores) / len(recall_scores) if recall_scores else 0
    avg_relevance = sum(relevance_scores) / len(relevance_scores) if relevance_scores else 0
    
    print(f"Avg Context Precision: {avg_precision}")
    print(f"Avg Context Recall: {avg_recall}")
    print(f"Avg Context Relevance: {avg_relevance}")
    
    # Assert on the averages
    assert avg_precision >= 1.0
    assert avg_recall >= 1.0
    assert avg_relevance >= 1.0

def test_faithfulness_and_response_relevancy_from_dataset():
    dataset = create_dataset()  
    evaluation_dataset = EvaluationDataset.from_list(dataset)

    result = evaluate(dataset=evaluation_dataset,
                      metrics=[Faithfulness(), ResponseRelevancy()],
                      llm=evaluator_llm,
                      embeddings=evaluator_embeddings)
    
    response_relevancy_scores = []
    faithfulness_scores = []
    
    # Collect scores across all results
    for score in result.scores:
        faithfulness_scores.append(score["faithfulness"])
        response_relevancy_scores.append(score["answer_relevancy"])
    
    # Calculate averages
    avg_faithfulness = sum(faithfulness_scores) / len(faithfulness_scores) if faithfulness_scores else 0
    avg_response_relevancy = sum(response_relevancy_scores) / len(response_relevancy_scores) if response_relevancy_scores else 0
    
    print(f"Avg faithfulness: {avg_faithfulness}")
    print(f"Avg response_relevancy: {avg_response_relevancy}")
    
    # Assert on the averages
    assert avg_faithfulness >= 0.8
    assert avg_response_relevancy >= 2.0

def test_factual_correctness_metrics_from_dataset():
    dataset = create_dataset()  
    evaluation_dataset = EvaluationDataset.from_list(dataset)

    result = evaluate(dataset=evaluation_dataset,
                      metrics=[FactualCorrectness()],
                      llm=evaluator_llm,
                      embeddings=evaluator_embeddings)
    
    factual_correctness_scores = []
    
    # Collect scores across all results
    for score in result.scores:
        factual_correctness_scores.append(score["factual_correctness(mode=f1)"])
    
    # Calculate averages
    avg_factual_correctness = sum(factual_correctness_scores) / len(factual_correctness_scores) if factual_correctness_scores else 0
    
    print(f"Avg factual_correctness(mode=f1): {avg_factual_correctness}")
    
    # Assert on the averages
    assert avg_factual_correctness >= 0.8

# GENERATION METRIC


# FACTUAL CORRECTNESS:  NON_RAG METRIC
# Metric that compares and evaluates the factual accuracy of the generated response with the reference
def test_factual_correctness():

    score = evaluate_custom(FactualCorrectness)
    assert score >= 0.25 

# GENERATION METRIC


# FAITHFULLNESS:
# A response is considered faithful if all claims of llm response can be supported by the retrieved context(factually correct)
def test_faithfulness():
    score = evaluate_custom(Faithfulness)
    assert score >= 0.8 


# RETRIEVAL METRIC


# CONTEXT PRECISION:
#  Indicates how accurately the retrieval system ranks relevant contexts. Context Precision metric evaluates the retriever’s ability
#  to rank relevant chunks higher than irrelevant ones for a given query in the retrieved context.
#  Specifically, it assesses whether the relevant chunks in the retrieved context are prioritized at the top of the ranking.
def test_context_precision():
    score = evaluate_custom(ContextPrecision)
    assert score > 0.0


# RETRIEVAL METRIC


# CONTEXT RECALL:
# Can it retrieve all relevant context required to answer the user question.
# Formula: No of claims in the ground_truth supported by the retrieved contexts / Total no. of claims in the ground_truth
def test_context_recall():
    score = evaluate_custom(LLMContextRecall)
    assert score > 0.3


# RETRIEVAL METRIC


# CONTEXT RELEVANCE:
#  Evaluates how much the relevant **retrieved_contexts** (chunks or passages) are pertinent
#  to the **user_input** (Completely non-relevant chunks are ignored from the score and won't affect the score.
#  Only the chunks which are either completely relevant or partailly relevant are considered for the score calculation).
#  This is done via independent "LLM-as-a-judge" prompt calls that each rate the relevance on a scale of **0, 1, or 2**.
#  The ratings are then converted to a [0,1] scale and averaged to produce the final score.
#  Higher scores indicate that the contexts are more closely aligned with the user's query.
def test_context_relevance():
    score = evaluate_custom(ContextRelevance)
    assert score == 1.0
