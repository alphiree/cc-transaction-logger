import os
from datetime import datetime, timedelta

import pandas as pd
from dotenv import load_dotenv

from cards import CreditCardName
from utils import update_env_file
from utils.extractors import TransactionExtractor, get_extractor_for_merchant
from utils.gmail import Gmail
from utils.googlesheets import SheetManager

load_dotenv()

cc_init = CreditCardName()


def main():
    gmail_client = Gmail(os.getenv("GMAIL_EMAIL"), os.getenv("GMAIL_APP_PASSWORD"))
    sheet_client = SheetManager(os.getenv("GOOGLE_SHEET_CREDS_PATH"))

    transaction_extractor = TransactionExtractor()

    print("Hello from cc-transaction-logger-v2!")
    print(f"Running extractor for {cc_init.NICKNAME}")

    # Determine time range for fetching emails
    last_runtime = os.getenv(cc_init.LAST_RUN_TIME_ENV_NAME, None)
    if last_runtime:
        start_date = datetime.strptime(last_runtime, "%Y-%m-%d %H:%M:%S")
    else:
        start_date = datetime.now() - timedelta(days=7)
    end_date = datetime.now()
    date_interval = [start_date, end_date]

    dfs = []

    # Process each merchant
    for merchant in cc_init.MERCHANTS:
        print(f"Fetching emails from {merchant}...")

        # Get the extractor to determine the merchant's email address
        extractor = get_extractor_for_merchant(merchant)

        # Step 1: Fetch emails directly using the Gmail client
        emails = gmail_client.read_emails_filtered(
            sender=extractor.merchant_email, date_interval=date_interval, limit=10
        )

        if emails:
            print(f"Found {len(emails)} emails for {merchant}")

            # Step 2: Process the emails to extract transaction data
            df = transaction_extractor.process_email_data(
                merchant=merchant, emails_data=emails
            )

            if df is not None:
                print(f"Extracted {len(df)} transactions from {merchant}")
                dfs.append(df)
            else:
                print(f"No valid transactions found in {merchant} emails")
        else:
            print(f"No emails found for {merchant}")

    # Process extracted transactions
    if dfs:
        df = pd.concat(dfs)
        df = df.sort_values(by="date", ascending=True)
        df = df[df["card_number"].astype(str) == cc_init.LAST_DIGITS]
        print(df)

        # Upload transactions to Google Sheets
        print("Creating logger sheet...")
        worksheet = sheet_client.create_logger_sheet(
            spreadsheet_id=cc_init.GOOGLE_SHEET_ID,
            statement_day=int(cc_init.STATEMENT_DATE),
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
    update_env_file(
        cc_init.LAST_RUN_TIME_ENV_NAME, end_date.strftime("%Y-%m-%d %H:%M:%S")
    )


if __name__ == "__main__":
    main()
