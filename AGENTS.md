# AGENTS.md - Agentic Coding Guidelines for cc-transaction-logger

## Project Overview

Python application that automatically logs credit card transactions by extracting data from notification emails and storing them in Google Sheets.

## Build/Lint/Test Commands

### Core Commands
```bash
# Run main application
uv run main.py

# Test a specific merchant extractor (interactive testing)
uv run python test_extractor.py <merchant> [days_back]
# Examples:
uv run python test_extractor.py Foodpanda
uv run python test_extractor.py Grab 7
uv run python test_extractor.py Metrobank 14

# Run pytest tests
uv run pytest

# Run pytest on specific test file
uv run pytest test_extractor.py

# Run pytest with verbose output and single test
uv run pytest -v test_extractor.py::test_function_name

# Run pytest with coverage
uv run pytest --cov=utils --cov-report=term-missing
```

### Environment Setup
```bash
# Install dependencies (requires uv package manager)
pip install uv
uv sync

# Copy example env and configure
cp .env.example .env
# Edit .env with your credentials
```

## Code Style Guidelines

### Imports
- **Order**: Standard library → third-party → local imports
- **Format**: Separate blocks with blank lines
```python
import os
import re
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Callable, Dict, Optional

import pandas as pd
from bs4 import BeautifulSoup

from utils.extractors.base import BaseEmailExtractor, TransactionData
```

### Type Hints
- Use modern syntax (Python 3.10+): `list[str]`, `str | None`
- Always type function parameters and return values
- Use `Optional[T]` or `T | None` for nullable types
- Dataclasses should have type annotations for all fields

### Naming Conventions
- **Classes**: `PascalCase` (e.g., `FoodpandaEmailExtractor`, `TransactionData`)
- **Functions/Methods**: `snake_case` (e.g., `extract_payment_info`, `register_extractors`)
- **Constants**: `UPPER_SNAKE_CASE` (e.g., `NICKNAME`, `STATEMENT_DATE`)
- **Private members**: Single underscore prefix (e.g., `_extract_order_confirmation_html`)
- **Extractor classes**: `{Merchant}EmailExtractor` suffix pattern

### Class Structure
```python
class BaseEmailExtractor(ABC):
    def __init__(self, merchant_email: str):
        super().__init__()
        self.merchant_email = merchant_email
        self.html_extractors: Dict[str, Callable] = {}
        self.text_extractors: Dict[str, Callable] = {}
        self.register_extractors()

    @abstractmethod
    def register_extractors(self) -> None:
        pass
```

### Error Handling
- Use try-except blocks in extraction methods
- Return `TransactionData()` (empty) on failure instead of raising
- Print errors to help with debugging
- Validate inputs early, raise `ValueError` for invalid merchant names
```python
try:
    # extraction logic
    return TransactionData(...)
except Exception as e:
    print(f"Error extracting transaction: {e}")
    return TransactionData()
```

### Documentation
- Use docstrings for all public methods and classes
- Document Args, Returns, and purpose
- Follow Google style docstrings
- Add inline comments for complex logic

### TransactionData Class
```python
@dataclass
class TransactionData:
    card_number: Optional[str] = None
    amount: Optional[float] = None
    merchant: Optional[str] = None
    category: Optional[str] = None
```

### Adding New Merchants
1. Create new extractor in `utils/extractors/{merchant}.py`
2. Inherit from `BaseEmailExtractor`
3. Implement `register_extractors()` method
4. Add to `EXTRACTOR_REGISTRY` in `utils/extractors/__init__.py`
5. Test with `test_extractor.py`

### File Organization
- `main.py`: Entry point, orchestrates workflow
- `cards/`: Credit card configurations (one per card)
- `utils/`: Core utilities
- `utils/extractors/`: Merchant-specific extractors
- `utils/gmail.py`: Gmail API client
- `utils/googlesheets.py`: Google Sheets API client
- `test_extractor.py`: Interactive testing tool

## Key Patterns

### Extractor Registration Pattern
```python
def register_extractors(self) -> None:
    self.html_extractors = {
        "SubjectPattern": self._extraction_method,
    }
    self.text_extractors = {
        "SubjectPattern": self._extraction_method,
    }
```

### Extraction Method Pattern
```python
def _extract_method(self, soup: BeautifulSoup, subject: str | None = None) -> TransactionData:
    if subject not in expected_subjects:
        return TransactionData()
    try:
        # extraction logic using regex, BeautifulSoup, etc.
        return TransactionData(card_number=..., amount=..., ...)
    except Exception as e:
        print(f"Error: {e}")
        return TransactionData()
```

## Dependencies
- `beautifulsoup4`: HTML parsing
- `gspread`: Google Sheets API
- `pandas`: Data manipulation
- `python-dotenv`: Environment variables
- `pytest`: Testing
