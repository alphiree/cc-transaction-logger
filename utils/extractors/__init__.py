import pandas as pd

from utils.extractors.base import TransactionData

from .foodpanda import FoodpandaEmailExtractor
from .grab import GrabEmailExtractor
from .greengsm import GreenGSMEmailExtractor
from .metrobank import MetrobankEmailExtractor

# Registry of available extractors
# To add a new extractor:
# 1. Create a new extractor class (see _template_extractor.py for reference)
# 2. Import it here
# 3. Add it to this registry
EXTRACTOR_REGISTRY = {
    "Grab": GrabEmailExtractor(),
    "Metrobank": MetrobankEmailExtractor(),
    "Foodpanda": FoodpandaEmailExtractor(),
    "GreenGSM": GreenGSMEmailExtractor(),
    # "YourNewMerchant": YourNewMerchantExtractor(),
}


def get_extractor_for_merchant(merchant: str):
    """Get the appropriate extractor for a merchant"""
    extractor = EXTRACTOR_REGISTRY.get(merchant)
    if not extractor:
        raise ValueError(f"No extractor for merchant: {merchant}")
    return extractor


class TransactionExtractor:
    """
    Pure transaction extraction class that handles only the extraction logic
    without any email fetching functionality.
    """

    def __init__(self):
        self.extractors = EXTRACTOR_REGISTRY

    def extract_from_email(
        self, merchant: str, email_body: str, email_subject: str | None = None
    ) -> TransactionData:
        """Extract transaction information from a single email content"""
        extractor = self.extractors.get(merchant)
        if not extractor:
            raise ValueError(f"No extractor for merchant: {merchant}")
        return extractor.extract_payment_info(email_body, email_subject)

    def process_email_data(
        self, merchant: str, emails_data: list[dict]
    ) -> pd.DataFrame | None:
        """
        Process a list of email data and extract transactions

        Args:
            merchant (str): The merchant name for selecting the right extractor
            emails_data (list[dict]): List of dictionaries containing email data
                                     with 'body', 'subject', 'date' keys

        Returns:
            pd.DataFrame | None: DataFrame with extracted transactions or None if no valid transactions
        """
        if not emails_data:
            return None

        # Create a list to store transaction data
        transaction_data_list = []

        # Process each email
        for email_data in emails_data:
            # Extract transaction data from the email content
            transaction_data = self.extract_from_email(
                merchant=merchant,
                email_body=email_data["body"],
                email_subject=email_data.get("subject"),
            )

            # Only add valid transaction data
            if transaction_data.card_number:
                # Convert TransactionData to dict for DataFrame
                transaction_dict = {
                    "date": email_data["date"],
                    "subject": email_data.get("subject", ""),
                    "card_number": transaction_data.card_number,
                    "total_paid_amount": transaction_data.amount,
                    "merchant": transaction_data.merchant,
                }
                transaction_data_list.append(transaction_dict)

        # Create DataFrame from the list of transaction data
        if transaction_data_list:
            return pd.DataFrame(transaction_data_list)

        return None
