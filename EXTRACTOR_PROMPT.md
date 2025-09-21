# Credit Card Transaction Logger - Extractor Development Prompt

Use this prompt when working with email extractors for the credit card transaction logger repository.

## Repository Overview

This is a Python application that automatically extracts credit card transaction data from notification emails and logs them to Google Sheets. The main workflow:

1. **Fetch emails** from Gmail using IMAP for specific merchants
2. **Extract transaction data** (card number, amount, merchant name) using merchant-specific extractors
3. **Log transactions** to Google Sheets with formatting and validation

## Key Files and Structure

```
├── main.py                           # Main application entry point
├── test_extractor.py                 # Generic tool to test any extractor
├── utils/
│   ├── gmail.py                      # Gmail email fetching
│   ├── googlesheets.py               # Google Sheets operations  
│   └── extractors/
│       ├── __init__.py               # Extractor registry and TransactionExtractor class
│       ├── base.py                   # BaseEmailExtractor abstract class
│       ├── foodpanda.py              # Foodpanda extractor implementation
│       ├── grab.py                   # Grab extractor implementation
│       ├── metrobank.py              # Metrobank extractor implementation
│       └── test_data/
│           ├── __init__.py           # available_tests list
│           ├── conftest.py           # Pytest configuration
│           ├── test_extractors.py    # Automated tests
│           └── *_email_template.py   # Test email templates
```

## How Extractors Work

### 1. Base Architecture
All extractors inherit from `BaseEmailExtractor` in `utils/extractors/base.py`:

```python
class BaseEmailExtractor:
    def __init__(self, merchant_email: str):
        self.merchant_email = merchant_email
        self.html_extractors = {}  # Dict of {subject_pattern: extractor_method}
        self.text_extractors = {}  # Dict of {subject_pattern: extractor_method}
    
    def extract_payment_info(self, email_body: str, email_subject: str) -> TransactionData:
        # Main extraction method - handles both HTML and text emails
        
    def register_extractors(self) -> None:
        # Override this to register subject patterns and extraction methods
```

### 2. TransactionData Structure
Extractors return a `TransactionData` object:
```python
@dataclass
class TransactionData:
    card_number: str | None = None    # Card identifier (e.g., "1234", "FPND", "GRAB")
    amount: float | None = None       # Transaction amount as float
    merchant: str | None = None       # Merchant/restaurant name
```

### 3. Extraction Flow
1. Email subject is matched against registered patterns in `html_extractors` or `text_extractors`
2. Matching extractor method is called with parsed HTML (BeautifulSoup) or raw text
3. Method extracts data using regex patterns, HTML parsing, etc.
4. Returns `TransactionData` with extracted information

### 4. Registry System
Extractors are registered in `utils/extractors/__init__.py`:
```python
EXTRACTOR_REGISTRY = {
    "Foodpanda": FoodpandaEmailExtractor(),
    "Grab": GrabEmailExtractor(), 
    "Metrobank": MetrobankEmailExtractor(),
}
```

## Testing Extractors

### Quick Testing
Use the generic test tool to test any extractor with real emails:
```bash
# Test specific merchant (default: last 3 days)
uv run python test_extractor.py <Merchant>

# Test with custom date range
uv run python test_extractor.py <Merchant> <days_back>

# Examples
uv run python test_extractor.py Foodpanda
uv run python test_extractor.py Grab 7
```

### Unit Testing
Run pytest for automated tests:
```bash
# Test all extractors
uv run pytest utils/extractors/test_data/test_extractors.py -v

# Test specific extractor
uv run pytest utils/extractors/test_data/test_extractors.py::test_extractor -v
```

## Adding a New Extractor

### Step 1: Create Extractor Class
Create `utils/extractors/newmerchant.py`:

```python
import re
from bs4 import BeautifulSoup
from utils.extractors.base import BaseEmailExtractor, TransactionData

class NewMerchantEmailExtractor(BaseEmailExtractor):
    def __init__(self, merchant_email: str = "noreply@newmerchant.com"):
        super().__init__(merchant_email)
        self.register_extractors()

    def register_extractors(self) -> None:
        self.html_extractors = {
            "Transaction completed": self._extract_transaction_html,
            "Payment successful": self._extract_payment_html,
        }
        self.text_extractors = {
            "Transaction completed": self._extract_transaction_text,
        }

    def _extract_transaction_html(self, soup: BeautifulSoup, subject: str | None = None) -> TransactionData:
        try:
            # Extract amount using regex or BeautifulSoup
            amount_match = re.search(r'Total:\s*\$([0-9,.]+)', str(soup))
            amount = float(amount_match.group(1).replace(',', '')) if amount_match else None
            
            # Extract merchant name
            merchant_elem = soup.find('td', string=re.compile('Merchant:'))
            merchant = merchant_elem.find_next_sibling().get_text().strip() if merchant_elem else "NewMerchant"
            
            # Card number (often not available, use placeholder)
            card_number = "NMERCH"
            
            return TransactionData(card_number=card_number, amount=amount, merchant=merchant)
        except Exception as e:
            print(f"Error extracting NewMerchant transaction: {e}")
            return TransactionData()
```

