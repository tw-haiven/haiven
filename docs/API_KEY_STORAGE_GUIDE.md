# API Key Storage Guide

This guide explains how Haiven stores API keys securely and provides best practices for different deployment scenarios, including implementation details for developers.

## 🔐 **Current Implementation**

Haiven uses a secure file-based storage system via the `ApiKeyAuthService` class in `app/auth/api_key_auth_service.py` which interacts with the storage through the `ApiKeyRepository` interface.

### 🛡️ **Security Features:**
- **SHA-256 hashing** - Never stores actual API keys, only hashes
- **Usage tracking** - Monitors when keys are used
- **Expiration** - Keys expire after max 30 days by default
- **Revocation** - Keys can be revoked instantly
- **Audit logging** - All operations are logged
- **In-memory caching** - Reduces file I/O and improves performance

### 📁 **Storage Location:**
Configuration driven. Defaults to file-based storage in the application directory:
```
app/config/api_keys.json
```

### 🔒 **File Structure:**
```json
{
  "keys": {
    "KEY_HASH": {
      "name": "USER DEFINED KEY NAME",
      "user_id": "PSEUDONYMIZED_USER_ID",
      "created_at": "UTC_TIMESTAMP",
      "expires_at": "UTC_TIMESTAMP",
      "last_used": "UTC_TIMESTAMP",
      "usage_count": 0
    }
  }
}
```

## 💾 **Implementation Architecture**

The API key storage system is built with a layered architecture:

### 1. **ApiKeyAuthService** (`app/auth/api_key_auth_service.py`)
- Handles API key generation, validation, and management
- Uses SHA-256 hashing for key security
- Pseudonymizes user IDs for privacy
- Interacts with the repository layer for storage operations

### 2. **ApiKeyRepository Interface** (`app/auth/api_key_repository.py`)
- Abstract interface defining storage operations:
  - `save_key(key_hash, key_data)` - Save a new API key
  - `find_by_hash(key_hash)` - Find a key by its hash
  - `update_key(key_hash, key_data)` - Update key metadata
  - `delete_key(key_hash)` - Delete a key
  - `find_all()` - Get all keys
  - `find_by_user_id(user_id)` - Find keys for a specific user

### 3. **FileApiKeyRepository** (`app/auth/file_api_key_repository.py`)
- Implements the repository interface with file-based storage
- Includes in-memory caching for performance
- Persists data to a JSON file

### 4. **ApiKeyRepositoryFactory** (`app/auth/api_key_repository_factory.py`)
- Factory pattern for creating repository instances
- Implements Singleton pattern to ensure only one instance per type
- Currently, supports "file" repository type
- Designed to support other repository types (e.g., database) in the future

## 🔄 **Caching Implementation**

The `FileApiKeyRepository` class implements a basic in-memory caching mechanism for API keys:

1. **Initialization**: When a `FileApiKeyRepository` instance is created, it loads all API keys from the configured JSON file into an in-memory dictionary (`self.keys`).

2. **Read Operations**: All read operations (`find_by_hash`, `find_all`, `find_by_user_id`) use the in-memory cache without accessing the file system.

3. **Write Operations**: Write operations (`save_key`, `update_key`, `delete_key`) update both the in-memory cache and the file on disk.

This implementation provides several benefits:
- Reduced file I/O for read operations
- Faster access to API key data
- Simple and easy to understand

## 🔧 **Configuration Options**
### 📂 **File Location:**
```yaml
# Example configuration in YAML
api_key_storage:
  type: "file"  # Currently only "file" is supported
  file_path: "app/config/api_keys.json"  # Default storage location
```

### ⏰ **Custom Expiration:**
```python
# Generate key with custom expiration
api_key = manager.generate_api_key(
    name="Long-lived Key",
    user_email="service@example.com",
    expires_days=3  # 3 days instead of default 30
)
```

## 📈 **Future Scaling Options**

When you need to scale beyond ~10,000 keys, consider:

### 🗄️ **Database Storage:**
```python
# Example implementation (not provided)
class DatabaseApiKeyManager:
    def __init__(self, database_url: str):
        self.engine = create_engine(database_url)
        # ... implementation
```

### 🏢 **External Vault:**
```python
# Example implementation (not provided)
class VaultApiKeyManager:
    def __init__(self, vault_url: str, vault_token: str):
        self.vault = hvac.Client(url=vault_url, token=vault_token)
        # ... implementation
```

## 📊 **Monitoring & Alerts**

### 📈 **Usage Monitoring:**
```python
# Monitor key usage
from auth.api_key_auth import get_api_key_manager

manager = get_api_key_manager()
for key_hash, info in manager.keys.items():
    if info['usage_count'] > 10000:
        print(f"High usage key: {info['name']}")
```

### 🚨 **Expiration Alerts:**
```python
# Check for expiring keys
from datetime import datetime, timedelta

manager = get_api_key_manager()
soon = datetime.utcnow() + timedelta(days=30)

for key_hash, info in manager.keys.items():
    expires = datetime.fromisoformat(info['expires_at'])
    if expires < soon:
        print(f"Key expiring soon: {info['name']}")
```

