# Credit Card Transaction Logger v2

![README Banner](banner.png)

A Python application that automatically logs credit card transactions by extracting data from notification emails and storing them in Google Sheets.

## Table of Contents

- [Description](#description)
- [Installation](#installation)
- [Usage](#usage)
- [Configuration](#configuration)
- [Architecture](#architecture)
- [Dependencies](#dependencies)
- [Development](#development)

## Description

This project automatically extracts credit card transaction information from emails sent by supported merchants/banks and logs them into a Google Sheet. It uses Gmail API to read emails and Google Sheets API to maintain a transaction log, making it easier to track and manage credit card expenses.

Currently supported merchants:

- Grab
- Metrobank

## Installation

1. Clone the repository:

   ```bash
   git clone https://github.com/alphiree/cc-transaction-logger.git
   cd cc-transaction-logger-v2
   ```

2. Install dependencies using `uv`:

   ```bash
   # Install uv if you don't have it
   pip install uv # or folllow the installation process here: https://docs.astral.sh/uv/getting-started/installation/
   ```

3. Set up Google Sheets API credentials:

   - Go to the [Google Cloud Console](https://console.cloud.google.com/)
   - Create a new project
   - Enable the Google Sheets API and Google Drive API
   - Create a service account and download the credentials as JSON
   - Save the credentials file as `sheet-creds.json` in the project root

4. Create a `.env` file with required environment variables (see [Configuration](#configuration))

## Usage

Run the application to fetch and log transactions:

```bash
uv run main.py
```

The script will:

1. Connect to Gmail using the provided credentials
2. Search for transaction emails from configured merchants
3. Extract transaction details (card number, amount, merchant)
4. Log the transactions to a Google Sheet
5. Update the last runtime in the `.env` file

## Configuration

Create a `.env` file with the following variables:

```
# Gmail credentials
GMAIL_EMAIL=your-email@gmail.com
GMAIL_APP_PASSWORD=your-app-specific-password

# Google Sheets configuration
GOOGLE_SHEET_CREDS_PATH=sheet-creds.json
GOOGLE_SHEET_ID=your-google-sheet-id
STATEMENT_DAY=9

# User configuration
PAYER_USERS=user_1,user_2,others

# Runtime tracking (will be updated automatically)
LAST_RUNTIME=YYYY-MM-DD HH:MM:SS
```

Notes:

- `GMAIL_APP_PASSWORD`: Create an app-specific password in your Google Account settings
- `GOOGLE_SHEET_ID`: The ID from your Google Sheet URL
- `STATEMENT_DAY`: The day of the month when your credit card statement is generated
- `PAYER_USERS`: Comma-separated list of possible payers for dropdown selection in the sheet

## Architecture

The project consists of the following main components:

- `main.py`: Entry point that orchestrates the email fetching and data extraction
- `utils/gmail.py`: Handles Gmail connection and email retrieval
- `utils/googlesheets.py`: Manages Google Sheets operations
- `utils/extractors/`: Contains merchant-specific email extractors:
  - `base.py`: Base extractor class
  - `grab.py`: Grab transaction email extractor
  - `metrobank.py`: Metrobank transaction email extractor

The workflow:

1. Connect to Gmail using IMAP
2. Fetch emails from specified merchants within a date range
3. Extract transaction data (card number, amount, merchant) using pattern matching
4. Format data into a pandas DataFrame
5. Create or update a Google Sheet with the transactions
6. Save the last runtime for incremental processing

## Dependencies

- beautifulsoup4: HTML parsing for email content
- gspread: Google Sheets API client
- gspread-formatting: Formatting Google Sheets
- pandas: Data manipulation
- python-dotenv: Environment variable management
- google-auth: Google authentication

## Development

To add support for a new merchant/bank:

1. Create a new extractor in `utils/extractors/` following the pattern in existing files
2. Implement the `extract_payment_info()` method to parse email content
3. Add the merchant name to the `MERCHANTS` list in `main.py`
4. Update the `extractors` dictionary in `utils/extractors/__init__.py`

Make sure to test thoroughly with sample emails to ensure accurate data extraction.
