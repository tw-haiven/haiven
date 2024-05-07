# ADR 3: Implementing local embeddings (HuggingFaceEmbeddings)

## Context

**Our requirements**
- We need to accommodate various methods of computing embeddings for RAG workflows.
- Support for local embeddings is desired for cost efficiency and privacy.
- Flexibility to switch between embeddings without code modification is essential.

**Options**
1. Utilize pretrained models from Hugging Face with a hand coded wrapper for local execution and embedding generation.
2. Leverage built-in support from Langchain through the 'HuggingFaceEmbeddings' component for local embeddings.
3. Exclude local embeddings, relying on cloud-hosted APIs for embedding calculations.

## Decision

Option 3 is chosen. Despite Langchain offering the 'HuggingFaceEmbeddings' component, its integration brings substantial Python dependencies (e.g., pytorch and transformers) and significantly increases the Docker image size (from 500MB to 7GB, reducible to 3GB with optimization). Local execution also demands substantial RAM due to embedding model requirements.

Cloud-hosted models, under regular workloads, proved cost-effective and mitigated the image size and RAM issues. However, to facilitate future support for local embeddings or new cloud API embeddings, a provider component is introduced in the code to deliver embeddings based on configuration.


## Consequences

- Presently, local embedding generation is not supported.
- Docker image is streamlined, demanding less RAM, as embedding calculations are outsourced.

**Trade-offs**

- A privacy-focused client might request local embedding support in the future, necessitating code modifications and potential vertical scaling.
- The use of cloud-hosted models for embedding generation is time-intensive, impacting the 'on-the-fly RAG' feature's performance. While cost is not a primary concern, large text file uploads could lead to network timeouts; implementing a character-based limit is recommended.