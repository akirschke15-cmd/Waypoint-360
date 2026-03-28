---
name: python-testing
description: pytest patterns with fixtures, parametrization, markers, mocking, async tests, exception testing, file operations, test organization, and coverage metrics.
origin: ECC
version: 2.0
---

# Python Testing Skill

pytest patterns for building reliable, maintainable test suites.

## When to Activate

- Writing Python tests with pytest
- Setting up test infrastructure
- Structuring test suites
- Testing async code
- Mocking dependencies

## Project Structure

```
my_project/
├── my_project/
│   ├── __init__.py
│   ├── user.py
│   └── database.py
├── tests/
│   ├── __init__.py
│   ├── conftest.py          # Shared fixtures
│   ├── unit/
│   │   ├── test_user.py
│   │   └── test_database.py
│   └── integration/
│       └── test_api.py
├── pytest.ini               # or pyproject.toml
└── requirements-dev.txt
```

## Basic Test Structure

```python
# tests/unit/test_user.py
import pytest
from my_project.user import User, ValidationError

class TestUser:
    """User model tests"""

    def test_create_user_with_valid_email(self):
        """Should create user with valid email"""
        user = User(id='123', name='Alice', email='alice@example.com')
        assert user.email == 'alice@example.com'

    def test_create_user_rejects_invalid_email(self):
        """Should raise ValidationError for invalid email"""
        with pytest.raises(ValidationError, match='Invalid email'):
            User(id='123', name='Alice', email='invalid-email')

    def test_user_string_representation(self):
        """Should return user name in string representation"""
        user = User(id='123', name='Alice', email='alice@example.com')
        assert str(user) == 'Alice'
```

## Fixtures

Reusable test setup.

```python
# tests/conftest.py
import pytest
from my_project.user import User
from my_project.database import Database

@pytest.fixture
def sample_user():
    """Create a sample user for testing"""
    return User(
        id='123',
        name='Alice',
        email='alice@example.com'
    )

@pytest.fixture
def another_user():
    """Create another sample user"""
    return User(
        id='456',
        name='Bob',
        email='bob@example.com'
    )

@pytest.fixture
def users(sample_user, another_user):
    """Return list of sample users"""
    return [sample_user, another_user]

@pytest.fixture
def mock_db(mocker):
    """Mock database for unit tests"""
    return mocker.Mock(spec=Database)

@pytest.fixture
def real_db():
    """Real database for integration tests"""
    db = Database(':memory:')
    db.connect()
    yield db
    db.close()

# Usage in tests
def test_user_email(sample_user):
    assert sample_user.email == 'alice@example.com'

def test_multiple_users(users):
    assert len(users) == 2
    assert users[0].name == 'Alice'
```

## Parametrization

Test multiple inputs with one test function.

```python
import pytest

@pytest.mark.parametrize('email,expected', [
    ('valid@example.com', True),
    ('invalid-email', False),
    ('user@domain.co.uk', True),
    ('', False),
    ('user@', False),
])
def test_email_validation(email, expected):
    """Test email validation with multiple inputs"""
    from my_project.user import validate_email
    assert validate_email(email) == expected

@pytest.mark.parametrize('name,age', [
    ('Alice', 30),
    ('Bob', 25),
    ('Carol', 35),
])
def test_user_creation(name, age):
    """Test user creation with multiple names and ages"""
    from my_project.user import User
    user = User(id='1', name=name, age=age)
    assert user.name == name
    assert user.age == age

# Parametrize with fixtures
@pytest.mark.parametrize('user_id', ['123', '456', '789'])
def test_user_lookup(user_id, mock_db):
    """Test user lookup for multiple IDs"""
    mock_db.get_user.return_value = User(id=user_id)
    user = mock_db.get_user(user_id)
    assert user.id == user_id
```

## Mocking

Mock external dependencies.

```python
import pytest
from unittest.mock import Mock, patch, MagicMock

def test_user_creation_sends_email(mocker):
    """Test that creating user sends welcome email"""
    # Mock the email service
    mock_email = mocker.patch('my_project.services.send_email')

    from my_project.user import create_user
    create_user(email='alice@example.com')

    # Assert email was called
    mock_email.assert_called_once()
    call_args = mock_email.call_args
    assert 'alice@example.com' in call_args[0]

def test_database_query_with_mock(mocker):
    """Test with mocked database"""
    mock_db = mocker.Mock()
    mock_db.query.return_value = [
        {'id': '1', 'name': 'Alice'},
        {'id': '2', 'name': 'Bob'}
    ]

    result = mock_db.query('SELECT * FROM users')
    assert len(result) == 2

def test_api_call_with_response(mocker):
    """Mock HTTP response"""
    mock_response = mocker.Mock()
    mock_response.status_code = 200
    mock_response.json.return_value = {'id': '123', 'name': 'Alice'}

    mocker.patch('requests.get', return_value=mock_response)

    import requests
    response = requests.get('/api/users/123')
    assert response.json()['name'] == 'Alice'

def test_side_effect_for_sequence(mocker):
    """Mock multiple calls with different returns"""
    mock_fn = mocker.Mock(side_effect=[10, 20, 30])

    assert mock_fn() == 10
    assert mock_fn() == 20
    assert mock_fn() == 30

def test_side_effect_for_exception(mocker):
    """Mock function that raises exception"""
    mock_fn = mocker.Mock(side_effect=ValueError('Invalid'))

    with pytest.raises(ValueError, match='Invalid'):
        mock_fn()
```

