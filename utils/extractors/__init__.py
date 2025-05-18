from datetime import datetime

import pandas as pd

from utils.gmail import Gmail

from .grab import GrabEmailExtractor
from .metrobank import MetrobankEmailExtractor


class EmailTransactionExtract:
    def __init__(self, gmail_client: Gmail):
        self.gmail_client = gmail_client
        self.extractors = {
            "Grab": GrabEmailExtractor(),
            "Metrobank": MetrobankEmailExtractor(),
        }

    def extract(self, merchant: str, text: str):
        extractor = self.extractors.get(merchant)
        if not extractor:
            raise ValueError(f"No extractor for merchant: {merchant}")
        return extractor.extract_payment_info(text)

    def fetch_and_extract(
        self,
        merchant: str,
        date_interval: list[datetime] | None = None,
        limit: int = 10,
    ) -> pd.DataFrame | None:
        """
        Fetch emails for a merchant and extract payment information

        Args:
            merchant (str): Name of the merchant (e.g., "Grab", "Metrobank")
            date_interval: Optional date interval for filtering emails
            limit (int): Maximum number of emails to fetch
        """
        extractor = self.extractors.get(merchant)
        if not extractor:
            raise ValueError(f"No extractor for merchant: {merchant}")

        # Use the extractor's merchant_email to filter emails
        emails = self.gmail_client.read_emails_filtered(
            sender=extractor.merchant_email,
            date_interval=date_interval,
            limit=limit,
        )

        if emails:
            df = pd.DataFrame(emails)
            df = df.assign(
                **dict(
                    zip(
                        ["card_number", "total_paid_amount", "merchant"],
                        zip(
                            *df.apply(
                                lambda x: extractor.extract_payment_info(
                                    x["body"], x["subject"]
                                ),
                                axis=1,
                            )
                        ),
                    )
                ),
            )
            return df
        return None
