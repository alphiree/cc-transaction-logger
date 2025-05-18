import os
from datetime import datetime, timedelta

import pandas as pd
from dotenv import load_dotenv

from utils import update_env_file
from utils.extractors import EmailTransactionExtract
from utils.gmail import Gmail
from utils.googlesheets import SheetManager

load_dotenv()

MERCHANTS = [
    # Accepted merchants can be found in utils/extractors/__init__.py
    "Grab",
    "Metrobank",
]


def main():
    gmail_client = Gmail(os.getenv("GMAIL_EMAIL"), os.getenv("GMAIL_APP_PASSWORD"))
    sheet_client = SheetManager(os.getenv("GOOGLE_SHEET_CREDS_PATH"))
    print("Hello from cc-transaction-logger-v2!")
    last_runtime = os.getenv("LAST_RUNTIME", None)
    if last_runtime:
        start_date = datetime.strptime(last_runtime, "%Y-%m-%d %H:%M:%S")
    else:
        start_date = datetime.now() - timedelta(days=7)
    end_date = datetime.now()

    dfs = []

    # Fetch and extract transactions from each merchant
    for merchant in MERCHANTS:
        print(f"Fetching and extracting from {merchant}...")
        extractor = EmailTransactionExtract(gmail_client=gmail_client)
        df = extractor.fetch_and_extract(
            merchant=merchant, date_interval=[start_date, end_date]
        )
        if df is not None:
            print(f"Extracted {len(df)} transactions from {merchant}")
            dfs.append(df)
        else:
            print(f"No transactions found for {merchant}")

    if dfs:
        df = pd.concat(dfs)

        # Upload transactions to Google Sheets
        print("Creating logger sheet...")
        worksheet = sheet_client.create_logger_sheet(
            spreadsheet_id=os.getenv("GOOGLE_SHEET_ID"),
            statement_day=int(os.getenv("STATEMENT_DAY")),
        )
        print("Uploading transactions to Google Sheets...")
        sheet_client.update_logger_sheet(
            worksheet=worksheet,
            df=df,
            end_date=end_date,
        )
        print("Done!")
    else:
        print("No transactions found, skipping upload to Google Sheets")

    # Update last runtime
    update_env_file("LAST_RUNTIME", end_date.strftime("%Y-%m-%d %H:%M:%S"))


if __name__ == "__main__":
    main()
