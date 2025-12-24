# Tests Directory

This directory contains all test files for the PublicLens project.

## Test Files

### Python Tests
- **test_crud.py** - Tests CRUD operations for the database layer
- **test_db.py** - Tests database connection and basic operations
- **test_e2e.py** - End-to-end integration tests
- **test_integration.py** - Integration tests for notification and Jac flow

### Jac Tests
- **test.jac** - General Jac tests
- **test_models.jac** - Model tests for Jac
- **test_spawn.jac** - Spawn functionality tests

## Running Tests

### Python Tests
Make sure you have the required dependencies installed:
```bash
pip install -r backend/python/requirements.txt
```

Then run individual tests:
```bash
python3 tests/test_crud.py
python3 tests/test_db.py
python3 tests/test_e2e.py
python3 tests/test_integration.py
```

### Jac Tests
Run Jac tests using the Jac runtime:
```bash
jac run tests/test.jac
jac run tests/test_models.jac
jac run tests/test_spawn.jac
```

## Notes
- Python tests automatically add the `backend/python` directory to the path
- Make sure services are running before executing integration and e2e tests
- Database tests require a properly configured PostgreSQL database
