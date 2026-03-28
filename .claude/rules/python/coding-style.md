# Python Coding Style

> This file extends [common/coding-style.md](../common/coding-style.md) with Python specifics.

## PEP 8 Compliance

- 4 spaces for indentation (not tabs)
- Max line length: 88 characters (Black formatter standard)
- 2 blank lines between top-level functions/classes
- 1 blank line between methods

## Type Hints

Always use type hints:

```python
# WRONG: No type hints
def process_user(data):
    return {"name": data["name"]}

# CORRECT: Full type hints
from typing import Dict, Any

def process_user(data: Dict[str, Any]) -> Dict[str, str]:
    return {"name": data["name"]}
```

## Context Managers

Use context managers for resource management:

```python
# WRONG: Manual cleanup
f = open('file.txt')
content = f.read()
f.close()

# CORRECT: Automatic cleanup
with open('file.txt') as f:
    content = f.read()
```

## List Comprehensions

Prefer comprehensions for clarity:

```python
# OK: Loop
result = []
for item in items:
    if item > 5:
        result.append(item * 2)

# BETTER: Comprehension
result = [item * 2 for item in items if item > 5]
```

## Error Handling

Catch specific exceptions:

```python
# WRONG: Too broad
try:
    operation()
except:
    pass

# CORRECT: Specific exception
try:
    operation()
except ValueError as e:
    logger.error(f"Invalid value: {e}")
    raise
```

## Logging

Use logging module, never print():

```python
import logging

logger = logging.getLogger(__name__)

logger.info("User created")
logger.error(f"Failed to process: {e}")
```
