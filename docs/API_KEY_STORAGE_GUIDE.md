# API Key Storage Guide

This guide explains how Haiven stores API keys securely and provides best practices for different deployment scenarios.

## 🔐 **Current Implementation**

Haiven uses a secure file-based storage system via the `ApiKeyManager` class in `app/auth/api_key_auth.py`.

### 🛡️ **Security Features:**
- **SHA-256 hashing** - Never stores actual API keys, only hashes
- **Usage tracking** - Monitors when keys are used
- **Expiration** - Keys expire after 365 days by default
- **Revocation** - Keys can be revoked instantly
- **Audit logging** - All operations are logged

### 📁 **Storage Location:**
```
app/config/api_keys.json
```

### 🔒 **File Structure:**
```json
{
  "keys": {
    "sha256_hash": {
      "name": "My API Key",
      "user_email": "user@example.com",
      "created_at": "2025-01-01T00:00:00.000000",
      "expires_at": "2025-12-31T23:59:59.999999",
      "last_used": "2025-01-01T12:00:00.000000",
      "usage_count": 42
    }
  }
}
```

## 🚀 **Deployment Best Practices**

### 🐳 **Docker Deployment:**
```dockerfile
# Dockerfile
FROM python:3.11-slim

# Create secure directory for API keys
RUN mkdir -p /app/config && chmod 700 /app/config

# Copy application
COPY . /app
WORKDIR /app

# Set file permissions
RUN chown -R app:app /app/config

USER app
```

```yaml
# docker-compose.yml
version: '3.8'
services:
  haiven:
    image: haiven:latest
    volumes:
      - haiven-config:/app/config
    environment:
      - PYTHONPATH=/app
volumes:
  haiven-config:
```

### ☸️ **Kubernetes Deployment:**
```yaml
# persistent-volume.yaml
apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: haiven-config-pvc
spec:
  accessModes:
    - ReadWriteOnce
  resources:
    requests:
      storage: 1Gi

---
# deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: haiven
spec:
  template:
    spec:
      containers:
      - name: haiven
        image: haiven:latest
        volumeMounts:
        - name: config
          mountPath: /app/config
        securityContext:
          runAsNonRoot: true
          runAsUser: 1000
          fsGroup: 1000
      volumes:
      - name: config
        persistentVolumeClaim:
          claimName: haiven-config-pvc
```

### 🌐 **Cloud Deployment:**

#### **AWS:**
```bash
# Use EFS for persistent storage
aws efs create-file-system --creation-token haiven-config
```

#### **Azure:**
```bash
# Use Azure Files
az storage share create --name haiven-config --account-name mystorageaccount
```

#### **Google Cloud:**
```bash
# Use Cloud Storage FUSE
gcsfuse haiven-config /app/config
```

## 🔒 **Security Hardening**

### 📂 **File Permissions:**
```bash
# Set secure permissions
chmod 600 /app/config/api_keys.json
chown app:app /app/config/api_keys.json
```

### 🔐 **Access Control:**
```bash
# Restrict directory access
chmod 700 /app/config
```

### 📋 **Backup Strategy:**
```bash
#!/bin/bash
# backup-api-keys.sh
DATE=$(date +%Y%m%d_%H%M%S)
cp /app/config/api_keys.json /app/backups/api_keys_${DATE}.json
find /app/backups/ -name "api_keys_*.json" -mtime +30 -delete
```

### 🔄 **Key Rotation:**
```bash
# Rotate keys older than 90 days
python -c "
from auth.api_key_auth import get_api_key_manager
from datetime import datetime, timedelta

manager = get_api_key_manager()
cutoff = datetime.utcnow() - timedelta(days=90)

for key_hash, info in manager.keys.items():
    created = datetime.fromisoformat(info['created_at'])
    if created < cutoff:
        print(f'Key {info["name"]} needs rotation')
"
```

## 🔧 **Configuration Options**

### 📍 **Custom Storage Path:**
```python
# In your application code
from auth.api_key_auth import ApiKeyManager

# Use custom path
manager = ApiKeyManager(config_path="/custom/path/api_keys.json")
```

### ⏰ **Custom Expiration:**
```python
# Generate key with custom expiration
api_key = manager.generate_api_key(
    name="Long-lived Key",
    user_email="service@example.com",
    expires_days=30  # 30 days instead of default 365
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

## 🎯 **Summary**

Haiven's current API key storage is:
- ✅ **Secure** - SHA-256 hashes, no plain text keys
- ✅ **Simple** - File-based, no database required
- ✅ **Cloud-agnostic** - Works on any platform
- ✅ **Auditable** - Full logging and usage tracking
- ✅ **Scalable** - Handles thousands of keys efficiently

The existing implementation is production-ready and secure. Focus on proper deployment practices and file permissions rather than changing the storage mechanism. 