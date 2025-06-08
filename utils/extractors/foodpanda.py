import re

from bs4 import BeautifulSoup

from utils.extractors.base import BaseEmailExtractor, TransactionData


class FoodpandaEmailExtractor(BaseEmailExtractor):
    def __init__(self, merchant_email: str = "info@mail.foodpanda.ph"):
        """
        Initialize the FoodPanda extractor with the merchant's email address.
        """
        super().__init__(merchant_email)
        self.register_extractors()

    def register_extractors(self) -> None:
        """
        Register specific extractors for FoodPanda emails.
        """
        # Register HTML extractors - only process order confirmation emails
        self.html_extractors = {
            "Your order has been placed": self._extract_order_confirmation_html,
        }

        # For text emails, we'll convert them to HTML and use the same extractor
        self.text_extractors = {
            "Your order has been placed": self._extract_from_text_wrapper,
        }

    def _extract_order_confirmation_html(
        self, soup: BeautifulSoup, subject: str | None = None
    ) -> TransactionData:
        """
        Extract transaction data from FoodPanda order confirmation emails.

        Args:
            soup: BeautifulSoup object of the HTML email
            subject: Email subject (should be "Your order has been placed")

        Returns:
            TransactionData with extracted information
        """
        # Verify subject
        if subject != "Your order has been placed":
            return TransactionData()

        try:
            # Extract total amount - first try to find it in the HTML structure
            amount = None

            # Look for the Order Total row in the table
            order_total_elements = soup.find_all(text=lambda t: "Order Total" in t)
            for element in order_total_elements:
                # Get the parent element and then find the amount
                parent = element.parent
                if parent:
                    # Try to find the amount in nearby elements
                    amount_text = parent.find_next(text=lambda t: "₱" in str(t))
                    if amount_text:
                        # Extract the numeric value
                        amount_match = re.search(r"₱\s*([0-9,.]+)", str(amount_text))
                        if amount_match:
                            # Convert to float, removing commas
                            amount = float(amount_match.group(1).replace(",", ""))
                            break

            # If not found in the structure, try searching the entire HTML
            if not amount:
                # Look for pattern like "Order Total ₱803.00"
                amount_match = re.search(r"Order\s+Total\s*₱\s*([0-9,.]+)", str(soup))
                if amount_match:
                    amount = float(amount_match.group(1).replace(",", ""))

            # Extract restaurant name (merchant)
            restaurant = None
            restaurant_text = soup.find(
                text=lambda t: "from" in str(t) and "will be on its way" in str(t)
            )
            if restaurant_text:
                restaurant_match = re.search(
                    r"from\s+(.+?)\s+will be on its way", str(restaurant_text)
                )
                if restaurant_match:
                    restaurant = restaurant_match.group(1)

            # If restaurant name not found, use FoodPanda as default
            if not restaurant:
                restaurant = "FoodPanda"

            # We don't have card number in FoodPanda emails typically
            # Using a placeholder format for consistency
            card_number = "FPND"  # FoodPanda doesn't provide card details

            return TransactionData(
                card_number=card_number, amount=amount, merchant=restaurant
            )

        except Exception as e:
            print(f"Error extracting FoodPanda transaction: {e}")
            return TransactionData()

    def _extract_from_text_wrapper(
        self, text: str, subject: str | None = None
    ) -> TransactionData:
        """
        Simple wrapper that converts text to HTML and uses the HTML extractor.
        """
        # Create a simple HTML structure from the text
        html = f"<html><body><div>{text}</div></body></html>"
        soup = BeautifulSoup(html, "html.parser")

        # Use the HTML extractor
        return self._extract_order_confirmation_html(soup, subject)
