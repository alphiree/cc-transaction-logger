from bs4 import BeautifulSoup

from utils.extractors.base import BaseEmailExtractor


class GrabEmailExtractor(BaseEmailExtractor):
    def __init__(self, merchant_email: str = "no-reply@grab.com"):
        super().__init__(merchant_email)

    def extract_payment_info(
        self, html: str, subject: str | None = None
    ) -> tuple[str | None, float | None, str | None]:
        soup = BeautifulSoup(html, "html.parser")

        ## GrabFood
        span = soup.find("span", style="font-weight:bold; color:#000000;")
        if span:
            card_details = span.get_text(strip=True)
            card_parts = card_details.split()  # Split text by spaces
            last_four_digits = card_parts[-1]  # Last part is the last 4 digits
            total_paid_next_tag = (
                soup.find("span", text=lambda t: t and "TOTAL (INCL. TAX)" in t)
                .find_parent("td")
                .find_next_sibling("td")
            )
            total_paid_amount = float(
                "".join(
                    filter(lambda x: x.isdigit() or x == ".", total_paid_next_tag.text)
                )
            )
            merchant = "GrabFood"
            return last_four_digits, total_paid_amount, merchant

        ## GrabRide
        img_tag = soup.find("img", alt="MasterCard")
        if img_tag:
            # Find the parent <td> containing the image
            img_td = img_tag.find_parent("td")
            next_td = img_td.find_next_sibling("td")
            last_four_digits = next_td.text.strip()
            total_paid_next_tag = soup.find(
                "td", string="Total Paid"
            ).find_next_sibling("td")
            total_paid_amount = float(
                "".join(
                    filter(lambda x: x.isdigit() or x == ".", total_paid_next_tag.text)
                )
            )
            merchant = "GrabRide"
            return last_four_digits, total_paid_amount, merchant

        return None, None, None
