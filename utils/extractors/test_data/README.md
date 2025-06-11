# Email Extractor Test Data

This directory contains test data templates and utilities for testing email extractors.

## Structure

- `__init__.py` - Package initialization file that lists available test modules
- `conftest.py` - Pytest configuration for extractor tests
- `test_extractors.py` - Pytest tests for extractors
- `*_email_template.py` - Template files for each merchant (e.g., `foodpanda_email_template.py`)

## How to Use

### Running Tests with Pytest

To run the tests with pytest:

```bash
# Install pytest and pytest-cov if not already installed
uv add pytest

# Run tests from the project root
uv run pytest utils/extractors/test_data/test_extractors.py -v
```

### Adding New Test Templates

1. Create a new file named `{merchant}_email_template.py`
2. Follow the structure of existing templates:
   - Define email data in a dictionary with `from`, `subject`, `date`, and `body`
   - Define expected extraction results
   - Implement a `get_test_data()` function
3. Add the template name to `available_tests` in `__init__.py`

Example template structure:
```python
"""
Test data template for {Merchant} emails.
"""

# Sample email with subject
MERCHANT_EMAIL = {
    "from": "example@merchant.com",
    "subject": "Your Transaction",
    "date": "2023-01-01",
    "body": """
    Email content here...
    """
}

# Expected extraction results
EXPECTED_RESULTS = {
    "card_number": "1234",
    "amount": 100.00,
    "merchant": "Merchant Name"
}

def get_test_data():
    return {
        "email": MERCHANT_EMAIL,
        "expected": EXPECTED_RESULTS
    }
```

## Benefits

- Test extractors without real emails
- Ensure extractors continue to work after code changes
- Document expected behavior for each extractor
- Make it easier to add new extractors
- Automated testing with pytest 