## 📈 **Future Scaling Options**

When you need to scale beyond ~10,000 keys, consider implementing a database-backed repository:

### 🗄️ **Database Repository Implementation Guide:**

To implement a database-backed repository, follow these steps:

1. Create a new class that implements the `ApiKeyRepository` interface:

```python
# app/auth/db_api_key_repository.py
from auth.api_key_repository import ApiKeyRepository
from typing import Dict, Any, Optional
import sqlalchemy as sa
from sqlalchemy.orm import sessionmaker

class DbApiKeyRepository(ApiKeyRepository):
    """Database implementation of API key storage."""

    def __init__(self, config_service):
        """Initialize with database connection from config."""
        db_url = config_service.load_database_url()
        self.engine = sa.create_engine(db_url)
        self.Session = sessionmaker(bind=self.engine)

        # Create tables if they don't exist
        self._create_tables()

    def _create_tables(self):
        """Create necessary database tables if they don't exist."""
        metadata = sa.MetaData()

        # Define API keys table
        self.api_keys = sa.Table(
            'api_keys', metadata,
            sa.Column('key_hash', sa.String(64), primary_key=True),
            sa.Column('name', sa.String(255), nullable=False),
            sa.Column('user_id', sa.String(64), nullable=False, index=True),
            sa.Column('created_at', sa.DateTime, nullable=False),
            sa.Column('expires_at', sa.DateTime, nullable=False),
            sa.Column('last_used', sa.DateTime, nullable=True),
            sa.Column('usage_count', sa.Integer, default=0)
        )

        # Create tables
        metadata.create_all(self.engine)

    def save_key(self, key_hash: str, key_data: Dict[str, Any]) -> None:
        """Save an API key with its metadata."""
        with self.Session() as session:
            session.execute(
                self.api_keys.insert().values(
                    key_hash=key_hash,
                    name=key_data['name'],
                    user_id=key_data['user_id'],
                    created_at=key_data['created_at'],
                    expires_at=key_data['expires_at'],
                    last_used=key_data['last_used'],
                    usage_count=key_data['usage_count']
                )
            )
            session.commit()

    # Implement other required methods...
```

2. Update the factory to support the new repository type:

```python
# In app/auth/api_key_repository_factory.py
def get_repository(cls, config_service: ConfigService) -> ApiKeyRepository:
    # ...existing code...

    if repo_type == "file":
        from auth.file_api_key_repository import FileApiKeyRepository
        repository = FileApiKeyRepository(config_service)
    elif repo_type == "db":
        from auth.db_api_key_repository import DbApiKeyRepository
        repository = DbApiKeyRepository(config_service)
    else:
        raise NotImplementedError(
            f"API key repository type '{repo_type}' is not implemented."
        )

    # ...existing code...
```

3. Add configuration options to specify the repository type:

```python
# In app/config_service.py
def load_api_key_repository_type(self) -> str:
    """Load the API key repository type from configuration."""
    return self.get_config_value("api_key_repository_type", "file")
```

### 🏢 **External Vault Integration:**

For enhanced security, you can integrate with external secret management systems:

```python
# Example implementation
from auth.api_key_repository import ApiKeyRepository
import hvac

class VaultApiKeyRepository(ApiKeyRepository):
    def __init__(self, config_service):
        """Initialize with Vault connection from config."""
        vault_url = config_service.load_vault_url()
        vault_token = config_service.load_vault_token()
        self.vault = hvac.Client(url=vault_url, token=vault_token)
        self.mount_point = "secret"
        self.path_prefix = "api_keys"

    # Implement required methods...
```

## 🔍 **Potential Improvements**

While the current implementation is effective for most use cases, there are some potential improvements that could be considered:

1. **Delayed or Batch Writes**: Currently, every write operation immediately updates the file on disk. For high-frequency write scenarios, this could be optimized by implementing delayed or batch writes.

2. **Thread Safety**: The current implementation is not explicitly thread-safe. If the repository is accessed from multiple threads, concurrent modifications could lead to race conditions. Adding thread synchronization mechanisms would improve reliability in multi-threaded environments.

3. **Cache Invalidation**: There's no mechanism to detect if the file has been modified by another process. Adding a way to check for external changes and refresh the cache when needed could be beneficial in environments where multiple processes access the same file.

4. **Memory Usage Optimization**: For very large numbers of API keys, it might be worth implementing a more sophisticated caching strategy that limits the number of keys kept in memory.

## 🎯 **Summary**

Haiven's current API key storage is:
- ✅ **Secure** - SHA-256 hashes, no plain text keys
- ✅ **Simple** - File-based, no database required
- ✅ **Performant** - In-memory caching reduces file I/O
- ✅ **Cloud-agnostic** - Works on any platform
- ✅ **Auditable** - Full logging and usage tracking
- ✅ **Scalable** - Handles thousands of keys efficiently
- ✅ **Extensible** - Designed to support different storage backends

The existing implementation is production-ready and secure. Focus on proper deployment practices and file permissions rather than changing the storage mechanism unless you have specific scaling requirements.
