# ADR 006: We are adopting Firestore as the backend for API key storage

*This ADR was generated using the Haiven ADR prompt and reflects a thorough analysis of requirements, codebase usage, cost, and technical fit as of July 2025.* 

## Decision Summary
We are migrating our API key storage from a local file-based repository to Google Firestore. This decision is driven by the need for secure, scalable, and atomic storage that supports high-frequency, concurrent operations, while remaining cost-effective and easy to integrate with our existing codebase.

## Context
- **Status quo:**
  - API keys and metadata are stored in a local JSON file, accessed via a repository pattern.
  - This approach is simple and works for development/testing, but is not safe for concurrent updates or distributed deployments.
- **Goals and requirements:**
  - Use a Google Cloud-based storage solution (GCS, Firestore, or Cloud SQL/Postgres)
  - Ensure secure storage of sensitive API keys
  - Support atomic and concurrent updates (e.g., incrementing usage count, updating last-used timestamp)
  - Enable efficient high read/write operations for LLM/API usage
  - Keep operational overhead and costs low
  - Allow easy integration with the current repository interface
  - Versioning is not a hard requirement
- **Business impact:**
  - Enables us to scale API key management as usage grows
  - Reduces risk of data loss or race conditions
  - Supports future cloud-native deployments

## Options Considered

### 1. Do nothing (keep file-based storage)
- **Consequences:**
  - Positive: No migration effort, no new costs
  - Negative: Not safe for concurrent updates, not scalable, not suitable for production, risk of data loss/corruption, not cloud-native

### 2. Google Cloud Storage (GCS)
- **Description:** Store each API key as a JSON object in a GCS bucket
- **Consequences:**
  - Positive: Simple, cheap for storage, easy to use for static/infrequent updates
  - Negative: No built-in atomic updates, risk of race conditions, not recommended for high-frequency or concurrent operations

### 3. Firestore (NoSQL, Chosen Option)
- **Description:** Store each API key as a document in a Firestore collection
- **Consequences:**
  - Positive: Supports atomic field increments and transactions, safe for concurrent updates, pay-as-you-go, no server management, fine-grained security rules, easy integration
  - Negative: Costs can rise with very high ops, not SQL
  - **Suggested schema:**
    - Collection: `api_keys`
    - Document ID: key hash
    - Fields: `name`, `user_id`, `created_at`, `expires_at`, `last_used`, `usage_count`
    - Composite index: `user_id` + `created_at` for efficient user-based queries

### 4. Cloud SQL (Postgres)
- **Description:** Store each API key as a row in a Postgres table
- **Consequences:**
  - Positive: Full SQL, transactions for atomicity, good for complex queries, predictable cost at scale
  - Negative: Higher base cost, more operational overhead, less elastic scaling
  - **Suggested schema:**
    - Table: `api_keys`
    - Columns: `key_hash` (PK), `name`, `user_id`, `created_at`, `expires_at`, `last_used`, `usage_count`

## Cost Comparison (2024)
| Option     | Storage Cost | Read Cost (1M) | Write Cost (1M) | Base/Instance Cost | Atomicity/Concurrency |
|------------|-------------|----------------|-----------------|--------------------|----------------------|
| GCS        | $0.02/GB    | $0.40          | $5.00           | None               | No                   |
| Firestore  | $0.15/GB    | $0.30          | $0.90           | None               | Yes                  |
| Cloud SQL  | $0.24/GB    | Included       | Included        | ~$30–$50/month     | Yes                  |

## Who Should Be Consulted
- DevOps/Cloud infrastructure team (for provisioning and securing Firestore)
- Security team (for access control and compliance)
- Backend/API developers (for repository implementation and migration)
- Product owner/leadership (for business impact and cost monitoring)

## Reasons and Rationale
- We need atomic, concurrent-safe updates for API key usage tracking, which file-based and GCS solutions cannot provide.
- Firestore offers the best balance of cost, scalability, security, and ease of integration for our current and near-future needs.
- The repository pattern in our codebase allows us to migrate with minimal disruption.
- We retain the file-based implementation for local development and testing.

## Questions for Further Clarification
- Are there any regulatory or compliance requirements that would affect our choice?
- Do we anticipate needing complex SQL queries or reporting on API key data in the future?
- What is our expected scale (peak ops/sec) for API key usage in production?

---