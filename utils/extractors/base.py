from abc import ABC, abstractmethod


class BaseEmailExtractor(ABC):
    def __init__(self, merchant_email: str):
        self.merchant_email = merchant_email

    @abstractmethod
    def extract_payment_info(
        self, text: str, subject: str | None = None
    ) -> tuple[str | None, float | None, str | None]:
        """
        Extracts transaction details from the merchant's email HTML.

        Args:
            text: The whole email text or an HTML text
            subject: The subject of the email
        Returns:
            tuple: (last_four_digits: str, total_paid_amount: float, merchant: str)
        """
        pass
