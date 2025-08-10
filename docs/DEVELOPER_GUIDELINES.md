# Developer Guidelines

## Testing

### Slow Integration Tests

Some tests are marked as slow integration tests and are skipped during regular test runs to improve development speed. These tests perform real operations (like Firestore database calls) and can take significant time to complete.

#### Skipped Tests:
- `test_firestore_integration.py` - Tests complete Firestore integration
- `test_json_serialization.py` - Tests JSON serialization with real Firestore operations

#### Running Slow Tests

To run these tests individually:

```bash
# Run Firestore integration test
poetry run pytest test_firestore_integration.py -v

# Run JSON serialization test  
poetry run pytest test_json_serialization.py -v

# Run all slow integration tests
poetry run pytest -m "slow_integration"

# Run all tests (including slow ones) - not recommended for regular development
poetry run pytest
```

**Note:** The regular `poetry run test` command automatically excludes slow integration tests for faster development feedback.

#### When to Run Slow Tests

Run these tests when:
- Making changes to Firestore integration code
- Modifying API key authentication logic
- Testing JSON serialization fixes
- Before deploying to production
- When debugging Firestore-related issues

#### Test Performance

Regular test suite: ~1-2 minutes
With slow tests: ~3-5 minutes

The slow tests are skipped by default to maintain fast feedback during development.

### Test Best Practices

1. **Unit tests should be fast** - Use mocks for external dependencies
2. **Integration tests can be slow** - But should be clearly marked
3. **Use `@pytest.mark.skip`** for tests that shouldn't run in CI
4. **Add clear skip reasons** with instructions on how to run manually 