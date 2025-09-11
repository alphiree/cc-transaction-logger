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
        # Handle both with and without period in subject
        self.html_extractors = {
            "Your order has been placed": self._extract_order_confirmation_html,
            "Your order has been placed.": self._extract_order_confirmation_html,
        }

        # For text emails, we'll convert them to HTML and use the same extractor
        self.text_extractors = {
            "Your order has been placed": self._extract_from_text_wrapper,
            "Your order has been placed.": self._extract_from_text_wrapper,
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
        # Verify subject (handle both with and without period)
        if subject not in ["Your order has been placed", "Your order has been placed."]:
            return TransactionData()

        try:
            # Extract total amount - first try to find it in the HTML structure
            amount = None

            # IMPROVED: Be more specific about finding the Order Total (not Subtotal)
            # Look specifically for "Order Total" followed by a price
            order_total_text = None
            for text in soup.find_all(string=True):
                if "Order Total" in text:
                    order_total_text = text
                    break

            if order_total_text:
                # Get the parent element
                parent = order_total_text.parent
                if parent:
                    # Look for the next element with price information
                    price_regex = re.compile(r"₱\s*([0-9,.]+)")

                    # Search in the next few siblings or nearby elements
                    next_elements = []
                    next_sibling = parent.next_sibling
                    for _ in range(5):  # Check next 5 elements
                        if next_sibling:
                            next_elements.append(next_sibling)
                            next_sibling = next_sibling.next_sibling

                    # Search for price in next elements
                    for elem in next_elements:
                        price_match = price_regex.search(str(elem))
                        if price_match:
                            amount = float(price_match.group(1).replace(",", ""))
                            break

            # If still not found, try a broader search in the entire email
            if not amount:
                # Look for "Order Total" followed by price in the same line or nearby
                # Handle new format where they might be on separate lines
                matches = re.findall(
                    r"Order\s+Total\s*[\s\n]*₱\s*([0-9,.]+)", str(soup), re.DOTALL
                )
                if matches:
                    # Use the last match if multiple are found (usually the correct one)
                    amount = float(matches[-1].replace(",", ""))
                else:
                    # Try alternate pattern where Order Total and amount are on separate lines
                    # Look for "Order Total" followed by "₱" and then the amount
                    order_total_pattern = re.search(
                        r"Order\s+Total[\s\n]*₱[\s\n]*([0-9,.]+)", str(soup), re.DOTALL
                    )
                    if order_total_pattern:
                        amount = float(order_total_pattern.group(1).replace(",", ""))

            # Extract restaurant name (merchant)
            restaurant = None
            
            # Try the original pattern first
            restaurant_text = soup.find(
                string=lambda t: t and "from" in str(t) and "will be on its way" in str(t)
            )
            if restaurant_text:
                restaurant_match = re.search(
                    r"from\s+(.+?)\s+will be on its way", str(restaurant_text)
                )
                if restaurant_match:
                    restaurant = restaurant_match.group(1)
            
            # If not found, try new pattern: "Your order from [Restaurant] has been placed"
            if not restaurant:
                restaurant_pattern = re.search(
                    r"Your order from\s+(.+?)\s+has been placed", str(soup), re.DOTALL
                )
                if restaurant_pattern:
                    restaurant = restaurant_pattern.group(1).strip()

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
