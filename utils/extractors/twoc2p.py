import re

from bs4 import BeautifulSoup

from utils.extractors.base import BaseEmailExtractor, TransactionData


class Generic2C2PEmailExtractor(BaseEmailExtractor):
    """
    Extractor for generic 2C2P payment receipts.
    Handles any payment made through 2C2P payment gateway.
    """

    def __init__(self, merchant_email: str = "noreply@2c2p.com"):
        super().__init__(merchant_email)
        self.register_extractors()
        self.merchant_category = None

    def register_extractors(self) -> None:
        self.html_extractors = {
            "RECEIPT FOR YOUR PAYMENT": self._extract_payment_html,
        }

    def _extract_payment_html(
        self, soup: BeautifulSoup, subject: str | None = None
    ) -> TransactionData:
        try:
            text = soup.get_text(" ", strip=True)

            amount_match = re.search(r"([0-9,]+\.[0-9]{2})\s*PHP", text)
            amount_str = (
                amount_match.group(1).replace(",", "") if amount_match else None
            )
            amount = float(amount_str) if amount_str else None

            if subject:
                merchant_match = re.search(r"RECEIPT FOR YOUR PAYMENT TO (.+)", subject)
                merchant = merchant_match.group(1).strip() if merchant_match else None
            else:
                merchant = None

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
                category=self.merchant_category,
            )

        except Exception as e:
            print(f"Error extracting 2C2P transaction: {e}")
            return TransactionData()
