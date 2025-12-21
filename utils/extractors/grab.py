from bs4 import BeautifulSoup

from utils.extractors.base import BaseEmailExtractor, TransactionData


class GrabEmailExtractor(BaseEmailExtractor):
    def __init__(self, merchant_email: str = "no-reply@grab.com"):
        super().__init__(merchant_email)
        self.register_extractors()
        self.merchant_category = None  # hardcoded on functions

    def register_extractors(self) -> None:
        """Register the specific extractors for Grab emails"""
        # HTML extractors
        self.html_extractors = {
            "GrabFood": self._extract_grabfood,
            "GrabRide": self._extract_grabride,
            # Add more extractors as needed
        }

        # Currently no text extractors for Grab
        self.text_extractors = {}

    def _extract_grabfood(
        self, soup: BeautifulSoup, subject: str | None = None
    ) -> TransactionData:
        """Extract transaction data from GrabFood emails"""
        span = soup.find("span", style="font-weight:bold; color:#000000;")
        if not span:
            return TransactionData()

        card_details = span.get_text(strip=True)
        card_parts = card_details.split()  # Split text by spaces
        last_four_digits = card_parts[-1]  # Last part is the last 4 digits

        total_paid_next_tag = None
        total_paid_span = soup.find(
            "span", text=lambda t: t and "TOTAL (INCL. TAX)" in t
        )
        if total_paid_span:
            total_paid_next_tag = total_paid_span.find_parent("td").find_next_sibling(
                "td"
            )

        if not total_paid_next_tag:
            return TransactionData()

        total_paid_amount = float(
            "".join(filter(lambda x: x.isdigit() or x == ".", total_paid_next_tag.text))
        )

        return TransactionData(
            card_number=last_four_digits,
            amount=total_paid_amount,
            merchant="GrabFood",
            category="Food & Dining",
        )

    def _extract_grabride(
        self, soup: BeautifulSoup, subject: str | None = None
    ) -> TransactionData:
        """Extract transaction data from GrabRide emails"""
        img_tag = soup.find("img", alt="MasterCard")
        if not img_tag:
            return TransactionData()

        # Find the parent <td> containing the image
        img_td = img_tag.find_parent("td")
        next_td = img_td.find_next_sibling("td")
        last_four_digits = next_td.text.strip()

        total_paid_element = soup.find("td", string="Total Paid")
        if not total_paid_element:
            return TransactionData()

        total_paid_next_tag = total_paid_element.find_next_sibling("td")
        total_paid_amount = float(
            "".join(filter(lambda x: x.isdigit() or x == ".", total_paid_next_tag.text))
        )

        return TransactionData(
            card_number=last_four_digits,
            amount=total_paid_amount,
            merchant="GrabRide",
            category="Transportation",
        )
