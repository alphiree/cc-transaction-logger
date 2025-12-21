from bs4 import BeautifulSoup

from utils.extractors.base import BaseEmailExtractor, TransactionData


class TemplateExtractor(BaseEmailExtractor):
    """
    Template extractor class to use as a reference when implementing new merchant extractors.

    Steps to create a new extractor:
    1. Copy this file and rename it to your merchant (e.g., amazon_extractor.py)
    2. Rename the class to match your merchant (e.g., AmazonExtractor)
    3. Update the merchant_email parameter in __init__
    4. Implement your specific extraction methods
    5. Register your extraction methods in register_extractors()
    6. Add your extractor to the EXTRACTOR_REGISTRY in __init__.py
    """

    def __init__(self, merchant_email: str = "example@merchant.com"):
        """
        Initialize the extractor with the merchant's email address.

        Args:
            merchant_email: The email address used by the merchant to send transaction emails
        """
        super().__init__(merchant_email)
        self.register_extractors()
        self.merchant_category = None

    def register_extractors(self) -> None:
        """
        Register specific extractors for this merchant.
        Map email types or subjects to specific extraction methods.
        """
        # Register HTML extractors - add methods for different email types
        self.html_extractors = {
            "OrderConfirmation": self._extract_order_confirmation_html,
            "ShippingNotification": self._extract_shipping_notification_html,
            # Add more HTML extractors as needed
        }

        # Register text extractors - add methods for different email types
        self.text_extractors = {
            "TransactionReceipt": self._extract_transaction_receipt_text,
            # Add more text extractors as needed
        }

    # --- HTML extraction methods ---

    def _extract_order_confirmation_html(
        self, soup: BeautifulSoup, subject: str | None = None
    ) -> TransactionData:
        """
        Extract transaction data from Order Confirmation HTML emails.

        Args:
            soup: BeautifulSoup object of the HTML email
            subject: Email subject (optional)

        Returns:
            TransactionData with extracted information
        """
        # TEMPLATE: Replace with your actual extraction logic

        # Example: Find card number element
        # card_element = soup.find("div", class_="card-info")
        # last_four_digits = card_element.text[-4:] if card_element else None

        # Example: Find amount element
        # amount_element = soup.find("span", class_="total-amount")
        # amount = float(amount_element.text.strip("$")) if amount_element else None

        # Example: Set merchant name
        # merchant = "Your Merchant Name" or extract from email

        # For template, just return empty TransactionData
        return TransactionData()

    def _extract_shipping_notification_html(
        self, soup: BeautifulSoup, subject: str | None = None
    ) -> TransactionData:
        """Extract transaction data from Shipping Notification HTML emails."""
        # Implement extraction logic for shipping notifications
        # This is just a template method
        return TransactionData()

    # --- Text extraction methods ---

    def _extract_transaction_receipt_text(
        self, text: str, subject: str | None = None
    ) -> TransactionData:
        """
        Extract transaction data from plain text transaction receipts.

        Args:
            text: Plain text email content
            subject: Email subject (optional)

        Returns:
            TransactionData with extracted information
        """
        # TEMPLATE: Replace with your actual extraction logic

        # Example: Extract card number
        # card_pattern = r"ending in (\d{4})"
        # card_match = re.search(card_pattern, text)
        # last_four_digits = card_match.group(1) if card_match else None

        # Example: Extract amount
        # amount_pattern = r"Total: \$(\d+\.\d{2})"
        # amount_match = re.search(amount_pattern, text)
        # amount = float(amount_match.group(1)) if amount_match else None

        # Example: Set merchant
        # merchant = "Your Merchant Name"

        # For template, just return empty TransactionData
        return TransactionData()
