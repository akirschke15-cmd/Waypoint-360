---
name: python-patterns
description: Pythonic idioms, PEP 8 standards, type hints, error handling, context managers, comprehensions, generators, dataclasses, decorators, concurrency patterns, and package organization.
origin: ECC
version: 2.0
---

# Python Patterns Skill

Production-grade Python patterns following PEP 8 and modern best practices.

## When to Activate

- Writing Python code (API, data processing, automation)
- Reviewing Python code
- Establishing team Python standards
- Refactoring legacy Python code
- Optimizing performance

## Naming Conventions

```python
# GOOD: lowercase with underscores (PEP 8)
user_name = "Alice"
get_user_by_id = lambda x: x
MAX_RETRIES = 3

# GOOD: classes PascalCase
class UserRepository:
    pass

# GOOD: private with underscore prefix
_internal_value = None

def _helper_function():
    pass

# BAD: camelCase
userName = "Alice"
getUser = lambda x: x

# BAD: UPPER_CASE for non-constants
MAX_TRIES = 3  # only if truly constant
```

## Type Hints

Always use type hints.

```python
from typing import Optional, List, Dict, Callable, Union
from dataclasses import dataclass

# GOOD: function types
def get_user(user_id: str) -> Optional[User]:
    pass

def process_items(items: List[str]) -> Dict[str, int]:
    return {item: len(item) for item in items}

def callback_handler(func: Callable[[str], bool]) -> None:
    pass

# GOOD: complex types
def fetch_data(
    url: str,
    timeout: float = 10.0,
    headers: Optional[Dict[str, str]] = None
) -> Dict[str, any]:
    pass

# GOOD: union types (Python 3.10+)
def process(value: str | int | None) -> bool:
    pass

# BAD: no type hints
def get_user(user_id):
    pass

# BAD: generic any
def process(data: any) -> any:
    pass
```

## Dataclasses

```python
from dataclasses import dataclass, field
from typing import List

@dataclass
class User:
    id: str
    name: str
    email: str
    tags: List[str] = field(default_factory=list)
    is_active: bool = True

    def __post_init__(self):
        """Validation after initialization"""
        if not self.email:
            raise ValueError("Email required")

# Usage
user = User(id="123", name="Alice", email="alice@example.com")
print(user)  # User(id='123', name='Alice', email='alice@example.com', ...)
```

## Error Handling

```python
# GOOD: custom exceptions
class ValidationError(Exception):
    pass

class UserNotFoundError(Exception):
    pass

# GOOD: specific exception handling
def create_user(email: str) -> User:
    if not email:
        raise ValidationError("Email required")

    existing = find_user_by_email(email)
    if existing:
        raise ValidationError("Email already registered")

    return User(email=email)

# GOOD: catch specific errors
try:
    user = create_user(email)
except ValidationError as e:
    print(f"Validation failed: {e}")
except Exception as e:
    logger.error(f"Unexpected error: {e}", exc_info=True)
    raise

# BAD: bare except (swallows errors)
try:
    risky_operation()
except:
    pass  # Silent failure!

# BAD: too broad
try:
    user = create_user(email)
except Exception:
    print("Error occurred")
```

## Context Managers

```python
from contextlib import contextmanager

# GOOD: built-in context manager
with open('file.txt') as f:
    content = f.read()

# GOOD: custom context manager
@contextmanager
def database_connection(host: str, port: int):
    db = connect(host, port)
    try:
        yield db
    finally:
        db.close()

# Usage
with database_connection('localhost', 5432) as db:
    user = db.query('SELECT * FROM users')

# GOOD: class-based context manager
class Transaction:
    def __init__(self, db):
        self.db = db

    def __enter__(self):
        self.db.begin()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_type:
            self.db.rollback()
        else:
            self.db.commit()

# Usage
with Transaction(db) as tx:
    tx.db.execute('INSERT ...')
    tx.db.execute('UPDATE ...')
```

## Comprehensions & Generators

```python
# GOOD: list comprehension (readable)
squares = [x**2 for x in range(10)]

# GOOD: list comprehension with condition
evens = [x for x in range(10) if x % 2 == 0]

# GOOD: dict comprehension
user_map = {user.id: user for user in users}

# GOOD: set comprehension
unique_tags = {tag for user in users for tag in user.tags}

# GOOD: generator (memory-efficient)
def generate_numbers(n: int):
    for i in range(n):
        yield i**2

# GOOD: generator expression
squares = (x**2 for x in range(10))

# BAD: list when generator would suffice
def process_large_file(filename: str):
    all_lines = [line for line in open(filename)]  # loads all into memory
    for line in all_lines:
        process(line)

# GOOD: generator for large files
def process_large_file(filename: str):
    with open(filename) as f:
        for line in f:  # lazy iteration
            process(line)
```

## Decorators

