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

    def register_extractors(self) -> None:
        """Register the specific extractors for Metrobank emails"""
        # HTML extractors - Metrobank typically doesn't use HTML emails
        self.html_extractors = {}

        # Text extractors
        self.text_extractors = {
            "Transaction Notification": self._extract_transaction_notification,
            # Add more notification types here in the future
        }

    def _extract_transaction_notification(
        self, text: str, subject: str | None = None
    ) -> TransactionData:
        """Extract data from Transaction Notification emails"""
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

        return TransactionData(
            card_number=last_four_digits, amount=total_paid_amount, merchant=merchant
        )
