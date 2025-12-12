import re

from bs4 import BeautifulSoup

from utils.extractors.base import BaseEmailExtractor, TransactionData


class GreenGSMEmailExtractor(BaseEmailExtractor):
    """
    Extractor for 2C2P payment receipts for GREEN AND SMART MOBILITY PHILIPPINES INC.
    """

    def __init__(self, merchant_email: str = "noreply@2c2p.com"):
        super().__init__(merchant_email)
        self.register_extractors()

    def register_extractors(self) -> None:
        # The subject always starts with "RECEIPT FOR YOUR PAYMENT"
        self.html_extractors = {
            r"RECEIPT FOR YOUR PAYMENT": self._extract_payment_html,
        }

    def _extract_payment_html(
        self, soup: BeautifulSoup, subject: str | None = None
    ) -> TransactionData:
        try:
            text = soup.get_text(" ", strip=True)

            # --- Extract Amount ---
            amount_match = re.search(r"([0-9]+\.[0-9]{2})\s*PHP", text)
            amount = float(amount_match.group(1)) if amount_match else None

            # --- Extract Merchant ---
            merchant_match = re.search(
                r"payment of [0-9.]+\s*PHP to (.+?)\.", text, re.IGNORECASE
            )
            merchant = merchant_match.group(1).strip() if merchant_match else None

            # --- Extract Card Number ---
            card_match = re.search(
                r"Paid via:\s*(?:MasterCard|Visa|AMEX|JCB)\s+[0-9X]+([0-9]{4})",
                text,
                re.IGNORECASE,
            )
            card_number = card_match.group(1) if card_match else None

            return TransactionData(
                card_number=card_number,
                amount=amount,
                merchant=merchant,
            )

        except Exception as e:
            print(f"Error extracting GreenSmart transaction: {e}")
            return TransactionData()