```python
from functools import wraps
import time

# GOOD: timer decorator
def timer(func: Callable) -> Callable:
    @wraps(func)  # preserves function metadata
    def wrapper(*args, **kwargs):
        start = time.time()
        result = func(*args, **kwargs)
        duration = time.time() - start
        print(f"{func.__name__} took {duration:.3f}s")
        return result
    return wrapper

@timer
def slow_function():
    time.sleep(1)

# GOOD: retry decorator
def retry(max_attempts: int = 3, delay: float = 1.0):
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            for attempt in range(max_attempts):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    if attempt == max_attempts - 1:
                        raise
                    time.sleep(delay)
        return wrapper
    return decorator

@retry(max_attempts=3, delay=0.5)
def unreliable_operation():
    pass
```

## Async/Await

```python
import asyncio

# GOOD: async function
async def fetch_user(user_id: str) -> User:
    async with aiohttp.ClientSession() as session:
        async with session.get(f'/api/users/{user_id}') as resp:
            data = await resp.json()
            return User(**data)

# GOOD: gather parallel requests
async def load_users(user_ids: List[str]) -> List[User]:
    tasks = [fetch_user(uid) for uid in user_ids]
    return await asyncio.gather(*tasks)

# GOOD: with timeout
async def fetch_with_timeout(url: str, timeout: float = 10.0):
    try:
        return await asyncio.wait_for(fetch(url), timeout)
    except asyncio.TimeoutError:
        logger.error(f"Request to {url} timed out")
        raise

# GOOD: run async code from sync
result = asyncio.run(fetch_user('123'))

# BAD: blocking in async function
async def fetch_data(url: str):
    response = requests.get(url)  # blocks! use aiohttp instead
    return response.json()
```

## Class Patterns

```python
# GOOD: inheritance for behavior
class Repository:
    def __init__(self, db):
        self.db = db

    def get(self, id: str):
        return self.db.query(f'SELECT * WHERE id = {id}')

class UserRepository(Repository):
    def get_by_email(self, email: str):
        return self.db.query(f'SELECT * FROM users WHERE email = {email}')

# GOOD: composition over inheritance
@dataclass
class UserService:
    repository: UserRepository
    cache: Cache

    def get_user(self, user_id: str) -> Optional[User]:
        cached = self.cache.get(user_id)
        if cached:
            return cached
        user = self.repository.get(user_id)
        if user:
            self.cache.set(user_id, user)
        return user
```

## Package Organization

```
my_project/
├── setup.py                  # Package metadata
├── pyproject.toml           # Modern Python packaging
├── requirements.txt         # Production dependencies
├── requirements-dev.txt     # Dev dependencies
├── README.md
├── .gitignore
├── my_project/
│   ├── __init__.py
│   ├── __main__.py          # python -m my_project
│   ├── api/
│   │   ├── __init__.py
│   │   ├── routes.py
│   │   └── handlers.py
│   ├── models/
│   │   ├── __init__.py
│   │   ├── user.py
│   │   └── schemas.py
│   ├── services/
│   │   ├── __init__.py
│   │   ├── user_service.py
│   │   └── email_service.py
│   ├── repositories/
│   │   ├── __init__.py
│   │   └── user_repository.py
│   ├── config.py
│   ├── logger.py
│   └── utils.py
└── tests/
    ├── __init__.py
    ├── conftest.py          # pytest fixtures
    ├── unit/
    │   ├── test_user_service.py
    │   └── test_repositories.py
    └── integration/
        └── test_api.py
```

## Logging

```python
import logging

# GOOD: configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)

# GOOD: use logger
logger.info(f"User {user_id} created")
logger.warning(f"Retry attempt {attempt}")
logger.error(f"Failed to fetch {url}", exc_info=True)

# BAD: print statements
print("User created")  # no timestamp, level, or context

# BAD: string formatting in log calls
logger.info(f"User {user.id} {user.name} {user.email}")
# Instead: logger.info("User created", extra={'user_id': user.id, 'name': user.name})
```

## Testing Best Practices

```python
import pytest

# GOOD: fixtures for reusable setup
@pytest.fixture
def user():
    return User(id='123', name='Alice', email='alice@example.com')

@pytest.fixture
def mock_repository(mocker):
    return mocker.Mock(spec=UserRepository)

# GOOD: parametrize tests
@pytest.mark.parametrize('email,expected', [
    ('valid@example.com', True),
    ('invalid-email', False),
    ('', False),
])
def test_email_validation(email, expected):
    assert validate_email(email) == expected

# GOOD: clear test names
def test_create_user_with_valid_email(user):
    assert user.email == 'alice@example.com'

def test_create_user_rejects_invalid_email():
    with pytest.raises(ValidationError):
        create_user(email='invalid-email')

# BAD: unclear test names
def test_user():
    pass

def test_email():
    pass
```

## Production Checklist

- [x] Type hints on all functions
- [x] Docstrings for public functions
- [x] Custom exceptions for error cases
- [x] Proper logging (not print)
- [x] Async for I/O operations
- [x] Context managers for resource cleanup
- [x] Tests cover happy path + errors
- [x] PEP 8 compliant (use black, flake8)
- [x] No hardcoded secrets
- [x] Proper package structure
- [x] Setup.py or pyproject.toml
- [x] Requirements files pinned