## Async Testing

```python
import pytest
import asyncio

@pytest.mark.asyncio
async def test_async_function():
    """Test async function"""
    from my_project.async_utils import fetch_user

    user = await fetch_user('123')
    assert user.id == '123'

@pytest.mark.asyncio
async def test_async_with_timeout():
    """Test async with timeout"""
    async def slow_operation():
        await asyncio.sleep(2)
        return 'done'

    with pytest.raises(asyncio.TimeoutError):
        await asyncio.wait_for(slow_operation(), timeout=0.5)

@pytest.fixture
async def async_fixture():
    """Async fixture for setup/teardown"""
    # Setup
    resource = await setup_resource()
    yield resource
    # Teardown
    await cleanup_resource(resource)

@pytest.mark.asyncio
async def test_with_async_fixture(async_fixture):
    """Test using async fixture"""
    assert async_fixture is not None
```

## Exception Testing

```python
import pytest

def test_raises_specific_exception():
    """Test that function raises specific exception"""
    from my_project.user import create_user

    with pytest.raises(ValueError, match='Invalid email'):
        create_user(email='invalid-email')

def test_raises_any_exception():
    """Test that function raises any exception"""
    def risky_operation():
        raise RuntimeError('Something went wrong')

    with pytest.raises(Exception):
        risky_operation()

def test_exception_info():
    """Capture exception info"""
    with pytest.raises(ValueError) as exc_info:
        raise ValueError('Test error')

    assert 'Test error' in str(exc_info.value)
    assert exc_info.type is ValueError

def test_no_exception():
    """Test that function doesn't raise"""
    from my_project.user import validate_email

    # Should not raise
    assert validate_email('valid@example.com') is True
```

## File Operations Testing

```python
import pytest
import tempfile
import os

@pytest.fixture
def temp_file():
    """Temporary file fixture"""
    fd, path = tempfile.mkstemp()
    yield path
    os.close(fd)
    os.remove(path)

def test_file_operations(temp_file):
    """Test reading/writing files"""
    from my_project.file_utils import read_file, write_file

    write_file(temp_file, 'test content')
    content = read_file(temp_file)

    assert content == 'test content'

@pytest.fixture
def temp_directory():
    """Temporary directory fixture"""
    with tempfile.TemporaryDirectory() as temp_dir:
        yield temp_dir

def test_directory_operations(temp_directory):
    """Test directory operations"""
    test_file = os.path.join(temp_directory, 'test.txt')

    with open(test_file, 'w') as f:
        f.write('content')

    assert os.path.exists(test_file)
```

## Markers

Organize and filter tests.

```python
# tests/conftest.py
import pytest

def pytest_configure(config):
    config.addinivalue_line(
        "markers", "integration: integration tests"
    )
    config.addinivalue_line(
        "markers", "slow: slow tests"
    )
    config.addinivalue_line(
        "markers", "unit: unit tests"
    )

# tests/integration/test_api.py
@pytest.mark.integration
def test_api_endpoint(real_db):
    """Integration test"""
    pass

@pytest.mark.slow
def test_large_dataset():
    """Slow test, skip with -m 'not slow'"""
    pass

# Run commands
# pytest -m unit              # run only unit tests
# pytest -m integration       # run only integration
# pytest -m 'not slow'        # skip slow tests
```

## Coverage

```bash
# Run with coverage
pytest --cov=my_project --cov-report=html

# Measure coverage
pytest --cov=my_project --cov-report=term
```

Configuration in pyproject.toml:
```toml
[tool.pytest.ini_options]
testpaths = ["tests"]
python_files = ["test_*.py"]
addopts = "--cov=my_project --cov-report=term --strict-markers"
markers = [
    "unit: unit tests",
    "integration: integration tests",
    "slow: slow tests"
]

[tool.coverage.run]
branch = true
source = ["my_project"]

[tool.coverage.report]
exclude_lines = [
    "pragma: no cover",
    "def __repr__",
    "raise NotImplementedError",
    "if __name__ == .__main__.:"
]
fail_under = 80
```

## Common Patterns

```python
# Setup and teardown
@pytest.fixture(autouse=True)
def setup_teardown():
    """Run before and after each test"""
    # Setup
    print("Setup")
    yield
    # Teardown
    print("Teardown")

# Skip tests
@pytest.mark.skip(reason="Not implemented yet")
def test_feature():
    pass

@pytest.mark.skipif(os.name == 'nt', reason="Unix only")
def test_unix_only():
    pass

# Expected to fail
@pytest.mark.xfail
def test_known_issue():
    """This test is expected to fail"""
    assert False
```

## Best Practices

- [x] Test names clearly describe what they test
- [x] One assertion per test (or related assertions)
- [x] Use fixtures for common setup
- [x] Mock external dependencies
- [x] Test both happy path and error cases
- [x] Use parametrize for multiple inputs
- [x] Isolate tests (no shared state)
- [x] Target >80% coverage
- [x] Run tests automatically (pre-commit, CI/CD)
- [x] Keep tests fast (mock slow operations)