### Step 2: Register in Registry
Add to `utils/extractors/__init__.py`:
```python
from .newmerchant import NewMerchantEmailExtractor

EXTRACTOR_REGISTRY = {
    "Foodpanda": FoodpandaEmailExtractor(),
    "Grab": GrabEmailExtractor(),
    "Metrobank": MetrobankEmailExtractor(),
    "NewMerchant": NewMerchantEmailExtractor(),  # Add this line
}
```

### Step 3: Add to Main Merchants List
Add to `main.py`:
```python
MERCHANTS = [
    "Grab",
    "Metrobank", 
    "Foodpanda",
    "NewMerchant",  # Add this line
]
```

### Step 4: Create Test Template
Create `utils/extractors/test_data/newmerchant_email_template.py`:
```python
NEWMERCHANT_TRANSACTION_EMAIL = {
    "from": "noreply@newmerchant.com",
    "subject": "Transaction completed",
    "date": "2023-01-01 12:00:00",
    "body": """
    Transaction Details:
    Merchant: Test Restaurant
    Total: $25.99
    Transaction ID: TXN123456
    """,
}

EXPECTED_RESULTS = {
    "card_number": "NMERCH",
    "amount": 25.99,
    "merchant": "Test Restaurant",
}

def get_test_data():
    return {"email": NEWMERCHANT_TRANSACTION_EMAIL, "expected": EXPECTED_RESULTS}
```

### Step 5: Register Test
Add to `utils/extractors/test_data/__init__.py`:
```python
available_tests = [
    "foodpanda_email_template",
    "newmerchant_email_template",  # Add this line
]
```

## Updating an Existing Extractor

### Common Update Scenarios

1. **New email format/subject**: Add new patterns to `register_extractors()`
2. **Different HTML structure**: Update regex patterns or BeautifulSoup selectors
3. **New merchant email address**: Update default email in `__init__()`
4. **Fix extraction bugs**: Debug using `test_extractor.py` first

### Debugging Process
1. **Test with real emails**: `uv run python test_extractor.py <Merchant> 7`
2. **Examine email content**: Check actual HTML/text structure
3. **Update extraction logic**: Modify regex patterns, HTML selectors
4. **Test again**: Verify fixes work with both old and new formats
5. **Run unit tests**: Ensure existing tests still pass

### Best Practices

#### Extraction Patterns
- Use **regex with DOTALL flag** for multiline matching: `re.search(pattern, text, re.DOTALL)`
- **Handle multiple formats**: Support both old and new email templates
- **Graceful degradation**: Return partial data if some fields fail
- **Use BeautifulSoup for HTML**: `soup.find()`, `soup.find_all(string=True)`

#### Error Handling
```python
try:
    # Extraction logic
    amount = extract_amount(soup)
    merchant = extract_merchant(soup)
    return TransactionData(card_number="MERCH", amount=amount, merchant=merchant)
except Exception as e:
    print(f"Error extracting {merchant_name} transaction: {e}")
    return TransactionData()  # Return empty data on failure
```

#### Subject Matching
```python
def register_extractors(self) -> None:
    # Handle variations in subjects
    self.html_extractors = {
        "Order confirmed": self._extract_order,
        "Order confirmed.": self._extract_order,  # With period
        "Your order is confirmed": self._extract_order,  # Alternate wording
    }
```

## Common Extraction Patterns

### Amount Extraction
```python
# Pattern 1: Simple currency prefix
amount_match = re.search(r'₱\s*([0-9,.]+)', text)

# Pattern 2: Total label followed by amount
total_match = re.search(r'Total:?\s*₱?\s*([0-9,.]+)', text, re.DOTALL)

# Pattern 3: Order Total on separate lines
order_total_match = re.search(r'Order\s+Total[\s\n]*₱[\s\n]*([0-9,.]+)', text, re.DOTALL)

if amount_match:
    amount = float(amount_match.group(1).replace(',', ''))
```

### Merchant Name Extraction
```python
# Pattern 1: "from [merchant]" pattern
merchant_match = re.search(r'from\s+(.+?)\s+(will|has)', text)

# Pattern 2: "order from [merchant]" pattern  
order_match = re.search(r'order from\s+(.+?)\s+has been', text)

# Pattern 3: BeautifulSoup table/label lookup
merchant_elem = soup.find('td', string=re.compile('Merchant'))
merchant = merchant_elem.find_next_sibling().get_text().strip()
```

## Environment Setup

Ensure your `.env` file has:
```
GMAIL_EMAIL=your-email@gmail.com
GMAIL_APP_PASSWORD=your-app-specific-password
GOOGLE_SHEET_CREDS_PATH=sheet-creds.json
GOOGLE_SHEET_ID=your-google-sheet-id
```

## Usage Instructions for LLM

When I ask you to:

1. **"Update [Merchant] extractor"**: 
   - Test current extractor with `test_extractor.py`
   - Debug failing extractions
   - Update extraction patterns in the extractor file
   - Verify both old and new formats work
   - Fix any deprecation warnings

2. **"Add [NewMerchant] extractor"**:
   - Follow the 5-step process above
   - Create extractor class with proper patterns
   - Register in registry and main merchants list  
   - Create test template with sample email
   - Test with real emails if available

3. **"Debug extraction issues"**:
   - Use `test_extractor.py` to identify failures
   - Examine actual email content/structure
   - Update regex patterns or HTML selectors
   - Test edge cases and format variations

Always test thoroughly and ensure backward compatibility with existing email formats.