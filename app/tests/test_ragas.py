# © 2024 Thoughtworks, Inc. | Licensed under the Apache License, Version 2.0  | See LICENSE.md file for permissions.
import os
from langchain_aws import ChatBedrockConverse
from ragas.llms import LangchainLLMWrapper
from ragas.dataset_schema import SingleTurnSample
from ragas.metrics._factual_correctness import FactualCorrectness
from ragas.metrics._faithfulness import Faithfulness
from ragas.metrics import LLMContextRecall, ContextRelevance
from ragas.metrics._context_precision import ContextPrecision

os.environ["AZURE_OPENAI_API_KEY"] = os.environ["OPENAI_API_KEY"]

# AWS Bedrock Claude Sonnet 3.7
bedrock_llm = ChatBedrockConverse(
    region_name="us-east-1",
    model="us.anthropic.claude-3-7-sonnet-20250219-v1:0",
    temperature=0.9,
)
evaluator_llm = LangchainLLMWrapper(bedrock_llm)


# GENERATION METRIC


# FACTUAL CORRECTNESS:  NON_RAG METRIC
# Metric that compares and evaluates the factual accuracy of the generated response with the reference
def test_factual_correctness():
    sample = SingleTurnSample(
        response="capital of France :Paris.",  # LLM Response
        reference="France' capital is Paris",  # ground truth
        user_input="",
    )
    factual_correctness = FactualCorrectness(llm=evaluator_llm)
    score = factual_correctness.single_turn_score(sample)
    assert score == 1.0


# GENERATION METRIC


# FAITHFULLNESS:
# A response is considered faithful if all claims of llm response can be supported by the retrieved context(factually correct)
def test_faithfulness():
    sample = SingleTurnSample(
        response="capital of France :Paris.",
        reference="",
        retrieved_contexts=[
            "The capital of France is Paris..",
            "Eat nutritious food",
            "Do Exercise daily",
        ],
        user_input="",
    )

    faithfulness = Faithfulness(llm=evaluator_llm)
    score = faithfulness.single_turn_score(sample)
    assert score == 1.0


# RETRIEVAL METRIC


# CONTEXT PRECISION:
#  Indicates how accurately the retrieval system ranks relevant contexts. Context Precision metric evaluates the retriever’s ability
#  to rank relevant chunks higher than irrelevant ones for a given query in the retrieved context.
#  Specifically, it assesses whether the relevant chunks in the retrieved context are prioritized at the top of the ranking.
def test_context_precision():
    sample = SingleTurnSample(
        reference="The capital of France is Paris.",
        retrieved_contexts=[
            "The capital of France is Paris",
            "Bahmni is a comprehensive, easy-to-use, and fully open-source Hospital Information System (HIS)",
        ],
        user_input="",
    )

    context_precision = ContextPrecision(llm=evaluator_llm)
    score = context_precision.single_turn_score(sample)
    assert score > 0.95


# RETRIEVAL METRIC


# CONTEXT RECALL:
# Can it retrieve all relevant context required to answer the user question.
# Formula: No of claims in the ground_truth supported by the retrieved contexts / Total no. of claims in the ground_truth
def test_context_recall():
    sample = SingleTurnSample(
        response="capital of France :Paris.",
        reference="The capital of France is Paris. It is a cold country",
        retrieved_contexts=["The capital of France is Paris", "Eat nutritious food"],
        user_input="",
    )

    context_recall = LLMContextRecall(llm=evaluator_llm)
    score = context_recall.single_turn_score(sample)
    assert score == 0.5


# RETRIEVAL METRIC


# CONTEXT RELEVANCE:
#  Evaluates how much the relevant **retrieved_contexts** (chunks or passages) are pertinent
#  to the **user_input** (Completely non-relevant chunks are ignored from the score and won't affect the score.
#  Only the chunks which are either completely relevant or partailly relevant are considered for the score calculation).
#  This is done via independent "LLM-as-a-judge" prompt calls that each rate the relevance on a scale of **0, 1, or 2**.
#  The ratings are then converted to a [0,1] scale and averaged to produce the final score.
#  Higher scores indicate that the contexts are more closely aligned with the user's query.
def test_context_relevance():
    sample = SingleTurnSample(
        user_input="What is the capital of France?",
        retrieved_contexts=[
            "Albert was born in Germany.",
            "Albert Einstein was born at Ulm, in Germany.",
            "capital of France :Paris.",
        ],
    )

    scorer = ContextRelevance(llm=evaluator_llm)
    score = scorer.single_turn_score(sample)
    assert score == 1.0
