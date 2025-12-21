from utils.extractors.base import BaseEmailExtractor, TransactionData


class MetrobankEmailExtractor(BaseEmailExtractor):
    def __init__(
        self,
        start_str: str = "at",
        end_str: str = "for PHP",
        str_to_find: str = "ending in ",
        merchant_email: str = "Customerservice@metrobankcard.com",
    ) -> None:
        super().__init__(merchant_email)
        self.start_str = start_str
        self.end_str = end_str
        self.str_to_find = str_to_find
        self.register_extractors()
        self.merchant_category = None

    def register_extractors(self) -> None:
        """Register the specific extractors for Metrobank emails"""
        # HTML extractors - Metrobank typically doesn't use HTML emails
        self.html_extractors = {}

        # Text extractors
        self.text_extractors = {
            "Transaction Notification": self._extract_transaction_notification,
            "Metrobank Card Transaction Notification": self._extract_metrobank_card_transaction_notification,
            # Add more notification types here in the future
        }

    def _extract_transaction_notification(
        self, text: str, subject: str | None = None
    ) -> TransactionData:
        """Extract data from Transaction Notification emails from the standard transactions"""
        if subject != "Transaction Notification":
            return TransactionData()

        last_four_digits = None
        merchant = None
        total_paid_amount = None

        # Extract card number
        start_index = text.find(self.str_to_find)
        if start_index != -1:
            start_index += len(self.str_to_find)
            last_four_digits = text[start_index : start_index + 4]

        # Extract merchant
        start_index = text.find(self.start_str)
        end_index = text.find(self.end_str)
        if start_index != -1 and end_index != -1:
            start_index += len(self.start_str)
            merchant = text[start_index:end_index].strip()

        # Extract amount
        start_index = text.find(self.end_str)
        if start_index != -1:
            start_index += len(self.end_str)
            amount_text = text[start_index : start_index + 10]
            amount_digits = "".join(filter(lambda x: x.isdigit(), amount_text))
            if amount_digits:
                total_paid_amount = float(amount_digits) / 100

        if total_paid_amount:
            return TransactionData(
                card_number=last_four_digits,
                amount=total_paid_amount,
                merchant=merchant,
                category=self.merchant_category,
            )
        else:
            return TransactionData(
                card_number=last_four_digits,
                amount=0,
                merchant="Invalid",
                category=self.merchant_category,
            )

    def _extract_transaction_notification_for_appbills(
        self, text: str, subject: str | None = None
    ) -> TransactionData:
        """Extract data from Transaction Notification emails from the billing transactions"""
        return TransactionData()

    def _extract_metrobank_card_transaction_notification(
        self, text: str, subject: str | None = None
    ) -> TransactionData:
        """Extract data from Metrobank Card Transaction Notification emails (e.g., PayBills)"""
        if subject != "Metrobank Card Transaction Notification":
            return TransactionData()

        import re

        try:
            # Extract card number (last 4 digits)
            card_match = re.search(r"ending in (\d{4})", text)
            card_number = card_match.group(1) if card_match else None

            # Extract amount - look for "PHP 1699.00" pattern
            amount_match = re.search(r"PHP\s*([0-9,.]+)", text)
            amount = None
            if amount_match:
                amount_str = amount_match.group(1).replace(",", "").rstrip(".")
                amount = float(amount_str)

            # Extract merchant - look for PayBills transactions specifically
            merchant = None
            if "PayBills" in text or "paybills" in text.lower():
                merchant = "pay bills option"
            else:
                # Fallback: extract text between "for your" and "transaction"
                merchant_match = re.search(
                    r"for your\s+(.+?)\s+transaction", text, re.IGNORECASE
                )
                if merchant_match:
                    merchant_text = merchant_match.group(1).strip()
                    # If it contains PayBills, simplify to "pay bills option"
                    if "PayBills" in merchant_text:
                        merchant = "pay bills option"
                    else:
                        merchant = merchant_text

            return TransactionData(
                card_number=card_number,
                amount=amount,
                merchant=merchant,
                category="Housing & Utilities",
            )

        except Exception as e:
            print(f"Error extracting Metrobank Card transaction: {e}")
            return TransactionData()
