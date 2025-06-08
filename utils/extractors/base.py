from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Callable, Dict, Optional

from bs4 import BeautifulSoup


@dataclass
class TransactionData:
    card_number: Optional[str] = None
    amount: Optional[float] = None
    merchant: Optional[str] = None
    # You can easily add more fields here in the future
    # category: Optional[str] = None
    # timestamp: Optional[datetime] = None
    # location: Optional[str] = None

    def to_tuple(self):
        """Convert to tuple format for backward compatibility"""
        return (self.card_number, self.amount, self.merchant)


class BaseEmailExtractor(ABC):
    def __init__(self, merchant_email: str):
        self.merchant_email = merchant_email
        # Subclasses should override these dictionaries with their specific methods
        self.html_extractors: Dict[str, Callable] = {}
        self.text_extractors: Dict[str, Callable] = {}

    def extract_payment_info(
        self, content: str, subject: str | None = None
    ) -> TransactionData:
        """
        Main extraction method that detects content type and calls the appropriate extractor.

        Args:
            content: The email content (could be HTML or plain text)
            subject: The subject of the email
        Returns:
            TransactionData: Object containing transaction information
        """
        # Check if content is likely HTML
        if (
            "<html" in content.lower()
            or "<body" in content.lower()
            or "<div" in content.lower()
        ):
            # Parse HTML content
            soup = BeautifulSoup(content, "html.parser")
            return self.extract_from_html(soup, subject)
        else:
            # Process as plain text
            return self.extract_from_text(content, subject)

    def extract_from_html(
        self, soup: BeautifulSoup, subject: str | None = None
    ) -> TransactionData:
        """
        Extracts transaction details from HTML emails.
        Uses the html_extractors dictionary to try different extraction methods.

        Args:
            soup: BeautifulSoup object of the email HTML
            subject: The subject of the email
        Returns:
            TransactionData: Object containing transaction information
        """
        # First try if we have a specific extractor for this subject
        if subject and subject in self.html_extractors:
            result = self.html_extractors[subject](soup, subject)
            if result and result.card_number:
                return result

        # If not, try all registered extractors
        for extractor_name, extractor_method in self.html_extractors.items():
            result = extractor_method(soup, subject)
            if result and result.card_number:
                return result

        # If no extractor succeeds, return empty result
        return TransactionData()

    def extract_from_text(
        self, text: str, subject: str | None = None
    ) -> TransactionData:
        """
        Extracts transaction details from plain text emails.
        Uses the text_extractors dictionary to try different extraction methods.

        Args:
            text: The plain text content of the email
            subject: The subject of the email
        Returns:
            TransactionData: Object containing transaction information
        """
        # First try if we have a specific extractor for this subject
        if subject and subject in self.text_extractors:
            result = self.text_extractors[subject](text, subject)
            if result and result.card_number:
                return result

        # If not, try all registered extractors
        for extractor_name, extractor_method in self.text_extractors.items():
            result = extractor_method(text, subject)
            if result and result.card_number:
                return result

        # If no extractor succeeds, return empty result
        return TransactionData()

    @abstractmethod
    def register_extractors(self) -> None:
        """
        Register the specific extractors for this merchant.
        Subclasses should override this method to populate the html_extractors
        and text_extractors dictionaries with their specific extraction methods.
        """
        pass
